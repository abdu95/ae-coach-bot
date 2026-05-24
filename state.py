# In-memory state per user.
# Resets if the bot restarts. For persistence, swap dict for SQLite.

from typing import Optional

_users: dict = {}

PHASES = [
    "idle",           # waiting for JD
    "jd_received",    # JD stored, waiting for CV
    "analyzing",      # CV uploaded, Claude call in progress
    "output_1",       # showing ATS score, waiting for Continue
    "output_2",       # showing XYZ check, waiting for Continue
    "output_3",       # showing tool radar, waiting for Continue
    "output_4",       # showing level, waiting for Continue
    "output_5",       # generating/showing roadmap
    "done",           # complete
]


def get(user_id: int) -> dict:
    if user_id not in _users:
        _users[user_id] = _empty()
    return _users[user_id]


def reset(user_id: int) -> None:
    _users[user_id] = _empty()


def _empty() -> dict:
    return {
        "phase": "idle",
        "jd": "",
        "cv_b64": "",
        "outputs": None,   # dict with keys: ats, xyz, tools, level
        "level": "",       # Pre-Junior | Junior | Mid | Senior
    }
