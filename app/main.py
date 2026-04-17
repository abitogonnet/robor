from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from app.bot import handle_incoming_message, parse_message_payload
from app.integrations.whatsapp_api import send_message

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

app = FastAPI(title="ABITO WhatsApp Bot")

@app.get("/webhook")
async def verify_webhook(token: str | None = None):
    if token == "verify_token" or token is None:
        return {"status": "ok", "message": "webhook verified"}
    raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    try:
        channel, phone, text = parse_message_payload(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    response_text = handle_incoming_message(phone=phone, text=text, channel=channel)
    send_message(channel=channel, user=phone, text=response_text)
    return JSONResponse({"status": "ok", "response": response_text})
