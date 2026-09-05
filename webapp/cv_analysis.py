"""
CV-vs-JD analysis engine (ATS score, XYZ formula check, tool radar, level
assessment, roadmap), self-contained for this service (deploy isolation -
see vacancy_source.py's docstring for why). Mirrors bot/coach.py's
analyze_cv/generate_cv_fixes/generate_roadmap/roadmap_block_title/
roadmap_max_item exactly, using analysis_prompts.py in place of bot/prompts.py.

Distinct from webapp/cv_fixes.py's generate_cv_fixes(level, vacancy, cv_text)
- that one rewrites a CV against one already-found vacancy (a different,
lighter feature); this generate_cv_fixes(level, jd, cv_text) is roadmap item 1
of the full JD-analysis flow. Both are kept, not merged.
"""

import json
import os
import re

import anthropic
from dotenv import load_dotenv

from analysis_prompts import ANALYSIS_PROMPT, ROADMAP_BLOCKS

load_dotenv()

client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5"


def _extract_json(text: str, array: bool = False):
    pattern = r'\[.*\]' if array else r'\{.*\}'
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in response: {text[:200]}")
    return json.loads(match.group(0))


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


async def generate_roadmap_item(level: str, item: int, jd: str, cv_text: str) -> str:
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
