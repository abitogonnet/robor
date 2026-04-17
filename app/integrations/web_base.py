import os
from datetime import date, time, datetime, timedelta
from app.integrations.db import get_connection, has_db
from app.utils import SLOT_TIMES, MODULE_CAPACITY, slot_persons_for_group

PUBLIC_DB_URL_ENV = "RENDER_PUBLIC_DB_URL"
PUBLIC_CATALOG_TABLE = os.environ.get("RENDER_PUBLIC_CATALOG_TABLE", "catalog")
PUBLIC_VISIT_TABLE = os.environ.get("RENDER_PUBLIC_VISIT_TABLE", "visitas_visita")


def get_catalog_item(item_code: str) -> dict[str, str | float] | None:
    if not has_db(PUBLIC_DB_URL_ENV):
        return {"abito_muestra": {"name": "Tour ABITO", "price": 150.0, "currency": "ARS"}}.get(item_code)

    query = f"SELECT name, price, currency FROM {PUBLIC_CATALOG_TABLE} WHERE code = %s LIMIT 1"
    with get_connection(PUBLIC_DB_URL_ENV) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (item_code,))
        row = cursor.fetchone()
        if row:
            return {"name": row[0], "price": row[1], "currency": row[2]}
    return None


def query_availability(visit_date: date, visit_time: time, modules: int, people_count: int) -> bool | None:
    if not has_db(PUBLIC_DB_URL_ENV):
        return None

    start = visit_time.strftime("%H:%M:%S")
    end_date_time = datetime.combine(visit_date, visit_time) + timedelta(minutes=modules * 30)
    end_time = end_date_time.time().strftime("%H:%M:%S")
    query = (
        f"SELECT hora_visita, SUM(cantidad_personas) FROM {PUBLIC_VISIT_TABLE} "
        f"WHERE fecha_visita = %s AND hora_visita >= %s AND hora_visita < %s "
        f"GROUP BY hora_visita"
    )
    with get_connection(PUBLIC_DB_URL_ENV) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, (visit_date.isoformat(), start, end_time))
            rows = cursor.fetchall()
            booked = {row[0].strftime("%H:%M:%S") if hasattr(row[0], "strftime") else row[0]: row[1] for row in rows}
            start_index = SLOT_TIMES.index(visit_time)
            reserved = slot_persons_for_group(people_count)
            for offset, slot_index in enumerate(range(start_index, start_index + modules)):
                if slot_index >= len(SLOT_TIMES):
                    return False
                slot_code = SLOT_TIMES[slot_index].strftime("%H:%M:%S")
                if booked.get(slot_code, 0) + reserved[offset] > MODULE_CAPACITY:
                    return False
            return True
        except Exception:
            return None


def create_visit_in_web(phone: str, visit_date: date, visit_time: time, people_count: int) -> dict[str, str]:
    if not has_db(PUBLIC_DB_URL_ENV):
        return {
            "status": "created",
            "booking_id": f"ABITO-{visit_date.strftime('%Y%m%d')}-{visit_time.strftime('%H%M')}-{phone[-4:]}",
        }

    now = datetime.now()
    estado = os.environ.get("RENDER_DEFAULT_VISIT_STATUS", "confirmado")
    origen = os.environ.get("RENDER_DEFAULT_VISIT_ORIGIN", "bot_whatsapp")
    insert = (
        f"INSERT INTO {PUBLIC_VISIT_TABLE} (nombre, dni, telefono, cantidad_personas, fecha_evento, fecha_visita, hora_visita, creado, actualizado, estado, observaciones_internas, origen, vio_prendas_catalogo) "
        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id"
    )
    with get_connection(PUBLIC_DB_URL_ENV) as conn:
        cursor = conn.cursor()
        cursor.execute(
            insert,
            (
                "Reserva WhatsApp",
                "0",
                phone,
                people_count,
                visit_date.isoformat(),
                visit_date.isoformat(),
                visit_time.strftime("%H:%M:%S"),
                now,
                now,
                estado,
                "Reserva creada por WhatsApp",
                origen,
                False,
            ),
        )
        row = cursor.fetchone()
        conn.commit()
        booking_id = f"ABITO-{visit_date.strftime('%Y%m%d')}-{visit_time.strftime('%H%M')}-{row[0]}"
        return {"status": "created", "booking_id": booking_id}
