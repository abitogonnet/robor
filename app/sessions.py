import os
import sqlite3
from pathlib import Path
from app.models import SessionData, BotState, Intent
from app.utils import format_date, format_time


def get_db_path() -> Path:
    configured = os.environ.get("BOT_DB_PATH")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parent.parent / "bot_data.sqlite"

DB_PATH = get_db_path()

CREATE_TABLES = [
    "CREATE TABLE IF NOT EXISTS sessions (phone TEXT PRIMARY KEY, state TEXT, intent TEXT, event_date TEXT, visit_day TEXT, visit_time TEXT, people_count INTEGER, link_sent INTEGER, visit_created INTEGER)",
    "CREATE TABLE IF NOT EXISTS reminders_sent (phone TEXT, reminder_type TEXT, reminder_time TEXT, PRIMARY KEY(phone, reminder_type, reminder_time))",
]


def get_connection():
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables():
    with get_connection() as conn:
        for statement in CREATE_TABLES:
            conn.execute(statement)


ensure_tables()


def serialize_session(data: SessionData) -> dict:
    return {
        "phone": data.phone,
        "state": data.state.value,
        "intent": data.intent.value,
        "event_date": format_date(data.event_date) if data.event_date else None,
        "visit_day": format_date(data.visit_day) if data.visit_day else None,
        "visit_time": format_time(data.visit_time) if data.visit_time else None,
        "people_count": data.people_count,
        "link_sent": int(data.link_sent),
        "visit_created": int(data.visit_created),
    }


def deserialize_session(row) -> SessionData:
    from datetime import datetime
    from app.utils import parse_iso_date, parse_iso_time

    return SessionData(
        phone=row["phone"],
        state=BotState(row["state"]),
        intent=Intent(row["intent"]),
        event_date=parse_iso_date(row["event_date"]) if row["event_date"] else None,
        visit_day=parse_iso_date(row["visit_day"]) if row["visit_day"] else None,
        visit_time=parse_iso_time(row["visit_time"] ) if row["visit_time"] else None,
        people_count=row["people_count"],
        link_sent=bool(row["link_sent"]),
        visit_created=bool(row["visit_created"]),
    )


def get_session(phone: str) -> SessionData:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE phone = ?", (phone,)).fetchone()
        if not row:
            return SessionData(phone=phone)
        return deserialize_session(row)


def save_session(session: SessionData) -> None:
    data = serialize_session(session)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO sessions(phone, state, intent, event_date, visit_day, visit_time, people_count, link_sent, visit_created) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(phone) DO UPDATE SET state=excluded.state, intent=excluded.intent, event_date=excluded.event_date, visit_day=excluded.visit_day, visit_time=excluded.visit_time, people_count=excluded.people_count, link_sent=excluded.link_sent, visit_created=excluded.visit_created",
            (
                data["phone"],
                data["state"],
                data["intent"],
                data["event_date"],
                data["visit_day"],
                data["visit_time"],
                data["people_count"],
                data["link_sent"],
                data["visit_created"],
            ),
        )


def record_reminder(phone: str, reminder_type: str, reminder_time: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO reminders_sent(phone, reminder_type, reminder_time) VALUES (?, ?, ?)",
            (phone, reminder_type, reminder_time),
        )


def has_reminder(phone: str, reminder_type: str, reminder_time: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM reminders_sent WHERE phone = ? AND reminder_type = ? AND reminder_time = ?",
            (phone, reminder_type, reminder_time),
        ).fetchone()
        return row is not None
