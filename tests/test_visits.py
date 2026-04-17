import importlib
from datetime import date, time

import pytest

@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("BOT_DB_PATH", str(tmp_path / "bot_data.sqlite"))
    import app.sessions, app.services.visits
    importlib.reload(app.sessions)
    importlib.reload(app.services.visits)


def test_module_capacity():
    from app.utils import modules_required
    assert modules_required(1) == 1
    assert modules_required(2) == 1
    assert modules_required(3) == 2
    assert modules_required(4) == 2
    assert modules_required(5) == 3


def test_overflow_of_schedule():
    from app.services.visits import check_availability
    assert not check_availability(date(2026, 6, 15), time(19, 30), 3)
    assert check_availability(date(2026, 6, 15), time(19, 30), 2)


def test_reject_end_of_day_slot():
    from app.services.visits import check_availability
    assert not check_availability(date(2026, 6, 15), time(19, 30), 3)
    assert not check_availability(date(2026, 6, 15), time(20, 0), 1)


def test_create_visit_updates_availability():
    from app.services.visits import create_visit, check_availability
    booking = create_visit("+5491111111111", date(2026, 6, 15), time(17, 0), 2)
    assert "booking_id" in booking
    assert not check_availability(date(2026, 6, 15), time(17, 0), 2)
