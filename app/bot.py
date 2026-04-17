import re
from datetime import datetime, date, time
from app.models import Intent, BotState
from app.sessions import get_session, save_session
from app.services.catalog import describe_price, catalog_link
from app.services.visits import check_availability, create_visit, find_alternatives
from app.utils import parse_iso_date, parse_iso_time, is_valid_visit_day, is_valid_visit_time, format_date, format_time
from app.models import Channel

PRICING_KEYWORDS = ["precio", "valor", "costo", "cuesta"]
VISIT_KEYWORDS = ["visita", "reservar", "reserva", "agenda"]
HUMAN_KEYWORDS = ["humano", "atención", "ayuda", "operador"]


def parse_message_payload(payload: dict) -> tuple[str, str, str]:
    if "channel" not in payload or "phone" not in payload or "text" not in payload:
        raise ValueError("Payload inválido. Se requiere channel, phone y text.")
    channel = payload["channel"].lower()
    if channel not in {Channel.whatsapp.value, Channel.instagram.value}:
        raise ValueError("Canal no soportado.")
    return channel, payload["phone"], payload["text"].strip()


def detect_intent(text: str) -> Intent:
    lower = text.lower()
    if any(word in lower for word in HUMAN_KEYWORDS):
        return Intent.humano
    if any(word in lower for word in PRICING_KEYWORDS):
        return Intent.precio
    if any(word in lower for word in VISIT_KEYWORDS):
        return Intent.visita
    if any(word in lower for word in ["hola", "buenos", "buenas", "hi"]):
        return Intent.saludo
    return Intent.desconocido


def handle_incoming_message(phone: str, text: str, channel: str = Channel.whatsapp.value) -> str:
    session = get_session(phone)
    intent = detect_intent(text)
    session.intent = intent

    if intent == Intent.humano:
        session.state = BotState.derivado_humano
        save_session(session)
        return "Si querés lo seguimos por atención humana."

    if session.state == BotState.inicio:
        if intent == Intent.precio:
            response = describe_price(text)
            response += f"\nSi querés, también podés reservar una visita en: {catalog_link()}"
            save_session(session)
            return response

        if intent == Intent.visita or intent == Intent.saludo:
            session.state = BotState.esperando_dia_visita
            session.link_sent = True
            save_session(session)
            return (
                f"Podés reservar tu visita desde acá: {catalog_link()}\n" 
                "Si preferís, te ayudo a reservar por WhatsApp. ¿Para qué día te gustaría venir?"
            )

        return "Hola, soy el bot de ABITO. Puedo ayudarte con precios, catálogo y reservas de visitas. ¿Qué necesitas?"

    if session.state == BotState.esperando_dia_visita:
        parsed = parse_iso_date(text)
        if not parsed or not is_valid_visit_day(parsed):
            return "Necesito un día de lunes a viernes válido y que no sea feriado. Por favor indicá la fecha en formato YYYY-MM-DD."
        session.visit_day = parsed
        session.state = BotState.esperando_horario_visita
        save_session(session)
        return "Perfecto. ¿A qué hora querés venir? Los horarios disponibles son 17:00, 17:30, 18:00, 18:30, 19:00 y 19:30."

    if session.state == BotState.esperando_horario_visita:
        parsed_time = parse_iso_time(text)
        if not parsed_time or not is_valid_visit_time(parsed_time):
            return "Ese horario no es válido. Elegí uno de los siguientes: 17:00, 17:30, 18:00, 18:30, 19:00 o 19:30."
        session.visit_time = parsed_time
        session.state = BotState.esperando_cantidad_personas
        save_session(session)
        return "¿Cuántas personas van a asistir? Capacidad por módulo: 2 personas."

    if session.state == BotState.esperando_cantidad_personas:
        count = extract_people_count(text)
        if count is None or count < 1:
            return "No entendí la cantidad. Decime cuántas personas vendrán, por ejemplo 2 o 3."
        session.people_count = count
        session.state = BotState.confirmando_visita
        save_session(session)
        return (
            f"Confirmo la visita para el {format_date(session.visit_day)} a las {format_time(session.visit_time)} "
            f"para {session.people_count} persona(s). Confirmás la reserva por WhatsApp?"
        )

    if session.state == BotState.confirmando_visita:
        if text.lower() in {"sí", "si", "confirmo", "ok", "dale", "confirmar"}:
            try:
                booking = create_visit(phone, session.visit_day, session.visit_time, session.people_count)
                session.visit_created = True
                session.state = BotState.inicio
                save_session(session)
                return (
                    f"Reserva confirmada. Tu visita está registrada con ID {booking['booking_id']}. "
                    f"Te esperamos el {format_date(session.visit_day)} a las {format_time(session.visit_time)}."
                )
            except Exception:
                session.state = BotState.inicio
                save_session(session)
                alternative = find_alternatives(session.visit_day, session.people_count)
                if alternative:
                    formatted = ", ".join(format_time(slot) for slot in alternative[:3])
                    return (
                        "No hay disponibilidad exacta en ese horario o cantidad. "
                        f"Podemos ofrecer estos horarios: {formatted}."
                    )
                return "Lo siento, no hay disponibilidad para ese día. Podés intentar otra fecha o reservar por la web."
        session.state = BotState.inicio
        save_session(session)
        return "Entendido. Si querés puedo enviarte el link de nuevo para reservar en la web."

    return "Lo siento, no entendí. Si querés lo seguimos por atención humana."


def extract_people_count(text: str) -> int | None:
    digits = re.findall(r"\d+", text)
    if digits:
        return int(digits[0])
    return None
