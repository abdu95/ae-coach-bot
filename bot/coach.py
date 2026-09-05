import os
import json
import re
import anthropic
from dotenv import load_dotenv
from prompts import ANALYSIS_PROMPT, ROADMAP_BLOCKS

load_dotenv()

client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5"


def _extract_json(text: str, array: bool = False):
    """Pull a JSON object or array out of a possibly-prose response."""
    pattern = r'\[.*\]' if array else r'\{.*\}'
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in response: {text[:200]}")
    return json.loads(match.group(0))


async def suggest_job_titles(cv_text: str) -> list:
    """Analyse CV text and return 5 suggested job titles."""
    from prompts import JOB_TITLE_PROMPT
    response = await client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"CV:\n{cv_text}\n\n{JOB_TITLE_PROMPT}"
        }]
    )
    return _extract_json(response.content[0].text, array=True)


async def search_one_vacancy(job_title, location, work_setup, industry, seen_companies=None):
    """Search live job postings and return ONE match (or None)."""
    from prompts import VACANCY_SEARCH_PROMPT
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
        return None
    return json.loads(match.group(0))


async def score_vacancy(cv_text: str, vacancy: dict) -> dict:
    """Score CV text against one vacancy."""
    from prompts import VACANCY_SCORE_PROMPT
    jd_text = f"{vacancy['title']} at {vacancy['company']}\n{vacancy['summary']}"
    response = await client.messages.create(
        model=MODEL,
        max_tokens=400,
        messages=[{
            "role": "user",
            "content": f"CV:\n{cv_text}\n\nJOB DESCRIPTION:\n{jd_text}\n\n{VACANCY_SCORE_PROMPT}"
        }]
    )
    return _extract_json(response.content[0].text)


async def analyze_cv(jd: str, cv_text: str) -> dict:
    """Full analysis: ats, xyz, tools, level."""
    response = await client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"CV:\n{cv_text}\n\nJOB DESCRIPTION:\n{jd}\n\n{ANALYSIS_PROMPT}"
        }]
    )
    return _extract_json(response.content[0].text)


def roadmap_block_title(level: str, item: int) -> str:
    blocks = ROADMAP_BLOCKS.get(level, ROADMAP_BLOCKS["Junior"])
    return blocks[item]["title"]


def roadmap_max_item(level: str) -> int:
    blocks = ROADMAP_BLOCKS.get(level, ROADMAP_BLOCKS["Junior"])
    return max(blocks.keys())


async def generate_cv_fixes(level: str, jd: str, cv_text: str) -> list:
    """Generate the Top-5 CV fixes as structured data (item 1 of the roadmap)."""
    blocks = ROADMAP_BLOCKS.get(level, ROADMAP_BLOCKS["Junior"])
    block = blocks[1]
    response = await client.messages.create(
        model=MODEL,
        max_tokens=block.get("max_tokens", 900),
        temperature=0.3,
        messages=[{
            "role": "user",
            "content": f"CV:\n{cv_text}\n\nJOB DESCRIPTION:\n{jd}\n\n{block['prompt']}"
        }]
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    return _extract_json(text, array=True)


async def generate_roadmap(level: str, item: int, jd: str, cv_text: str) -> str:
    """Generate one roadmap action item for the given level."""
    blocks = ROADMAP_BLOCKS.get(level, ROADMAP_BLOCKS["Junior"])
    block = blocks[item]
    prompt = block["prompt"]
    response = await client.messages.create(
        model=MODEL,
        max_tokens=block.get("max_tokens", 1800),
        temperature=0.3,
        messages=[{
            "role": "user",
            "content": f"CV:\n{cv_text}\n\nJOB DESCRIPTION:\n{jd}\n\n{prompt}"
        }]
    )
    return "".join(b.text for b in response.content if b.type == "text")