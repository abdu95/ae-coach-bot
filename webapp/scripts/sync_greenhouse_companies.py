"""
Syncs webapp/greenhouse_companies.csv into the `greenhouse_companies`
table: upserts every row in the CSV (active=true), and deactivates
(active=false, never deletes - keeps history of what was tried) any DB
row whose slug is no longer in the CSV.

Run this after editing the CSV to add/remove/rename a verified
company. Takes effect within webapp/db.py's get_active_companies()
cache TTL (10 minutes) - no deploy needed.

Usage:
    DATABASE_URL=postgresql://... python3 scripts/sync_greenhouse_companies.py [path/to/csv]

If no path is given, defaults to greenhouse_companies.csv next to this
script's parent directory (webapp/greenhouse_companies.csv).
"""

import csv
import os
import sys

import psycopg2

DEFAULT_CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "greenhouse_companies.csv")


def main() -> None:
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV_PATH
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("DATABASE_URL not set")

    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"No rows found in {csv_path}")

    conn = psycopg2.connect(dsn)
    try:
        with conn, conn.cursor() as cur:
            for row in rows:
                cur.execute(
                    """
                    INSERT INTO greenhouse_companies (slug, display_name, domain, active)
                    VALUES (%s, %s, %s, true)
                    ON CONFLICT (slug) DO UPDATE
                    SET display_name = EXCLUDED.display_name,
                        domain = EXCLUDED.domain,
                        active = true
                    """,
                    (row["company_slug"], row["display_name"], row["domain"]),
                )
            slugs_in_csv = [row["company_slug"] for row in rows]
            cur.execute(
                """
                UPDATE greenhouse_companies SET active = false
                WHERE slug != ALL(%s) AND active = true
                """,
                (slugs_in_csv,),
            )
            deactivated = cur.rowcount
        print(f"Synced {len(rows)} companies from {csv_path}; deactivated {deactivated} no-longer-listed rows.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
