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
        "phase": "idle",          # current stage
        "cv_b64": "",             # base64 CV
        "job_title": "",          # chosen or typed job title
        "location": "",           # EU / US / custom
        "work_setup": "",         # remote / office / hybrid
        "industry": "",           # health / fintech / custom
        "suggested_titles": [],   # 5 titles Claude suggested
        "vacancies": [],          # 5 vacancy dicts from search
        "vacancy_index": 0,       # which vacancy user is viewing
        "chosen_vacancy": None,   # vacancy user chose to apply
        "current_step": 0,        # 1-5 analysis steps
    }