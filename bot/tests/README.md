# Tests

Script-style, not pytest fixtures yet (fast to write during active development;
converting to proper pytest fixtures is a reasonable follow-up, not urgent).

Each file is a standalone script: it stubs out `state`'s DB calls so nothing
touches a real Postgres, then asserts against the real `bot.py`/`state.py`
logic. `_helpers.py` is not a test itself - it's shared scaffolding
(`FakeMessage`, the `state.*` monkey-patching, a fake connection-pool
builder) every other file here imports, so run only the `test_*.py` files.

**Requires Python 3.10+** (the codebase uses `X | None` union syntax) - on a
machine where the default `python3` is older, point at a 3.11 interpreter
matching `runtime.txt` instead.

Run from the repo root:

```bash
python3 bot/tests/test_launcher_flow.py
python3 bot/tests/test_marketing_source.py
python3 bot/tests/test_checks_used_not_clobbered.py
python3 bot/tests/test_payment_stats.py
```

Each prints `PASS: ...` per check and exits non-zero (via an uncaught
`AssertionError`) on failure. Run all four before deploying `ae-coach-bot`.
The Mini App (`vacancy-webapp`) has its own, separate `tests/` (Python) and
`tests/js/` (Node) suites in its own repo.
