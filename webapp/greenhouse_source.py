"""
Vacancy search backed by Greenhouse's public per-company job board API
(boards-api.greenhouse.io) instead of Claude's web-search tool. Every
returned link points at a posting Greenhouse itself currently serves, so
it can't go stale/dead the way an LLM-found link occasionally did.

The company list (128 companies across 22 domains as of 2026-09-06,
each individually confirmed live via a real API call before being
added - not guessed from memory, and not assumed just because a
company is well-known or Fortune-500-scale) now lives in the
`greenhouse_companies` DB table (see db.get_active_companies()),
not hardcoded here - edit webapp/scripts/greenhouse_companies.csv and run
scripts/sync_greenhouse_companies.py to change it, no deploy needed.
That verification step matters: most old-economy enterprises (banks,
retailers, industrials) run on Workday/SAP SuccessFactors/Oracle/
iCIMS, not Greenhouse - Greenhouse skews toward VC-backed tech (per
landbase.com's 2026 count, ~11.5k companies on Greenhouse, plurality
"Software Development", median company size 51-200 employees). So
"find 100 Fortune 500s on Greenhouse" isn't a realistic bar for most
domains; the list reflects real, verified coverage rather than a
target headcount.

Scaling further (hundreds/thousands more companies) is real ingestion
infrastructure (deduping, refresh jobs, maybe scraping other job
boards' company lists the way RealtimeJobsBot did - see the backlog
doc) - a good follow-up now that the approach itself is proven, not
done here.

Known simplifications: `industry` is accepted for interface
compatibility but not filtered on (no per-company industry tags yet).
`work_setup` only meaningfully filters "remote" (checked against the
posting's location string) - Greenhouse's job-list endpoint doesn't
reliably expose hybrid/onsite as structured data.
"""

import asyncio
import html
import re

import httpx

import db  # local to this folder


def _strip_html(text: str) -> str:
    # Greenhouse's `content` field comes HTML-entity-escaped (e.g. "&lt;div&gt;"),
    # so unescape BEFORE stripping tags - the other order leaves tags intact.
    # Some entities are double-escaped ("&amp;amp;") - unescape twice, which
    # is a safe no-op on already-clean text.
    text = html.unescape(html.unescape(text or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


async def _fetch_company_jobs(client: httpx.AsyncClient, slug: str) -> list:
    try:
        resp = await client.get(
            f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
            params={"content": "true"},
        )
        if resp.status_code != 200:
            return []
        return resp.json().get("jobs", [])
    except Exception:
        return []


def _title_match_tier(query: str, posting_title: str) -> int:
    """2 = every query word appears in the posting title (strong match).
    1 = at least one query word appears (weak - e.g. "Engineer" alone
    matches almost anything). 0 = no match at all. Callers must prefer
    tier 2 whenever any tier-2 candidate exists anywhere in the pool -
    otherwise a single weak tier-1 match can dominate the whole result
    via a recency tie-break, which is what happened before this fix
    (a query for "Software Engineer" returned an unrelated "Engineering
    Manager" posting because "engineer" is a substring of "engineering")."""
    words = [w for w in query.lower().split() if len(w) > 2]
    if not words:
        return 0
    posting_lower = posting_title.lower()
    # word-boundary match, not plain substring - otherwise "engineer" matches
    # inside "engineering" and "analytic" matches inside "analytics", turning
    # unrelated titles (e.g. "Engineering Manager") into false "strong" matches
    hits = [bool(re.search(rf"\b{re.escape(w)}\b", posting_lower)) for w in words]
    if all(hits):
        return 2
    if any(hits):
        return 1
    return 0


def _location_matches(query: str, posting_location: str) -> bool:
    if not query or query.strip().lower() == "any":
        return True
    return query.lower() in (posting_location or "").lower()


def _work_setup_matches(work_setup: str, posting_location: str) -> bool:
    if work_setup and work_setup.strip().lower() == "remote":
        return "remote" in (posting_location or "").lower()
    return True  # hybrid/onsite/Any: not reliably filterable from this endpoint, don't exclude


async def search_vacancies(job_title: str, location: str, work_setup: str,
                            industry: str, seen_companies=None, max_results: int = 3) -> list:
    """Returns up to `max_results` matches, at most one per company (so a
    single search doesn't hand back 3 postings from the same employer),
    preferring the strongest title-match tier available and, within a
    tier, the most recently updated posting."""
    seen = {c.lower() for c in (seen_companies or [])}
    companies = db.get_active_companies()
    slugs = [s for s, name in companies.items() if name.lower() not in seen]

    async with httpx.AsyncClient(timeout=8.0) as client:
        results = await asyncio.gather(*[_fetch_company_jobs(client, s) for s in slugs])

    candidates = []
    for slug, jobs in zip(slugs, results):
        company_name = companies[slug]
        for job in jobs:
            title = job.get("title", "")
            loc = (job.get("location") or {}).get("name", "")
            tier = _title_match_tier(job_title, title)
            if tier and _location_matches(location, loc) and _work_setup_matches(work_setup, loc):
                candidates.append({
                    "title": title,
                    "company": company_name,
                    "location": loc or "Not specified",
                    "url": job.get("absolute_url", ""),
                    "summary": _strip_html(job.get("content", ""))[:400],
                    "updated_at": job.get("updated_at", ""),
                    "_tier": tier,
                })

    if not candidates:
        return []

    best_tier = max(c["_tier"] for c in candidates)
    candidates = [c for c in candidates if c["_tier"] == best_tier]
    candidates.sort(key=lambda c: c["updated_at"], reverse=True)

    picked = []
    seen_this_call = set()
    for c in candidates:
        if c["company"] in seen_this_call:
            continue
        seen_this_call.add(c["company"])
        del c["updated_at"]
        del c["_tier"]
        picked.append(c)
        if len(picked) >= max_results:
            break
    return picked
