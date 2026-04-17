import importlib
from datetime import datetime, timedelta, date

import pytest

@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("BOT_DB_PATH", str(tmp_path / "bot_data.sqlite"))
    import app.sessions, app.services.visits
    importlib.reload(app.sessions)
    importlib.reload(app.services.visits)


def test_visit_reminder_sends_once(monkeypatch):
    from datetime import datetime
    from app.services.visits import create_visit
    from app.services.reminders import send_visit_reminders

    phone = "+5491111111111"
    now = datetime(2026, 6, 16, 11, 0)
    visit_date = now.date()
    visit_time = visit_date and datetime(2026, 6, 16, 17, 0).time()
    create_visit(phone, visit_date, visit_time, 2)

    sent_first = send_visit_reminders(now=now)
    sent_second = send_visit_reminders(now=now)
    assert sent_first == 1
    assert sent_second == 0


def test_return_reminder_deprecated(monkeypatch):
    from app.services.reminders import send_return_reminders
    import app.integrations.internal_base as internal_base

    def fake_returns(query_date):
        return [{"phone": "+5491111111111"}]
    monkeypatch.setattr(internal_base, "get_returns_for_date", fake_returns)
    sent = send_return_reminders(date(2026, 6, 15))
    assert sent == 1
    sent_again = send_return_reminders(date(2026, 6, 15))
    assert sent_again == 0
