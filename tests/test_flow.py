import importlib

import pytest

@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    monkeypatch.setenv("BOT_DB_PATH", str(tmp_path / "bot_data.sqlite"))
    import app.sessions, app.services.visits
    importlib.reload(app.sessions)
    importlib.reload(app.services.visits)


def test_full_visit_flow():
    from app.bot import handle_incoming_message
    from app.sessions import get_session

    phone = "+5491111111122"
    response1 = handle_incoming_message(phone, "Hola, quisiera reservar una visita")
    assert "reservar tu visita" in response1.lower()

    response2 = handle_incoming_message(phone, "2026-06-16")
    assert "qué hora" in response2.lower()

    response3 = handle_incoming_message(phone, "17:30")
    assert "cuántas personas" in response3.lower()

    response4 = handle_incoming_message(phone, "3 personas")
    assert "confirmo la visita" in response4.lower()

    response5 = handle_incoming_message(phone, "si")
    assert "reserva confirmada" in response5.lower()

    session = get_session(phone)
    from app.models import BotState

    assert session.visit_created
    assert session.state == BotState.inicio
