const fs = require("fs");
const path = require("path");
const { JSDOM } = require("jsdom");

const STATIC_DIR = path.resolve(__dirname, "..", "static");

/**
 * Loads the REAL index.html + app.js (not a rewritten copy) into a jsdom
 * window, with Telegram.WebApp and fetch mocked. Strips <script src> /
 * <link> tags before parsing so jsdom never tries to fetch the external
 * telegram-web-app.js or our own app.js/style.css over the network -
 * app.js is injected manually via window.eval after the mocks are in
 * place, so its top-level checkCVAndRoute() call hits the mock fetch.
 */
function loadApp({ user = { id: 777, first_name: "Test", username: "testuser" }, fetchImpl } = {}) {
  let rawHtml = fs.readFileSync(path.join(STATIC_DIR, "index.html"), "utf8");
  rawHtml = rawHtml.replace(/<script[^>]*><\/script>/g, "");
  rawHtml = rawHtml.replace(/<link[^>]*>/g, "");

  // "dangerously" (safe here - we've stripped every <script>/<link> tag
  // above, so nothing auto-executes at parse time) is needed so inline
  // onclick="..." HTML attributes get wired up as real event handlers,
  // not just "outside-only" which only lets us eval() code manually.
  const dom = new JSDOM(rawHtml, { url: "https://example.com/", runScripts: "dangerously" });
  const { window } = dom;

  window.Telegram = {
    WebApp: {
      initData: "mock_init_data",
      initDataUnsafe: { user },
      ready() {},
      expand() {},
      openLink(url) { window.__lastOpenedLink = url; },
    },
  };

  if (!window.requestAnimationFrame) {
    window.requestAnimationFrame = (cb) => setTimeout(cb, 0);
  }
  // jsdom doesn't implement scrollTo (irrelevant for these tests, just noisy)
  window.scrollTo = () => {};

  window.fetch = fetchImpl || defaultFetchMock();

  const appJs = fs.readFileSync(path.join(STATIC_DIR, "app.js"), "utf8");
  window.eval(appJs);

  return dom;
}

/** Waits for pending microtasks/timers (checkCVAndRoute etc. are async). */
function flush(times = 3) {
  return new Promise((resolve) => {
    let n = 0;
    const tick = () => {
      n += 1;
      if (n >= times) return resolve();
      setTimeout(tick, 0);
    };
    setTimeout(tick, 0);
  });
}

/**
 * Builds a fetch mock from a map of { "/api/path": handler(body) -> respBody }.
 * handler may return a plain object (200 OK) or { status, body } for errors.
 * FormData bodies (multipart uploads) are not JSON-parsed - handlers for
 * those paths receive `null` as the body.
 */
function makeFetchMock(handlers) {
  return async (url, opts = {}) => {
    const pathname = new URL(url, "https://example.com/").pathname;
    const handler = handlers[pathname];
    if (!handler) {
      throw new Error(`No mock registered for ${pathname}`);
    }
    let body = null;
    if (opts.body && typeof opts.body === "string") {
      try { body = JSON.parse(opts.body); } catch { body = null; }
    }
    const result = await handler(body);
    const status = result && result.status ? result.status : 200;
    const payload = result && result.status ? result.body : result;
    return {
      ok: status >= 200 && status < 300,
      status,
      json: async () => payload,
    };
  };
}

function defaultFetchMock(overrides = {}) {
  return makeFetchMock({
    "/api/cv-status": () => ({ has_cv: false, lang: "en" }),
    "/api/quota-status": () => ({ remaining: 3, quota: 3, price_per_check_tiyin: 1000000 }),
    ...overrides,
  });
}

module.exports = { loadApp, flush, makeFetchMock, defaultFetchMock };
