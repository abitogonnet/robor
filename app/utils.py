from datetime import datetime, date, time, timedelta
from math import ceil

WORK_START = time(17, 0)
WORK_END = time(20, 0)
SLOT_MINUTES = 30
SLOT_TIMES = [
    time(17, 0),
    time(17, 30),
    time(18, 0),
    time(18, 30),
    time(19, 0),
    time(19, 30),
]
MODULE_CAPACITY = 2
HOLIDAYS = {
    date(2026, 1, 1),
    date(2026, 12, 25),
}


def parse_iso_date(text: str) -> date | None:
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    return None


def parse_iso_time(text: str) -> time | None:
    normalized = text.strip().lower().replace("h", ":").replace(" ", "")
    for fmt in ["%H:%M", "%H%M"]:
        try:
            return datetime.strptime(normalized, fmt).time()
        except ValueError:
            continue
    return None


def is_valid_visit_day(value: date) -> bool:
    return value.weekday() < 5 and value not in HOLIDAYS


def is_valid_visit_time(value: time) -> bool:
    return value in SLOT_TIMES


def modules_required(people_count: int) -> int:
    return ceil(people_count / MODULE_CAPACITY)


def slot_persons_for_group(people_count: int) -> list[int]:
    full_modules = people_count // MODULE_CAPACITY
    remainder = people_count % MODULE_CAPACITY
    slots = [MODULE_CAPACITY] * full_modules
    if remainder:
        slots.append(remainder)
    return slots


def add_slots(start: time, count: int) -> list[time]:
    current = datetime.combine(date.today(), start)
    slots = []
    for _ in range(count):
        if current.time() not in SLOT_TIMES:
            break
        slots.append(current.time())
        current += timedelta(minutes=SLOT_MINUTES)
    return slots


def format_time(value: time) -> str:
    return value.strftime("%H:%M")


def format_date(value: date) -> str:
    return value.strftime("%Y-%m-%d")


def now() -> datetime:
    return datetime.now()


def six_hours_before(visit_datetime: datetime) -> datetime:
    return visit_datetime - timedelta(hours=6)
