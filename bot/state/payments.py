"""orders table: shared with vacancy-webapp's app/db/payments.py and read
by the separate payme-webhook service."""

import state


def get_or_create_order(telegram_id: int, amount: int, package: str) -> int:
    """Reuses an existing pending order for this user+package instead of
    creating a new row every time the limit-reached message is shown, so
    repeated prompts don't pile up dead `orders` rows. Refreshes the amount
    on reuse so a reused order always matches the currently-configured
    price — otherwise a stale pending order from before a price change
    would disagree with the checkout link built from the new price,
    and Payme would reject the transaction as an amount mismatch."""
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                UPDATE orders SET amount = %s
                WHERE id = (
                    SELECT id FROM orders
                    WHERE telegram_id = %s AND package = %s AND state = 'pending'
                    ORDER BY created_at DESC LIMIT 1
                )
                RETURNING id
            """, (amount, telegram_id, package))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute("""
                INSERT INTO orders (telegram_id, amount, package)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (telegram_id, amount, package))
            return cur.fetchone()[0]
    finally:
        state._pool.putconn(conn)


def payment_stats() -> dict:
    """Reads directly from `orders` (state='paid') rather than an event
    log, so it's accurate from day one - covers every payment ever made,
    including ones from before any payment-specific event existed."""
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                SELECT count(*), count(DISTINCT telegram_id), coalesce(sum(amount), 0)
                FROM orders WHERE state = 'paid'
            """)
            count, unique_payers, total_tiyin = cur.fetchone()
    finally:
        state._pool.putconn(conn)
    return {"count": count, "unique_payers": unique_payers, "total_uzs": total_tiyin // 100}
