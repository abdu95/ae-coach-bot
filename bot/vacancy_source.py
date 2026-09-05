"""
Vacancy sourcing, kept behind one interface so the implementation can be
swapped (LLM web search today -> hh.uz API or direct ATS crawling later)
without touching any caller. No dependency on bot.py, state.py, or the
Mini App - anything can import and call search_vacancies().
"""

import coach


async def search_vacancies(job_title: str, location: str, work_setup: str,
                            industry: str, seen_companies=None) -> list:
    """Return 0 or 1 matching vacancy as a list (today's LLM-web-search
    backend only ever returns one result per call). A future structured
    source (hh.uz, ATS crawling) can return more per call without changing
    this signature's contract to callers: a list of vacancy dicts."""
    vacancy = await coach.search_one_vacancy(
        job_title, location, work_setup, industry, seen_companies=seen_companies
    )
    return [vacancy] if vacancy else []
