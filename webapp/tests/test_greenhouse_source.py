import asyncio
import sys
import unittest.mock as mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import greenhouse_source as gs  # noqa: E402

FAKE_JOBS_BY_COMPANY = {
    "stripe": [
        {"title": "Senior Analytics Engineer", "absolute_url": "https://stripe.com/jobs/1",
         "location": {"name": "Remote - US"}, "content": "&lt;p&gt;Build things.&lt;/p&gt;",
         "updated_at": "2026-09-01T00:00:00Z"},
        {"title": "Engineering Manager, Payments", "absolute_url": "https://stripe.com/jobs/2",
         "location": {"name": "San Francisco"}, "content": "&lt;p&gt;Manage a team.&lt;/p&gt;",
         "updated_at": "2026-09-04T00:00:00Z"},
    ],
    "airbnb": [
        {"title": "Data Analyst, Trust", "absolute_url": "https://airbnb.com/jobs/1",
         "location": {"name": "Dublin, Ireland"}, "content": "&lt;p&gt;Analyze trust data.&lt;/p&gt;",
         "updated_at": "2026-09-02T00:00:00Z"},
    ],
    "reddit": [
        {"title": "Senior Analytics Engineer", "absolute_url": "https://reddit.com/jobs/1",
         "location": {"name": "Remote"}, "content": "Reddit role.", "updated_at": "2026-09-03T00:00:00Z"},
        {"title": "Analytics Engineer II", "absolute_url": "https://reddit.com/jobs/2",
         "location": {"name": "SF"}, "content": "Reddit role 2.", "updated_at": "2026-09-06T00:00:00Z"},
    ],
    "coinbase": [
        {"title": "Staff Analytics Engineer", "absolute_url": "https://coinbase.com/jobs/1",
         "location": {"name": "Remote"}, "content": "Coinbase role.", "updated_at": "2026-09-04T00:00:00Z"},
    ],
}


async def fake_fetch(client, slug):
    return FAKE_JOBS_BY_COMPANY.get(slug, [])


async def main():
    with mock.patch.object(gs, "COMPANIES", ["stripe", "airbnb"]), \
         mock.patch.object(gs, "_fetch_company_jobs", new=fake_fetch):

        # Test 1: strict match wins over a loose "Engineer" substring match
        # ("Engineering Manager" should NOT beat "Analytics Engineer" here)
        result = await gs.search_vacancies("Analytics Engineer", "Any", "Any", "Any")
        assert len(result) == 1, result
        assert result[0]["title"] == "Senior Analytics Engineer", result
        assert result[0]["company"] == "Stripe"
        print("PASS: strict all-words match preferred over weak substring match")

        # Test 2: word-boundary matching - "Engineer" must not match inside "Engineering"
        result2 = await gs.search_vacancies("Zzz Engineer Zzz", "Any", "Any", "Any")
        # only tier-1 (single word "engineer") matches exist here: both Stripe jobs
        # qualify via "Engineering"->no (boundary blocks it) but "Senior Analytics
        # Engineer" contains the standalone word "Engineer" - confirm no false
        # positive from "Engineering Manager, Payments"
        assert result2[0]["title"] != "Engineering Manager, Payments", result2
        print("PASS: word-boundary matching excludes 'Engineering' from an 'Engineer' query")

        # Test 3: location filter
        result3 = await gs.search_vacancies("Data Analyst", "Dublin", "Any", "Any")
        assert len(result3) == 1, result3
        assert result3[0]["company"] == "Airbnb"
        print("PASS: location filter narrows to the matching posting")

        # Test 4: remote work_setup filter excludes non-remote postings
        result4 = await gs.search_vacancies("Analytics Engineer", "Any", "remote", "Any")
        assert result4[0]["location"] == "Remote - US", result4
        print("PASS: work_setup=remote filters to remote-only postings")

        # Test 5: seen_companies excludes a company entirely
        result5 = await gs.search_vacancies("Analytics Engineer", "Any", "Any", "Any", seen_companies=["Stripe"])
        assert result5 == [], result5
        print("PASS: seen_companies excludes that company from candidates")

        # Test 6: HTML content is unescaped and stripped
        result6 = await gs.search_vacancies("Analytics Engineer", "Any", "Any", "Any")
        assert "<" not in result6[0]["summary"] and "&lt;" not in result6[0]["summary"], result6
        assert result6[0]["summary"] == "Build things.", result6
        print("PASS: HTML content is properly unescaped and tag-stripped")

        # Test 7: no match anywhere returns an empty list, not an error
        result7 = await gs.search_vacancies("Nonexistent Zzzrole", "Any", "Any", "Any")
        assert result7 == [], result7
        print("PASS: no match returns an empty list")

    # Test 8: multi-result - up to max_results, one per company, most-recent-first within tier
    with mock.patch.object(gs, "COMPANIES", ["stripe", "airbnb", "reddit", "coinbase"]), \
         mock.patch.object(gs, "_fetch_company_jobs", new=fake_fetch):
        result8 = await gs.search_vacancies("Analytics Engineer", "Any", "Any", "Any")
        assert len(result8) == 3, result8  # capped at default max_results=3
        companies = [r["company"] for r in result8]
        assert len(companies) == len(set(companies)), result8  # one per company, no dupes
        # Reddit has 2 matching jobs (2026-09-03 and 2026-09-06) - the newer one should win
        reddit_result = next(r for r in result8 if r["company"] == "Reddit")
        assert reddit_result["title"] == "Analytics Engineer II", result8
        print("PASS: multi-result search returns up to max_results, one per company, newest-per-company")

        result8b = await gs.search_vacancies("Analytics Engineer", "Any", "Any", "Any", max_results=2)
        assert len(result8b) == 2, result8b
        print("PASS: max_results is respected when lower than the available match count")

    print("\nALL GREENHOUSE SOURCE CHECKS PASSED")


asyncio.run(main())
