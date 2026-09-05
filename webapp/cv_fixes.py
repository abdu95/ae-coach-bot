"""
CV fix recommendations against a specific vacancy, self-contained for this
service (deploy isolation - see vacancy_source.py's docstring for why).
Mirrors bot/coach.py's generate_cv_fixes + the Junior/Mid/Senior "CV Fixes"
prompts from bot/prompts.py exactly.

Pre-Junior is deliberately NOT a key here: in the original roadmap,
Pre-Junior's item 1 is a "3-Month Plan", not "CV Fixes" - passing
"Pre-Junior" through unchanged would silently generate the wrong content.
Falls back to the Junior prompt instead (same fallback bot/coach.py's own
ROADMAP_BLOCKS.get(level, ROADMAP_BLOCKS["Junior"]) uses for any
unrecognized level).
"""

import json
import os
import re

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-5"

_JUNIOR_CONTEXT = """
CONTEXT:
- First identify the target role from the JD.
- Candidate level: Junior (0-2 years production experience in this role's domain)
- Your task: identify the gap between what the JD requires and what the CV demonstrates,
  then close that gap at Junior depth.

GAP ANALYSIS RULES:
- Only give advice tied to a specific missing skill or weakness relative to THIS JD
- Do not give generic advice — every recommendation must reference something the JD requires
  that the CV lacks
- Prioritise gaps by hiring impact: what would make or break getting this specific role
- Be honest about what is missing — do not soften gaps
"""

_MID_CONTEXT = """
CONTEXT:
- First identify the target role from the JD.
- Candidate level: Mid (2-4 years production experience in this role's domain)
- Your task: identify the gap between what the JD requires and what the CV demonstrates,
  then close that gap at Mid depth.

GAP ANALYSIS RULES:
- Only give advice tied to specific missing skills or weaknesses relative to THIS JD
- Do not give generic advice — every recommendation grounded in a JD requirement the CV lacks
- Prioritise gaps by hiring impact: ownership, stakeholder communication, depth of craft
- At Mid level, gaps are often about demonstrating ownership and impact, not just tool knowledge
"""

_SENIOR_CONTEXT = """
CONTEXT:
- First identify the target role from the JD.
- Candidate level: Senior (4+ years production experience in this role's domain)
- Your task: identify the gap between what the JD requires and what the CV demonstrates,
  then close that gap at Senior depth.

GAP ANALYSIS RULES:
- Only give advice tied to specific missing signals relative to THIS JD
- At Senior level, gaps are usually about strategic scope, leadership narrative, and
  cross-org impact rather than tool knowledge - identify which type of gap this candidate has
- Do not give generic advice — reference specific JD requirements and specific CV weaknesses
- Be direct: if the CV reads like a Mid candidate, say so and fix it
"""

_ITEM_TEMPLATE = """
The candidate's CV and the target job description (JD) are provided.
{context}
DEPTH: {depth}
LENGTH: each field is ONE tightly worded sentence. No extra commentary.

Return ONLY a JSON array of exactly 5 objects, each with these exact keys:
[
  {{
    "issue": "<one short sentence: which JD requirement this CV bullet understates or misses>",
    "before": "<the exact original CV bullet - empty string \\"\\" if this fix adds something missing entirely, rather than rewriting>",
    "after": "<the rewritten (or new) bullet, max 30 words>"
  }},
  ...
]

No preamble, no markdown fences, no explanation - raw JSON array only.
"""

_PROMPTS = {
    "Junior": _ITEM_TEMPLATE.format(
        context=_JUNIOR_CONTEXT, depth="focus on quantification and clarity, not leadership language."),
    "Mid": _ITEM_TEMPLATE.format(
        context=_MID_CONTEXT, depth="emphasise ownership, business impact, and cross-team work — not just task descriptions."),
    "Senior": _ITEM_TEMPLATE.format(
        context=_SENIOR_CONTEXT, depth="every bullet must show scope, influence, and business outcome — not just execution."),
}


async def generate_cv_fixes(level: str, vacancy: dict, cv_text: str) -> list:
    prompt = _PROMPTS.get(level, _PROMPTS["Junior"])
    jd_text = f"{vacancy['title']} at {vacancy['company']}\n{vacancy['summary']}"
    response = await client.messages.create(
        model=MODEL,
        max_tokens=900,
        temperature=0.3,
        messages=[{
            "role": "user",
            "content": f"CV:\n{cv_text}\n\nJOB DESCRIPTION:\n{jd_text}\n\n{prompt}"
        }],
    )
    text = response.content[0].text
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON array found in response: {text[:200]}")
    return json.loads(match.group(0))
