import os
from datetime import date
from app.integrations.db import get_connection, has_db

INTERNAL_DB_URL_ENV = "RENDER_INTERNAL_DB_URL"
INTERNAL_RETURNS_TABLE = os.environ.get("RENDER_INTERNAL_RETURNS_TABLE", "returns")


def get_returns_for_date(query_date: date) -> list[dict[str, str]]:
    if not has_db(INTERNAL_DB_URL_ENV):
        return []

    query = f"SELECT phone FROM {INTERNAL_RETURNS_TABLE} WHERE return_date = %s"
    results = []
    with get_connection(INTERNAL_DB_URL_ENV) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (query_date.isoformat(),))
        rows = cursor.fetchall()
        for row in rows:
            results.append({"phone": row[0]})
    return results
