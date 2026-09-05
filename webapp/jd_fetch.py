"""
Fetches and extracts job-description text from a pasted URL, so the
CV-vs-JD analysis screen accepts a link as an alternative to pasting the
full text. Self-contained for this service (deploy isolation - see
vacancy_source.py's docstring for why).

This is whole-page text extraction, not a job-board-aware scraper - it
strips script/style/nav/header/footer blocks and remaining tags, then
returns the rest as plain text. Quality varies by site (cookie banners,
related-job lists, etc. can leak into the result); good enough as a
convenience for pasting a link instead of manually copying text, not a
guarantee of a clean, isolated job description.
"""

import html
import re

import httpx

_URL_PATTERN = re.compile(r"^https?://\S+$")
_MAX_CHARS = 20_000


def looks_like_url(text: str) -> bool:
    return bool(_URL_PATTERN.match(text.strip()))


def _extract_text(raw_html: str) -> str:
    text = re.sub(r"<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", raw_html,
                  flags=re.IGNORECASE | re.DOTALL)
    text = html.unescape(html.unescape(text))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


async def fetch_jd_text(url: str) -> str:
    """Raises httpx.HTTPError on network/HTTP failure - callers should
    catch and show a friendly 'couldn't read that link' message."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
        response = await client.get(
            url, headers={"User-Agent": "Mozilla/5.0 (compatible; AcceptedAI/1.0)"}
        )
        response.raise_for_status()
    return _extract_text(response.text)[:_MAX_CHARS]
