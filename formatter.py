"""
Format Claude outputs as Telegram HTML messages.
Telegram HTML supports: <b>, <i>, <code>, <pre>, <a>
Max message length: 4096 chars. split_long() handles overflow.
"""

TOOL_EMOJI = {
    "strong": "✅",
    "mentioned": "🟡",
    "not_found": "❌",
}

TOOL_LABELS = {
    "Git": "Git / GitHub",
    "SQL": "SQL",
    "Python": "Python",
    "dbt": "dbt",
    "data_warehouse": "Data Warehouse",
    "Cloud": "Cloud (AWS/GCP/Azure)",
}


def step_ats(ats: dict) -> str:
    score = ats["score"]
    bar = _score_bar(score)
    matched = ", ".join(ats.get("matched", [])) or "none"
    missing = ", ".join(ats.get("missing", [])) or "none"
    verdict = ats.get("verdict", "")

    return (
        f"<b>📊 Output 1 — ATS Score</b>\n\n"
        f"<b>Score: {score}/100</b>\n"
        f"{bar}\n\n"
        f"<b>Matched keywords:</b> {matched}\n\n"
        f"<b>Missing keywords:</b> {missing}\n\n"
        f"{verdict}"
    )


def step_xyz(xyz: dict) -> str:
    passing = xyz.get("passing", [])
    failing = xyz.get("failing", [])
    rewrites = xyz.get("rewrites", [])

    lines = ["<b>✍️ Output 2 — XYZ Formula Check</b>"]
    lines.append("\nThe ideal bullet: <i>Accomplished X as measured by Y by doing Z</i>\n")

    if passing:
        lines.append(f"<b>✅ Passing ({len(passing)}):</b>")
        for b in passing[:3]:
            lines.append(f"• {_esc(b)}")

    if failing:
        lines.append(f"\n<b>❌ Needs work ({len(failing)}):</b>")
        for b in failing[:3]:
            lines.append(f"• {_esc(b)}")

    if rewrites:
        lines.append("\n<b>Suggested rewrites:</b>")
        for i, r in enumerate(rewrites[:2], 1):
            orig = _esc(r.get("original", ""))
            improved = _esc(r.get("improved", ""))
            lines.append(f"\n<i>Before:</i> {orig}")
            lines.append(f"<i>After:</i>  {improved}")

    return "\n".join(lines)


def step_tools(tools: dict) -> str:
    lines = ["<b>🛠 Output 3 — Tool Radar</b>\n"]
    for key, label in TOOL_LABELS.items():
        rating = tools.get(key, "not_found")
        emoji = TOOL_EMOJI.get(rating, "❓")
        rating_text = rating.replace("_", " ").title()
        lines.append(f"{emoji}  <b>{label}</b> — {rating_text}")

    lines.append("\n✅ Strong  🟡 Mentioned  ❌ Not found")
    return "\n".join(lines)


def step_level(level: dict) -> str:
    assessment = level.get("assessment", "Unknown")
    reasoning = level.get("reasoning", "")

    level_emoji = {
        "Pre-Junior": "🌱",
        "Junior": "📗",
        "Mid": "📘",
        "Senior": "📙",
    }.get(assessment, "📄")

    return (
        f"<b>{level_emoji} Output 4 — Level Assessment</b>\n\n"
        f"<b>Level: {assessment}</b>\n\n"
        f"{reasoning}"
    )


def step_roadmap_header(level: str) -> str:
    return f"<b>🗺 Output 5 — Your Roadmap ({level})</b>\n\n⏳ Searching for live roles and building your plan..."


def format_roadmap(text: str) -> str:
    """
    Convert markdown-ish roadmap text from Claude into Telegram HTML.
    Handles ### headers, numbered lists, bullet points, bold.
    """
    lines = text.split("\n")
    out = []
    for line in lines:
        if line.startswith("### "):
            out.append(f"\n<b>{_esc(line[4:])}</b>")
        elif line.startswith("## "):
            out.append(f"\n<b>{_esc(line[3:])}</b>")
        else:
            # Convert **bold** to <b>bold</b>
            converted = _bold(line)
            out.append(converted)
    return "\n".join(out)


def split_long(text: str, limit: int = 4000) -> list[str]:
    """Split text into chunks under the Telegram message limit."""
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks


# ── helpers ──────────────────────────────────────────────────────────────────

def _score_bar(score: int) -> str:
    filled = round(score / 10)
    empty = 10 - filled
    return "█" * filled + "░" * empty + f"  {score}%"


def _esc(text: str) -> str:
    """Minimal HTML escaping for Telegram HTML mode."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _bold(text: str) -> str:
    """Convert **text** to <b>text</b> and escape surrounding content."""
    import re
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    result = []
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            result.append(f"<b>{_esc(part[2:-2])}</b>")
        else:
            result.append(_esc(part))
    return "".join(result)


def vacancy_card(vacancy: dict, score: dict, index: int, total: int) -> str:
    pct = score.get("score", 0)
    bar = _score_bar(pct)
    matched = ", ".join(score.get("matched", [])) or "none"
    missing = ", ".join(score.get("missing", [])) or "none"

    return (
        f"<b>Search {index} of {total} · {pct}% Match</b>\n"
        f"{bar}\n\n"
        f"<b>{_esc(vacancy['title'])}</b> @ <b>{_esc(vacancy['company'])}</b>\n"
        f"📍 {_esc(vacancy['location'])}\n\n"
        f"{_esc(vacancy['summary'])}\n\n"
        f"✅ <b>Matched:</b> {_esc(matched)}\n"
        f"❌ <b>Missing:</b> {_esc(missing)}\n\n"
        f"🔗 <a href='{vacancy['url']}'>View job posting</a>"
    )