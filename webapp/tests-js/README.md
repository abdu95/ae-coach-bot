# Frontend tests

Tests `webapp/static/app.js` for real, against the actual `index.html`/`app.js`
files (not rewritten copies) via [jsdom](https://github.com/jsdom/jsdom) +
Node's built-in test runner (`node --test`). No browser, no Python involved -
this is the first JS test setup in the repo (the Python `tests/` directories
test the FastAPI/bot backends only).

**Why jsdom instead of testing extracted functions**: `app.js` is a single
script with DOM calls throughout (not modularized), so most of its logic
can't be unit-tested in isolation without either rewriting production code
into modules or faking a DOM. jsdom lets the real file run unmodified and
be driven the way a browser would - clicking buttons, checking what's
visible, mocking only `fetch`/`Telegram.WebApp`.

**A quirk worth knowing**: top-level `function` declarations in `app.js`
attach to `window` (so `window.pickTitle(...)` etc. work from a test and
correctly mutate the module's internal state via closure), but `const
state = {...}` and `let currentLang` do NOT become `window` properties -
that's normal JS scoping for indirect `eval`, not a jsdom bug. So tests
never read/write `window.state` or `window.currentLang` directly; every
precondition is set by calling the same functions a real user action would
trigger, and every assertion is on observable DOM/API-call behavior.

## Setup (once)

```bash
cd webapp/tests-js
npm install
```

## Run

```bash
cd webapp/tests-js
npm test
```

## Files

- `helpers.js` - `loadApp()` boots a jsdom window from the real `index.html`,
  strips `<script src>`/`<link>` tags (so jsdom never tries to fetch the
  external `telegram-web-app.js` or the local `app.js`/`style.css` over the
  network), then injects `app.js` via `window.eval` with `Telegram.WebApp`
  and `fetch` mocked. `makeFetchMock()` builds a `fetch` stub from a
  `{ "/api/path": handler }` map; `flush()` waits out the async
  `checkCVAndRoute()` call that fires at script load.
- `app.test.js` - the actual test cases, covering: pure i18n/formatting
  logic, the welcome → options → inline-CV-upload-per-path first-run flow,
  the session-wide (not per-title) vacancy-search cap, the applications
  detail double-back-button fix, roadmap items appending instead of
  replacing each other, the post-roadmap next-step flow, and the
  checks-remaining header badge.
