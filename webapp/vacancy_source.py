"""
Self-contained vacancy search for the webapp service, deployed independently
from the main bot (path-as-root = webapp/, no access to files outside this
folder). Deliberately duplicates coach.py's search_one_vacancy rather than
importing across the deploy boundary, so this service has no dependency on
the rest of the repo. If/when this Mini App becomes permanent, reconcile
with the root-level vacancy_source.py (the bot-side implementation) instead
of maintaining two copies long-term.
"""

import json
import os
import re

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5"

VACANCY_SEARCH_PROMPT = """
Search for ONE currently active job posting matching these criteria as closely as possible:
- Job title: {job_title}
- Location: {location}
- Work setup: {work_setup}
- Industry: {industry}

If you cannot find a perfect match, return the closest real active posting you can find.
A close match is better than no result. Do not invent postings.

{exclude}

Return ONLY a JSON object (not an array) with these exact keys:
{{
  "company": "company name",
  "title": "exact job title",
  "location": "city and country",
  "url": "direct link to the posting",
  "summary": "2-sentence role description"
}}

No preamble. Raw JSON only.
"""


async def search_vacancies(job_title: str, location: str, work_setup: str,
                            industry: str, seen_companies=None) -> list:
    exclude = ""
    if seen_companies:
        exclude = f"Do NOT return jobs from these companies (already shown): {', '.join(seen_companies)}"

    prompt = VACANCY_SEARCH_PROMPT.format(
        job_title=job_title, location=location,
        work_setup=work_setup, industry=industry, exclude=exclude
    )
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return []
    return [json.loads(match.group(0))]
