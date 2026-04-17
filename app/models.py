from enum import Enum
from pydantic import BaseModel
from datetime import date, time

class Channel(str, Enum):
    whatsapp = "whatsapp"
    instagram = "instagram"

class BotState(str, Enum):
    inicio = "inicio"
    esperando_fecha_evento = "esperando_fecha_evento"
    esperando_dia_visita = "esperando_dia_visita"
    esperando_horario_visita = "esperando_horario_visita"
    esperando_cantidad_personas = "esperando_cantidad_personas"
    confirmando_visita = "confirmando_visita"
    derivado_humano = "derivado_humano"

class Intent(str, Enum):
    precio = "precio"
    visita = "visita"
    saludo = "saludo"
    desconocido = "desconocido"
    humano = "humano"

class SessionData(BaseModel):
    phone: str
    state: BotState = BotState.inicio
    intent: Intent = Intent.desconocido
    event_type: str | None = None
    event_date: date | None = None
    visit_day: date | None = None
    visit_time: time | None = None
    people_count: int | None = None
    link_sent: bool = False
    visit_created: bool = False

class VisitReservation(BaseModel):
    phone: str
    visit_date: date
    visit_time: time
    people_count: int
    created_by: str
