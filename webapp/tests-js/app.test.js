const test = require("node:test");
const assert = require("node:assert/strict");
const { loadApp, flush, defaultFetchMock } = require("./helpers");

// Top-level `function` declarations in app.js attach to `window` (so
// window.pickTitle(...) etc. work and correctly mutate the module's
// internal state via closure), but `const state = {...}` / `let
// currentLang` do NOT become window properties - that's normal JS
// scoping for indirect eval, not a jsdom quirk. So these tests never
// read/write `window.state` or `window.currentLang` directly; every
// precondition is set by driving the same functions a real user would
// trigger (pickTitle, analyzeCV, uploadCV, ...), and every assertion is
// on observable DOM/API-call behavior - which is what actually matters.

// ── Pure logic ────────────────────────────────────────────────────────

test("looksLikeUrl distinguishes a bare URL from JD text", async () => {
  const dom = loadApp({ fetchImpl: defaultFetchMock() });
  await flush();
  const { window } = dom;
  assert.equal(window.looksLikeUrl("https://boards.greenhouse.io/acme/jobs/1"), true);
  assert.equal(window.looksLikeUrl("http://example.com"), true);
  assert.equal(window.looksLikeUrl("We are looking for a Data Analyst..."), false);
  assert.equal(window.looksLikeUrl("check out https://example.com for details"), false);
});

test("t() renders the language the backend reports, not just English", async () => {
  const dom = loadApp({ fetchImpl: defaultFetchMock({ "/api/cv-status": () => ({ has_cv: true, lang: "ru" }) }) });
  await flush();
  const { window } = dom;
  assert.equal(window.t("get_roadmap_btn"), "🗺 Получить план");
});

test("t() interpolates {vars} into the template", async () => {
  const dom = loadApp({ fetchImpl: defaultFetchMock({ "/api/cv-status": () => ({ has_cv: true, lang: "en" }) }) });
  await flush();
  const { window } = dom;
  assert.equal(window.t("nav_checks_badge", { remaining: 2, quota: 3 }), "🎫 2/3");
});

test("checksLabel pluralizes in English", async () => {
  const dom = loadApp({ fetchImpl: defaultFetchMock({ "/api/cv-status": () => ({ has_cv: true, lang: "en" }) }) });
  await flush();
  const { window } = dom;
  assert.equal(window.checksLabel(1), "1 check");
  assert.equal(window.checksLabel(5), "5 checks");
});

test("formatRoadmapText converts markdown headers/bold and escapes raw HTML", async () => {
  const dom = loadApp({ fetchImpl: defaultFetchMock() });
  await flush();
  const { window } = dom;
  const out = window.formatRoadmapText("### Target Companies\n**Bold text** and <script>alert(1)</script>");
  assert.match(out, /<b>Target Companies<\/b>/);
  assert.match(out, /<b>Bold text<\/b>/);
  assert.ok(!out.includes("<script>"), "a raw script tag must come out escaped");
});

// ── Routing: welcome vs home, first-run flow ─────────────────────────────

test("checkCVAndRoute shows welcome-screen for a brand-new user (no CV), not a forced upload", async () => {
  const dom = loadApp({ fetchImpl: defaultFetchMock({ "/api/cv-status": () => ({ has_cv: false, lang: "en" }) }) });
  await flush();
  const { document } = dom.window;
  assert.equal(document.getElementById("welcome-screen").hidden, false);
  assert.equal(document.getElementById("home-screen").hidden, true);
  assert.equal(document.getElementById("cv-gate").hidden, true, "CV upload must not be forced as step 1 anymore");
});

test("checkCVAndRoute skips welcome and shows home-screen directly for a returning user", async () => {
  const dom = loadApp({ fetchImpl: defaultFetchMock({ "/api/cv-status": () => ({ has_cv: true, lang: "en" }) }) });
  await flush();
  const { document } = dom.window;
  assert.equal(document.getElementById("home-screen").hidden, false);
  assert.equal(document.getElementById("welcome-screen").hidden, true);
});

test("welcome-screen's continue button reveals the home-screen options", async () => {
  const dom = loadApp({ fetchImpl: defaultFetchMock({ "/api/cv-status": () => ({ has_cv: false, lang: "en" }) }) });
  await flush();
  const { document } = dom.window;
  document.getElementById("welcome-continue-btn").onclick();
  assert.equal(document.getElementById("home-screen").hidden, false);
});

// ── Inline CV-upload gating (asked only when the chosen path needs it) ──

test("goToAnalysis routes to cv-gate (not straight to the JD box) when no CV is on file", async () => {
  const dom = loadApp({ fetchImpl: defaultFetchMock({ "/api/cv-status": () => ({ has_cv: false, lang: "en" }) }) });
  await flush();
  const { document, window } = dom.window;
  window.goToAnalysis();
  assert.equal(document.getElementById("cv-gate").hidden, false);
  assert.equal(document.getElementById("analysis-screen").hidden, true);
});

test("goToVacancySearch routes to cv-gate when no CV is on file", async () => {
  const dom = loadApp({ fetchImpl: defaultFetchMock({ "/api/cv-status": () => ({ has_cv: false, lang: "en" }) }) });
  await flush();
  const { document, window } = dom.window;
  window.goToVacancySearch();
  assert.equal(document.getElementById("cv-gate").hidden, false);
  assert.equal(document.getElementById("title-screen").hidden, true);
});

test("goToAnalysis skips cv-gate and opens the JD box directly once a CV is on file", async () => {
  const dom = loadApp({ fetchImpl: defaultFetchMock({ "/api/cv-status": () => ({ has_cv: true, lang: "en" }) }) });
  await flush();
  const { document, window } = dom.window;
  window.goToAnalysis();
  assert.equal(document.getElementById("analysis-screen").hidden, false);
  assert.equal(document.getElementById("jd-input-box").hidden, false);
});

test("uploading a CV after goToAnalysis lands on the analysis screen (not home)", async () => {
  const dom = loadApp({
    fetchImpl: defaultFetchMock({
      "/api/cv-status": () => ({ has_cv: false, lang: "en" }),
      "/api/upload-cv": () => ({ saved: true }),
    }),
  });
  await flush();
  const { document, window } = dom.window;
  window.goToAnalysis(); // no CV yet -> lands on cv-gate
  const file = new window.File(["cv text"], "resume.pdf", { type: "application/pdf" });
  Object.defineProperty(document.getElementById("cv_file"), "files", { value: [file] });
  await window.uploadCV();
  await flush();
  assert.equal(document.getElementById("analysis-screen").hidden, false);
  assert.equal(document.getElementById("home-screen").hidden, true);
});

test("uploading a CV after goToVacancySearch lands on the title screen (not home)", async () => {
  const dom = loadApp({
    fetchImpl: defaultFetchMock({
      "/api/cv-status": () => ({ has_cv: false, lang: "en" }),
      "/api/upload-cv": () => ({ saved: true }),
    }),
  });
  await flush();
  const { document, window } = dom.window;
  window.goToVacancySearch();
  const file = new window.File(["cv text"], "resume.pdf", { type: "application/pdf" });
  Object.defineProperty(document.getElementById("cv_file"), "files", { value: [file] });
  await window.uploadCV();
  await flush();
  assert.equal(document.getElementById("title-screen").hidden, false);
  assert.equal(document.getElementById("home-screen").hidden, true);
});

// ── Session-wide vacancy-search cap (closes the per-title reset loophole) ─

test("the 3-search cap is session-wide: changing job titles does not reset it", async () => {
  let searchCalls = 0;
  const dom = loadApp({
    fetchImpl: defaultFetchMock({
      "/api/cv-status": () => ({ has_cv: true, lang: "en" }),
      "/api/search": () => {
        searchCalls += 1;
        return { vacancies: [{ title: "Data Analyst", company: `Co${searchCalls}`, location: "Remote", url: "https://x", summary: "..." }] };
      },
    }),
  });
  await flush();
  const { document, window } = dom.window;

  window.pickTitle("Data Analyst");
  document.getElementById("location").value = "Remote";
  await window.search();
  await window.search();
  await window.search();
  assert.equal(searchCalls, 3, "3 searches should have hit the API");

  // Previously, picking a NEW title reset the counter to 0, letting users
  // search forever by cycling titles. It must not anymore.
  window.pickTitle("Backend Engineer");
  await window.search();
  assert.equal(searchCalls, 3, "a 4th search, even under a brand-new title, must not hit the API");
});

test("liking a vacancy hides the like/search-again/carousel/analyze-CV decision block, leaving only the current step's buttons", async () => {
  const dom = loadApp({
    fetchImpl: defaultFetchMock({
      "/api/cv-status": () => ({ has_cv: true, lang: "en" }),
      "/api/search": () => ({ vacancies: [{ title: "Data Analyst", company: "Acme", location: "Remote", url: "https://x", summary: "..." }] }),
    }),
  });
  await flush();
  const { document, window } = dom.window;
  window.pickTitle("Data Analyst");
  await window.search();

  assert.equal(document.getElementById("vacancy-decision").hidden, false);
  window.likeVacancy();
  assert.equal(document.getElementById("vacancy-decision").hidden, true,
    "the like-it/search-again/carousel-nav block must disappear once the user commits to a vacancy");
  assert.match(document.getElementById("action-area").innerHTML, /checkFit\(\)/,
    "the current step's buttons (apply/check fit) must be visible");
});

test("hitting the search cap shows a call-to-action into the paid analysis flow", async () => {
  const dom = loadApp({
    fetchImpl: defaultFetchMock({
      "/api/cv-status": () => ({ has_cv: true, lang: "en" }),
      "/api/search": () => ({ vacancies: [{ title: "Data Analyst", company: "Acme", location: "Remote", url: "https://x", summary: "..." }] }),
    }),
  });
  await flush();
  const { document, window } = dom.window;
  window.pickTitle("Data Analyst");
  await window.search();
  await window.search();
  await window.search();
  const resultHtml = document.getElementById("result").innerHTML;
  assert.match(resultHtml, /goToAnalysis\(\)/, "the cap-hit card must offer a button into the analysis flow");
});

// ── Double back-button fix on the applications detail view ──────────────

test("opening an application detail hides the screen-level back button; closing restores it", async () => {
  const dom = loadApp({
    fetchImpl: defaultFetchMock({
      "/api/cv-status": () => ({ has_cv: true, lang: "en" }),
      "/api/applications": () => ({
        applications: [{ id: 1, title: "Data Analyst", company: "Acme", location: "Remote", url: "https://x", match_score: 80, status: "applied", created_at: new Date().toISOString() }],
      }),
    }),
  });
  await flush();
  const { document, window } = dom.window;

  await window.showApplications();
  assert.equal(document.getElementById("btn-applications-back").hidden, false);

  window.openApplicationDetail(1);
  assert.equal(document.getElementById("btn-applications-back").hidden, true,
    "only the detail view's own back button should show while viewing one application");
  assert.equal(document.getElementById("application-detail").hidden, false);

  window.closeApplicationDetail();
  assert.equal(document.getElementById("btn-applications-back").hidden, false);
  assert.equal(document.getElementById("application-detail").hidden, true);
});

// ── Roadmap: items append instead of replacing each other ───────────────

const FAKE_ANALYSIS = {
  limit_reached: false, remaining: 2, quota: 3, jd_text: "resolved jd text",
  ats: { score: 70, matched: ["SQL"], missing: ["dbt"], verdict: "Decent." },
  xyz: { passing: [], failing: [], rewrites: [] },
  tools: { SQL: "strong" },
  level: { assessment: "Junior", reasoning: "Some production experience." },
};

async function runAnalysis(window, document) {
  document.getElementById("jd_text").value = "x".repeat(150);
  await window.analyzeCV();
}

const ROADMAP_RESPONSES = {
  1: { title: "CV Fixes", fixes: [{ issue: "x", before: "", after: "y" }], is_last: false },
  2: { title: "Phone Screen Prep", text: "### Phone Screen Strategy\nSay hi.", is_last: false },
  3: { title: "Technical Interview Prep", text: "### Technical Interview Prep\nStudy SQL.", is_last: false },
  4: { title: "Target Companies", text: "### Target Companies\nAcme.", is_last: true },
};

function loadRoadmapDom() {
  let fetchCount = 0;
  const dom = loadApp({
    fetchImpl: defaultFetchMock({
      "/api/cv-status": () => ({ has_cv: true, lang: "en" }),
      "/api/cv-jd-analysis": () => FAKE_ANALYSIS,
      "/api/roadmap-item": (body) => { fetchCount += 1; return ROADMAP_RESPONSES[body.item]; },
      "/api/quota-status": () => ({ remaining: 1, quota: 3, price_per_check_tiyin: 1000000 }),
    }),
  });
  return { dom, getFetchCount: () => fetchCount };
}

test("the roadmap shows one item at a time (carousel), not all of them stacked", async () => {
  const { dom } = loadRoadmapDom();
  await flush();
  const { document, window } = dom.window;
  window.goToAnalysis();
  await runAnalysis(window, document);

  window.startRoadmap();
  await flush();
  const area = document.getElementById("roadmap-area");
  assert.match(area.innerHTML, /CV Fixes/);
  assert.ok(!area.innerHTML.includes("Phone Screen Strategy"), "later items must not be visible yet");
  assert.match(area.innerHTML, /1 \/ 4/, "counter should show step 1 of 4 for a Junior roadmap");
});

test("clicking Next fetches and shows the next item, replacing the previous one", async () => {
  const { dom } = loadRoadmapDom();
  await flush();
  const { document, window } = dom.window;
  window.goToAnalysis();
  await runAnalysis(window, document);
  window.startRoadmap();
  await flush();

  window.loadRoadmapItem(2);
  await flush();
  const area = document.getElementById("roadmap-area");
  assert.match(area.innerHTML, /Phone Screen Strategy/);
  assert.ok(!area.innerHTML.includes("CV Fixes"), "item 1 should no longer be shown once on item 2");
  assert.match(area.innerHTML, /2 \/ 4/);
});

test("Prev returns to an already-fetched item instantly, without a new API call", async () => {
  const { dom, getFetchCount } = loadRoadmapDom();
  await flush();
  const { document, window } = dom.window;
  window.goToAnalysis();
  await runAnalysis(window, document);
  window.startRoadmap();
  await flush();
  window.loadRoadmapItem(2);
  await flush();
  assert.equal(getFetchCount(), 2, "items 1 and 2 should each have been fetched once");

  window.loadRoadmapItem(1); // Prev
  await flush();
  const area = document.getElementById("roadmap-area");
  assert.match(area.innerHTML, /CV Fixes/);
  assert.match(area.innerHTML, /1 \/ 4/);
  assert.equal(getFetchCount(), 2, "going back to item 1 must be served from cache, not re-fetched");

  window.loadRoadmapItem(2); // forward again - also cached
  await flush();
  assert.equal(getFetchCount(), 2, "revisiting item 2 must also be served from cache");
});

test("Prev is disabled on the first item; Next is disabled on the last", async () => {
  const { dom } = loadRoadmapDom();
  await flush();
  const { document, window } = dom.window;
  window.goToAnalysis();
  await runAnalysis(window, document);
  window.startRoadmap();
  await flush();

  const navButtons = () => document.getElementById("roadmap-area").querySelectorAll(".nav-row button");
  assert.equal(navButtons()[0].disabled, true, "Prev must be disabled on item 1");
  assert.equal(navButtons()[1].disabled, false);

  window.loadRoadmapItem(2);
  await flush();
  window.loadRoadmapItem(3);
  await flush();
  window.loadRoadmapItem(4);
  await flush(5);
  assert.equal(navButtons()[0].disabled, false, "Prev must be enabled once past item 1");
  assert.equal(navButtons()[1].disabled, true, "Next must be disabled on the last item");
});

// ── Post-roadmap flow: no more dead end ──────────────────────────────────

test("finishing the roadmap with checks remaining offers 'analyze another job'", async () => {
  const dom = loadApp({
    fetchImpl: defaultFetchMock({
      "/api/cv-status": () => ({ has_cv: true, lang: "en" }),
      "/api/cv-jd-analysis": () => FAKE_ANALYSIS,
      "/api/roadmap-item": () => ({ title: "Target Companies", text: "Acme.", is_last: true }),
      "/api/quota-status": () => ({ remaining: 2, quota: 3, price_per_check_tiyin: 1000000 }),
    }),
  });
  await flush();
  const { document, window } = dom.window;
  window.goToAnalysis();
  await runAnalysis(window, document);
  window.startRoadmap();
  await flush(6);

  const area = document.getElementById("roadmap-area");
  assert.match(area.innerHTML, /Analyze another job/);
  assert.equal(document.getElementById("nav-checks").textContent, "🎫 2/3", "header badge should refresh after roadmap completion");
});

test("finishing the roadmap at zero checks routes straight into buying more", async () => {
  const dom = loadApp({
    fetchImpl: defaultFetchMock({
      "/api/cv-status": () => ({ has_cv: true, lang: "en" }),
      "/api/cv-jd-analysis": () => FAKE_ANALYSIS,
      "/api/roadmap-item": () => ({ title: "Target Companies", text: "Acme.", is_last: true }),
      "/api/quota-status": () => ({ remaining: 0, quota: 3, price_per_check_tiyin: 1000000 }),
    }),
  });
  await flush();
  const { document, window } = dom.window;
  window.goToAnalysis();
  await runAnalysis(window, document);
  window.startRoadmap();
  await flush(6);

  assert.ok(document.getElementById("buy-checks-box"), "a buy-checks box should render when out of free checks");
});

// ── Checks-remaining visibility in the header ────────────────────────────

test("a successful analysis updates the header checks badge", async () => {
  const dom = loadApp({
    fetchImpl: defaultFetchMock({
      "/api/cv-status": () => ({ has_cv: true, lang: "en" }),
      "/api/cv-jd-analysis": () => FAKE_ANALYSIS,
    }),
  });
  await flush();
  const { document, window } = dom.window;
  window.goToAnalysis();
  await runAnalysis(window, document);
  assert.equal(document.getElementById("nav-checks").textContent, "🎫 2/3");
});

test("hitting the free-check limit during analysis shows the buy-checks flow, not the results", async () => {
  const dom = loadApp({
    fetchImpl: defaultFetchMock({
      "/api/cv-status": () => ({ has_cv: true, lang: "en" }),
      "/api/cv-jd-analysis": () => ({ limit_reached: true, remaining: 0, quota: 3 }),
    }),
  });
  await flush();
  const { document, window } = dom.window;
  window.goToAnalysis();
  await runAnalysis(window, document);
  assert.ok(document.getElementById("buy-checks-box"), "should route straight to buying more checks");
  assert.equal(document.getElementById("jd-input-box").hidden, true);
});
