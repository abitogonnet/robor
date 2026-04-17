import os
from app.models import Channel

WHATSAPP_API_URL = os.environ.get("WHATSAPP_API_URL")
WHATSAPP_API_TOKEN = os.environ.get("WHATSAPP_API_TOKEN")


def send_message(channel: str, user: str, text: str) -> None:
    if channel == Channel.whatsapp.value:
        print(f"[WhatsApp] To {user}: {text}")
        return
    if channel == Channel.instagram.value:
        print(f"[Instagram] To {user}: {text}")
        return
    print(f"[Unknown channel] To {user}: {text}")


def verify_integration() -> bool:
    return bool(WHATSAPP_API_URL and WHATSAPP_API_TOKEN)
