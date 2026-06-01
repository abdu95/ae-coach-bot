import os
import re


import json
import anthropic
from dotenv import load_dotenv
from prompts import ANALYSIS_PROMPT, ROADMAP_PROMPTS

load_dotenv()
print("API KEY LOADED:", os.getenv("ANTHROPIC_API_KEY"))


client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5"


async def analyze_cv(jd: str, cv_b64: str) -> dict:
    """
    Call 1: analyze CV against JD.
    Returns parsed dict with keys: ats, xyz, tools, level.
    """
    response = await client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": cv_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": f"JOB DESCRIPTION:\n{jd}\n\n{ANALYSIS_PROMPT}",
                    },
                ],
            }
        ],
    )

    raw = response.content[0].text.strip()
    # Strip markdown fences if Claude adds them despite instructions
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


async def generate_roadmap(level: str, jd: str, cv_b64: str) -> str:
    """
    Call 2: generate Output 5 roadmap based on level.
    Uses web search for target companies / stepping-stone roles.
    """
    prompt = ROADMAP_PROMPTS.get(level, ROADMAP_PROMPTS["Junior"])

    response = await client.messages.create(
        model=MODEL,
        max_tokens=2500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": cv_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": f"JOB DESCRIPTION:\n{jd}\n\n{prompt}",
                    },
                ],
            }
        ],
    )

    # Extract text blocks only (web search results are incorporated by the API)
    return "".join(
        block.text for block in response.content if block.type == "text"
    )


async def suggest_job_titles(cv_b64: str) -> list:
    """Analyse CV and return 5 suggested job titles."""
    from prompts import JOB_TITLE_PROMPT
    response = await client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": cv_b64}},
                {"type": "text", "text": JOB_TITLE_PROMPT}
            ]
        }]
    )
    raw = response.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)


async def search_vacancies(job_title: str, location: str, work_setup: str, industry: str) -> list:
    """Search live job postings and return 5 matches."""
    from prompts import VACANCY_SEARCH_PROMPT
    prompt = VACANCY_SEARCH_PROMPT.format(
        job_title=job_title,
        location=location,
        work_setup=work_setup,
        industry=industry
    )
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )
    text = "".join(b.text for b in response.content if b.type == "text")
        # Web search responses wrap JSON in prose — extract the JSON array
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON array found in response: {text[:200]}")
    return json.loads(match.group(0))


async def score_vacancy(cv_b64: str, vacancy: dict) -> dict:
    """Score CV against one vacancy. Returns score, matched, missing, verdict."""
    from prompts import VACANCY_SCORE_PROMPT
    jd_text = f"{vacancy['title']} at {vacancy['company']}\n{vacancy['summary']}"
    response = await client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": cv_b64}},
                {"type": "text", "text": f"JOB DESCRIPTION:\n{jd_text}\n\n{VACANCY_SCORE_PROMPT}"}
            ]
        }]
    )
    raw = response.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(raw)