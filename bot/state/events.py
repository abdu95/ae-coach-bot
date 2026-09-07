"""events table: shared event log with vacancy-webapp's app/db/events.py."""

import json

import state


def log_event(telegram_id: int, event_type: str, metadata: dict | None = None) -> None:
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (telegram_id, event_type, metadata) VALUES (%s, %s, %s)",
                (telegram_id, event_type, json.dumps(metadata) if metadata is not None else None),
            )
    finally:
        state._pool.putconn(conn)


def event_stats(event_types: list[str]) -> dict[str, tuple[int, int]]:
    """Returns {event_type: (total_count, unique_users)} for each requested type."""
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                SELECT event_type, count(*), count(DISTINCT telegram_id)
                FROM events
                WHERE event_type = ANY(%s)
                GROUP BY event_type
            """, (event_types,))
            rows = {row[0]: (row[1], row[2]) for row in cur.fetchall()}
    finally:
        state._pool.putconn(conn)
    return {et: rows.get(et, (0, 0)) for et in event_types}
