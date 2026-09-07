"""Schema DDL and one-time legacy-data backfills, run once at startup by
__init__.py's init_db(). Pure functions of a cursor - no pool access, no
transaction handling here, the caller (init_db) owns the connection."""


def create_tables(cur) -> None:
    # user_state holds the session/flow fields (see _ACCOUNT_KEYS split
    # in session.py's _save) — actively read/written on every request, not legacy.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_state (
            user_id BIGINT PRIMARY KEY,
            data JSONB NOT NULL,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id     BIGINT PRIMARY KEY,
            username        TEXT,
            name            TEXT,
            language        TEXT,
            source          TEXT DEFAULT 'organic',
            checks_used     INT  NOT NULL DEFAULT 0,
            quota_override  INT,
            joined_waitlist BOOLEAN NOT NULL DEFAULT FALSE,
            waitlist_at     TIMESTAMPTZ,
            first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
            last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS name TEXT")
    # Daily proactive vacancy alerts: a saved title+location per user
    # (edited in the Mini App's Profile > Vacancy Alerts screen) plus
    # an explicit opt-in flag, defaulting FALSE - setting the search
    # criteria alone should not silently start sending daily
    # messages, unsolicited pushes are exactly what gets a bot muted.
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS saved_job_title TEXT")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS saved_location TEXT")
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS vacancy_alerts_enabled BOOLEAN NOT NULL DEFAULT FALSE")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id          BIGSERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL,
            event_type  TEXT   NOT NULL,
            metadata    JSONB,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_type_time ON events (event_type, created_at)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_events_user ON events (telegram_id)")
    # One row per tracked application. cv_snapshot/match_score/matched_keywords/
    # missing_keywords capture which CV version was used and how it scored
    # against this vacancy at the moment of applying - the exact link a
    # spreadsheet can't give you (see backlog doc §5, Application Tracking).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id                 BIGSERIAL PRIMARY KEY,
            telegram_id        BIGINT NOT NULL REFERENCES users(telegram_id),
            vacancy_title      TEXT NOT NULL,
            vacancy_company    TEXT NOT NULL,
            vacancy_location   TEXT,
            vacancy_url        TEXT,
            vacancy_summary    TEXT,
            cv_snapshot        TEXT,
            match_score        INT,
            matched_keywords   JSONB,
            missing_keywords   JSONB,
            status             TEXT NOT NULL DEFAULT 'applied',
            recruiter_contacted BOOLEAN NOT NULL DEFAULT FALSE,
            notes              TEXT,
            source             TEXT,
            created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_applications_telegram_id ON applications (telegram_id)")
    # Replaces the hand-maintained COMPANIES list that used to be
    # hardcoded (and duplicated between bot/ and webapp/, until the
    # bot/ copy was deleted as dead code) in greenhouse_source.py.
    # Edit webapp/greenhouse_companies.csv
    # and run webapp/scripts/sync_greenhouse_companies.py to add/
    # remove/rename a verified company - no deploy needed, takes
    # effect within webapp/db.py's cache TTL. Never delete a row on
    # removal, only deactivate - keeps history of what was tried.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS greenhouse_companies (
            slug         TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            domain       TEXT,
            active       BOOLEAN NOT NULL DEFAULT TRUE,
            created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    # Multiple saved CVs per user (the "My CVs" page), replacing the
    # single user_state.data->>'cv_text' field. Exactly one row per
    # user may have is_active=true at a time - that's the CV every
    # other feature (analysis, vacancy scoring, applications) reads
    # via webapp/db.py's get_active_cv_text(), so uploading a new CV
    # or switching the active one needs no changes anywhere else.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cvs (
            id                 BIGSERIAL PRIMARY KEY,
            telegram_id        BIGINT NOT NULL REFERENCES users(telegram_id),
            label              TEXT NOT NULL,
            cv_text            TEXT NOT NULL,
            is_active          BOOLEAN NOT NULL DEFAULT FALSE,
            extracted_position TEXT,
            created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    cur.execute("ALTER TABLE cvs ADD COLUMN IF NOT EXISTS extracted_position TEXT")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cvs_telegram_id ON cvs (telegram_id)")
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_cvs_one_active_per_user
        ON cvs (telegram_id) WHERE is_active
    """)
    # "My Checks" - analysis history. One row per completed
    # /api/cv-jd-analysis call (written immediately, before the user
    # even starts the roadmap, since the analysis itself is already
    # worth keeping); roadmap_items fills in as each roadmap step
    # completes, keyed by item number as a JSON string key
    # (e.g. {"1": {"title": "CV Fixes", "fixes": [...]}}). Without
    # this, closing the Mini App loses every past analysis for good -
    # unlike the old chat flow, where Telegram's own message history
    # let a user scroll back and re-read a result anytime.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cv_analyses (
            id             BIGSERIAL PRIMARY KEY,
            telegram_id    BIGINT NOT NULL REFERENCES users(telegram_id),
            jd_text        TEXT NOT NULL,
            ats            JSONB NOT NULL,
            xyz            JSONB NOT NULL,
            tools          JSONB NOT NULL,
            level          JSONB NOT NULL,
            roadmap_items  JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cv_analyses_telegram_id ON cv_analyses (telegram_id)")
    # Dedup for daily vacancy alerts: one row per (user, vacancy) the
    # daily job has already sent, so the next run only alerts on
    # genuinely new postings instead of re-sending the same ones
    # every day. Keyed on the posting's URL (stable/unique per
    # Greenhouse job), not title+company (postings get retitled).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerted_vacancies (
            id          BIGSERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL REFERENCES users(telegram_id),
            vacancy_url TEXT NOT NULL,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            UNIQUE (telegram_id, vacancy_url)
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_alerted_vacancies_telegram_id ON alerted_vacancies (telegram_id)")


def migrate_legacy_state(cur) -> None:
    """Backfill users from the legacy user_state table. Safe to run on every
    startup: ON CONFLICT DO NOTHING means an already-migrated user (one with
    a `users` row) is left untouched, so this is a no-op once every
    pre-existing user has been copied over exactly once."""
    cur.execute("""
        INSERT INTO users (telegram_id, language, checks_used, joined_waitlist, first_seen_at, last_seen_at)
        SELECT
            user_id,
            NULLIF(data->>'lang', ''),
            COALESCE((data->>'usage_count')::int, 0),
            COALESCE((data->>'waitlisted')::boolean, false),
            updated_at,
            updated_at
        FROM user_state
        ON CONFLICT (telegram_id) DO NOTHING
    """)


def migrate_legacy_cv_text(cur) -> None:
    """Backfill `cvs` from the legacy single-CV field (user_state's
    data->>'cv_text') for anyone who uploaded a CV before the multi-CV
    `cvs` table existed. Safe on every startup: only inserts for
    telegram_ids with a non-empty legacy cv_text and no `cvs` row yet,
    so it's a no-op once every pre-existing user has been copied over."""
    cur.execute("""
        INSERT INTO cvs (telegram_id, label, cv_text, is_active)
        SELECT user_id, 'My CV', data->>'cv_text', true
        FROM user_state
        WHERE data->>'cv_text' IS NOT NULL AND data->>'cv_text' != ''
          AND user_id NOT IN (SELECT telegram_id FROM cvs)
    """)
