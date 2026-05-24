import os


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
