$env:RENDER_PUBLIC_DB_URL = "postgresql://abito_web_user:<password>@dpg-d7cimldckfvc739qt08g-a.virginia-postgres.render.com/abito_web_db"
$env:RENDER_INTERNAL_DB_URL = "postgresql://abito_web_user:<password>@dpg-d7cimldckfvc739qt08g-a/abito_web_db"
$env:BOT_DB_PATH = "bot_data.sqlite"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
