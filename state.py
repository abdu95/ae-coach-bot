# In-memory state per user.
# Resets if the bot restarts. For persistence, swap dict for SQLite.

_users: dict = {}

def get(user_id: int) -> dict:
    if user_id not in _users:
        _users[user_id] = _empty()
    return _users[user_id]

def reset(user_id: int) -> None:
    _users[user_id] = _empty()


def _empty() -> dict:
    return {
        "phase": "idle",
        "cv_b64": "",
        "job_title": "",
        "location": "",
        "work_setup": "",
        "industry": "",
        "suggested_titles": [],
        "current_vacancy": None,    # the one being shown
        "seen_companies": [],       # companies already shown
        "search_count": 0,          # capped at 3
        "chosen_vacancy": None,
        "outputs": None,
        "level": "",
    }