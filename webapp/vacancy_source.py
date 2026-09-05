"""
Vacancy sourcing for the webapp service. Backed by greenhouse_source.py
(Greenhouse's public per-company API) as of 2026-09-05, replacing the
earlier Claude-web-search implementation after live use surfaced
occasional dead/stale links. See greenhouse_source.py's docstring for
what this trades off (small hand-verified company list, no industry
filter yet).
"""

import greenhouse_source


async def search_vacancies(job_title: str, location: str, work_setup: str,
                            industry: str, seen_companies=None) -> list:
    """Returns 0-3 matches (greenhouse_source's default), one per company -
    the Mini App shows these as a browsable carousel rather than forcing
    one-at-a-time "search again" round trips for variety."""
    return await greenhouse_source.search_vacancies(
        job_title, location, work_setup, industry, seen_companies=seen_companies
    )
