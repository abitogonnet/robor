import sqlite3
from math import ceil
from datetime import datetime, date, time, timedelta
from pathlib import Path
from app.utils import SLOT_TIMES, MODULE_CAPACITY, modules_required, slot_persons_for_group, is_valid_visit_day, is_valid_visit_time, WORK_END, SLOT_MINUTES, format_time, format_date
from app.integrations.web_base import create_visit_in_web, query_availability
from app.sessions import get_db_path

VISITS_TABLE = "CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY AUTOINCREMENT, phone TEXT, visit_date TEXT, visit_time TEXT, people_count INTEGER, booking_id TEXT, created_at TEXT)"


def get_connection():
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables():
    with get_connection() as conn:
        conn.execute(VISITS_TABLE)


ensure_tables()


def parse_date(value: str) -> date:
    return datetime.fromisoformat(value).date()


def parse_time(value: str) -> time:
    try:
        return time.fromisoformat(value)
    except ValueError:
        return datetime.fromisoformat(value).time()


def booked_slots_for_day(visit_date: date) -> dict[time, int]:
    with get_connection() as conn:
        rows = conn.execute("SELECT visit_time, people_count FROM visits WHERE visit_date = ?", (visit_date.isoformat(),)).fetchall()
    totals: dict[time, int] = {}
    for visit_time_str, people_count in rows:
        slot_time = parse_time(visit_time_str)
        total = totals.get(slot_time, 0) + people_count
        totals[slot_time] = total
    return totals


def check_availability(visit_date: date, visit_time: time, people_count: int) -> bool:
    if not is_valid_visit_day(visit_date):
        return False
    if not is_valid_visit_time(visit_time):
        return False

    required_modules = modules_required(people_count)
    start_index = SLOT_TIMES.index(visit_time)
    if start_index + required_modules > len(SLOT_TIMES):
        return False

    remote_availability = query_availability(visit_date, visit_time, required_modules, people_count)
    if remote_availability is False:
        return False
    if remote_availability is True:
        return True

    booked = booked_slots_for_day(visit_date)
    reserved = slot_persons_for_group(people_count)
    for offset, slot_index in enumerate(range(start_index, start_index + required_modules)):
        slot = SLOT_TIMES[slot_index]
        if booked.get(slot, 0) + reserved[offset] > MODULE_CAPACITY:
            return False
    end_slot = SLOT_TIMES[start_index + required_modules - 1]
    return end_slot < WORK_END


def find_alternatives(visit_date: date, people_count: int) -> list[time]:
    available: list[time] = []
    for slot in SLOT_TIMES:
        if check_availability(visit_date, slot, people_count):
            available.append(slot)
    return available


def create_visit(phone: str, visit_date: date, visit_time: time, people_count: int) -> dict[str, str]:
    if not check_availability(visit_date, visit_time, people_count):
        raise ValueError("No hay disponibilidad para ese horario y cantidad de personas.")
    booking = create_visit_in_web(phone, visit_date, visit_time, people_count)
    created_at = datetime.now().isoformat()
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO visits(phone, visit_date, visit_time, people_count, booking_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (phone, visit_date.isoformat(), visit_time.isoformat(), people_count, booking["booking_id"], created_at),
        )
    return booking


def visits_for_reminder_window() -> list[dict[str, str]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT phone, visit_date, visit_time FROM visits"
        ).fetchall()
    reminders = []
    for phone, visit_date_str, visit_time_str in rows:
        visit_date = parse_date(visit_date_str)
        visit_time = parse_time(visit_time_str)
        visit_dt = datetime.combine(visit_date, visit_time)
        reminders.append({"phone": phone, "visit_datetime": visit_dt, "visit_time": visit_time})
    return reminders
