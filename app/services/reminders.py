from datetime import datetime, date, timedelta
from app.services.visits import visits_for_reminder_window
from app.sessions import has_reminder, record_reminder
from app.integrations.whatsapp_api import send_message
from app.utils import six_hours_before

VISIT_REMINDER_TYPE = "visit_6h"
RETURN_REMINDER_TYPE = "return_same_day"


def send_visit_reminders(now: datetime | None = None) -> int:
    now = now or datetime.now()
    reminders = visits_for_reminder_window()
    sent = 0
    window_limit = now + timedelta(minutes=1)
    for entry in reminders:
        phone = entry["phone"]
        visit_dt = entry["visit_datetime"]
        reminder_time = six_hours_before(visit_dt)
        if not (now <= reminder_time < window_limit):
            continue
        reminder_key = reminder_time.isoformat()
        if has_reminder(phone, VISIT_REMINDER_TYPE, reminder_key):
            continue
        text = f"Te recordamos tu visita de hoy a las {visit_dt.strftime('%H:%M')} en ABITO."
        send_message(channel="whatsapp", user=phone, text=text)
        record_reminder(phone, VISIT_REMINDER_TYPE, reminder_key)
        sent += 1
    return sent


def send_return_reminders(query_date: date) -> int:
    from app.integrations.internal_base import get_returns_for_date
    returns = get_returns_for_date(query_date)
    sent = 0
    for record in returns:
        phone = record.get("phone")
        if not phone:
            continue
        reminder_id = f"{query_date.isoformat()}_{RETURN_REMINDER_TYPE}_{phone}"
        if has_reminder(phone, RETURN_REMINDER_TYPE, reminder_id):
            continue
        text = "Recordatorio: hoy es día de devolución. Si necesitás asistencia, respondé este mensaje."
        send_message(channel="whatsapp", user=phone, text=text)
        record_reminder(phone, RETURN_REMINDER_TYPE, reminder_id)
        sent += 1
    return sent
