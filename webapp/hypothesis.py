"""
Job title suggestion, self-contained for this service (deploy isolation -
see vacancy_source.py's docstring for why). Mirrors bot/coach.py's
suggest_job_titles exactly.
"""

import json
import os
import re

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5"

JOB_TITLE_PROMPT = """
Analyze this CV and suggest exactly 5 job titles this candidate is most suited for,
based on their domain, education, tools, and experience.

Return ONLY a JSON array of 5 strings. No preamble, no explanation.
Example: ["Data Analyst", "Analytics Engineer", "Data Engineer", "BI Developer", "Data Scientist"]
"""


async def suggest_job_titles(cv_text: str) -> list:
    response = await client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": f"CV:\n{cv_text}\n\n{JOB_TITLE_PROMPT}"}],
    )
    text = response.content[0].text
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON array found in response: {text[:200]}")
    return json.loads(match.group(0))


CURRENT_POSITION_PROMPT = """
Look at this CV and identify the candidate's most recent or current job title
(the role at their most recent/present employer, or their field of study if
they have no work experience yet).

Return ONLY that title as a short plain string, 1-5 words, no preamble, no
quotes, no explanation. Example: Data Analyst
"""


async def extract_current_position(cv_text: str) -> str:
    """Best-effort label for a CV in a list (e.g. 'Data Analyst') - not a
    recommendation like suggest_job_titles, just what's already on the CV."""
    response = await client.messages.create(
        model=MODEL,
        max_tokens=30,
        messages=[{"role": "user", "content": f"CV:\n{cv_text}\n\n{CURRENT_POSITION_PROMPT}"}],
    )
    return response.content[0].text.strip().strip('"')
