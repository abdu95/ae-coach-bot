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
