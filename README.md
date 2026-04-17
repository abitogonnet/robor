# ABITO WhatsApp Bot

Bot de WhatsApp para ABITO con flujo de consultas de precios, reserva de visitas y recordatorios.

## Características

- Webhook compatible con WhatsApp e Instagram (preparado)
- Persistencia de sesiones y estados de conversación
- Motor de intents simple y robusto
- Agenda realista de visitas con slots y capacidad
- Creación de visitas usando la base real simulada
- Recordatorios automáticos sin duplicados

## Estructura

- `app/main.py` — servidor FastAPI y webhook
- `app/bot.py` — lógica de conversación
- `app/sessions.py` — persistencia de sesiones
- `app/services/visits.py` — reglas de agenda y disponibilidad
- `app/services/reminders.py` — recordatorios automáticos
- `app/services/catalog.py` — precios / catálogo sencillo
- `app/integrations/*.py` — puntos de extensión para APIs externas

## Ejecutar

1. Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

2. Iniciar la app:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

## Webhook

- `GET /webhook` — verificación básica
- `POST /webhook` — recibe mensajes y responde

Ejemplo de payload:

```json
{
  "channel": "whatsapp",
  "phone": "+5491123456789",
  "text": "Quiero reservar una visita"
}
```

## Tests

```powershell
pytest
```

## Ejecutar localmente

1. Copiá `.env.example` a `.env` y completá los valores.
2. Instalá dependencias:

```powershell
python -m pip install -r requirements.txt
```

3. Ejecutá el bot:

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Si querés probar webhook desde Windows, usá `ngrok` o un servicio similar para exponer `http://localhost:8000`.

```powershell
ngrok http 8000
```

## Deploy en Render

Podés subir este proyecto a Render como un servicio web Python. El servicio debe usar:

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
- Environment Variables:
  - `RENDER_PUBLIC_DB_URL`
  - `RENDER_INTERNAL_DB_URL`
  - `RENDER_PUBLIC_CATALOG_TABLE` (opcional)
  - `RENDER_PUBLIC_VISIT_TABLE` (opcional)
  - `RENDER_INTERNAL_RETURNS_TABLE` (opcional)

Este repositorio incluye un archivo `render.yaml` de ejemplo para configurar Render.

## Configuración futura

Se pueden enlazar WhatsApp API real, Instagram y bases de datos del render actualizando `app/integrations/whatsapp_api.py`, `app/integrations/web_base.py` y `app/integrations/internal_base.py`.

## Variables de entorno para Render

- `RENDER_PUBLIC_DB_URL` — URL de la base pública del sitio web
- `RENDER_PUBLIC_CATALOG_TABLE` — tabla de catálogos (por defecto: `catalog`)
- `RENDER_PUBLIC_VISIT_TABLE` — tabla de reservas/visitas (por defecto: `visits`)
- `RENDER_INTERNAL_DB_URL` — URL de la base interna de devoluciones
- `RENDER_INTERNAL_RETURNS_TABLE` — tabla de devoluciones (por defecto: `returns`)

### Datos de tu base de Render

- Host interno: `dpg-d7cimldckfvc739qt08g-a`
- Host externo: `dpg-d7cimldckfvc739qt08g-a.virginia-postgres.render.com`
- Puerto: `5432`
- Base de datos: `abito_web_db`
- Usuario: `abito_web_user`
- URL de conexión externa:
  - `postgresql://abito_web_user:<password>@dpg-d7cimldckfvc739qt08g-a.virginia-postgres.render.com/abito_web_db`
- URL de conexión interna (Render):
  - `postgresql://abito_web_user:<password>@dpg-d7cimldckfvc739qt08g-a/abito_web_db`

### Ejemplo de configuración

```powershell
$env:RENDER_PUBLIC_DB_URL = "postgresql://abito_web_user:<password>@dpg-d7cimldckfvc739qt08g-a.virginia-postgres.render.com/abito_web_db"
$env:RENDER_INTERNAL_DB_URL = "postgresql://abito_web_user:<password>@dpg-d7cimldckfvc739qt08g-a/abito_web_db"
```
