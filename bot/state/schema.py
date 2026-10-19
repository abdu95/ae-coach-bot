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
    # Lets the Mini App show the exact vacancies from one digest when a
    # user taps the alert message's button, instead of dropping them on
    # the home screen with no link back to what the message was about
    # (real user feedback). batch_id groups every row a single
    # run_vacancy_alerts() digest inserted; searched_job_title/
    # searched_location snapshot the search criteria at send time, since
    # a user's saved search can change before they tap an older message.
    cur.execute("ALTER TABLE alerted_vacancies ADD COLUMN IF NOT EXISTS batch_id TEXT")
    cur.execute("ALTER TABLE alerted_vacancies ADD COLUMN IF NOT EXISTS vacancy_title TEXT")
    cur.execute("ALTER TABLE alerted_vacancies ADD COLUMN IF NOT EXISTS vacancy_company TEXT")
    cur.execute("ALTER TABLE alerted_vacancies ADD COLUMN IF NOT EXISTS vacancy_location TEXT")
    cur.execute("ALTER TABLE alerted_vacancies ADD COLUMN IF NOT EXISTS vacancy_summary TEXT")
    cur.execute("ALTER TABLE alerted_vacancies ADD COLUMN IF NOT EXISTS searched_job_title TEXT")
    cur.execute("ALTER TABLE alerted_vacancies ADD COLUMN IF NOT EXISTS searched_location TEXT")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_alerted_vacancies_batch ON alerted_vacancies (batch_id)")
    # Payme checkout. These two tables were first created by hand in prod
    # and only ever INSERTed into by code (state/payments.py, the webapp's
    # app/db/payments.py, payme-webhook's main.py), so a fresh database
    # had neither. Declared here (2026-10-19) to exactly match prod's live
    # DDL, which makes this a no-op there and gives scratch/staging DBs
    # the same schema. amount is in tiyin (1 UZS = 100 tiyin).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id          BIGSERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL,
            amount      BIGINT NOT NULL,
            package     TEXT   NOT NULL DEFAULT '10_checks',
            state       TEXT   NOT NULL DEFAULT 'pending',
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    # One row per Payme transaction (payme_id is Payme's own id). state
    # and the *_time columns are Payme's protocol values (ms epoch), kept
    # as-is so CheckTransaction/GetStatement can echo them back verbatim.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payme_transactions (
            id           BIGSERIAL PRIMARY KEY,
            payme_id     TEXT    NOT NULL UNIQUE,
            order_id     BIGINT  NOT NULL REFERENCES orders(id),
            amount       BIGINT  NOT NULL,
            state        INTEGER NOT NULL DEFAULT 1,
            create_time  BIGINT  NOT NULL DEFAULT 0,
            perform_time BIGINT  NOT NULL DEFAULT 0,
            cancel_time  BIGINT  NOT NULL DEFAULT 0,
            reason       INTEGER,
            created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)


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


# Every table holding per-user rows. Each gets a user_id pointing at the
# new internal users.id (web-launch plan, Phase 1).
USER_CHILD_TABLES = ("cvs", "applications", "cv_analyses", "alerted_vacancies", "events", "orders")


def migrate_internal_user_id(cur) -> None:
    """Phase 1 step 1.2 ("expand") of the web-launch plan: give every user an
    internal id, independent of Telegram, so browser users (no telegram_id)
    can exist later. Purely additive - telegram_id stays the primary key and
    every existing query, in all three services, keeps working unchanged.

    - users.id: BIGSERIAL, so Postgres numbers existing rows and every new
      INSERT INTO users (telegram_id) gets one automatically.
    - <child>.user_id on every per-user table, backfilled from telegram_id.
    - A BEFORE INSERT/UPDATE trigger fills user_id from telegram_id, so code
      that only writes telegram_id (all of it, today) keeps every row linked.

    events and orders have no foreign key, so they can reference a
    telegram_id with no users row (prod had one: a 2026-08 Payme test
    order). Those get a bare users row tagged source='backfill_orphan',
    so every row can be linked and stats can exclude them.

    Safe on every startup: each statement is IF NOT EXISTS / OR REPLACE /
    only touches rows still missing a user_id."""
    cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS id BIGSERIAL")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_id_key ON users (id)")
    for table in ("events", "orders"):
        cur.execute(f"""
            INSERT INTO users (telegram_id, source)
            SELECT DISTINCT t.telegram_id, 'backfill_orphan' FROM {table} t
            WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.telegram_id = t.telegram_id)
            ON CONFLICT (telegram_id) DO NOTHING
        """)
    cur.execute("""
        CREATE OR REPLACE FUNCTION fill_user_id_from_telegram_id() RETURNS trigger AS $$
        BEGIN
            IF NEW.user_id IS NULL AND NEW.telegram_id IS NOT NULL THEN
                SELECT id INTO NEW.user_id FROM users WHERE telegram_id = NEW.telegram_id;
            END IF;
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql
    """)
    for table in USER_CHILD_TABLES:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS user_id BIGINT")
        cur.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_user_id ON {table} (user_id)")
        cur.execute(f"""
            UPDATE {table} t SET user_id = u.id FROM users u
            WHERE u.telegram_id = t.telegram_id AND t.user_id IS NULL
        """)
        cur.execute(f"""
            CREATE OR REPLACE TRIGGER trg_{table}_fill_user_id
            BEFORE INSERT OR UPDATE OF telegram_id ON {table}
            FOR EACH ROW EXECUTE FUNCTION fill_user_id_from_telegram_id()
        """)
