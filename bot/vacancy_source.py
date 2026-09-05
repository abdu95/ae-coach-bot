"""
Vacancy sourcing, kept behind one interface so the implementation can be
swapped without touching any caller. No dependency on bot.py, state.py,
or the Mini App - anything can import and call search_vacancies().

Backed by greenhouse_source.py (Greenhouse's public per-company API) as
of 2026-09-05, replacing the earlier Claude-web-search approach
(coach.search_one_vacancy, still present but no longer called by
default) after live use surfaced occasional dead/stale links. See
greenhouse_source.py's docstring for what this trades off.
"""

import greenhouse_source


async def search_vacancies(job_title: str, location: str, work_setup: str,
                            industry: str, seen_companies=None) -> list:
    """Returns 0 or 1 matching vacancy as a list - the contract callers
    depend on. greenhouse_source can surface more than one match
    internally; this only ever returns the single best one for now (see
    the "how many vacancies to show" backlog item for revisiting that)."""
    return await greenhouse_source.search_vacancies(
        job_title, location, work_setup, industry, seen_companies=seen_companies
    )
