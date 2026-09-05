# Tests

Script-style, not pytest fixtures yet (fast to write during active development;
converting to proper pytest fixtures is a reasonable follow-up, not urgent).

Each file is a standalone script: it stubs out `state`'s DB calls (or mocks
`db`/`vacancy_source`/etc. in the webapp tests) so nothing touches a real
Postgres or calls the real Anthropic API, then asserts against the real
`bot.py`/`server.py` logic.

**Requires Python 3.10+** (the codebase uses `X | None` union syntax) - on a
machine where the default `python3` is older, point at a 3.11 interpreter
matching `runtime.txt` instead.

Run from the repo root:

```bash
python3 bot/tests/test_jobs_flow.py
python3 bot/tests/test_ats_regression.py
python3 bot/tests/test_marketing_source.py
python3 webapp/tests/test_webapp_cv.py
```

Each prints `PASS: ...` per check and exits non-zero (via an uncaught
`AssertionError`) on failure. Run all four before deploying either service.
