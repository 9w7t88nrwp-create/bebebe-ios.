

import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Telegram Relay API")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
API_KEY = os.getenv("APP_API_KEY", "")


class Message(BaseModel):
    text: str


@app.get("/")
async def home():
    return {"status": "online", "service": "Telegram Relay"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/send")
async def send_message(message: Message):
    if not BOT_TOKEN or not CHAT_ID or not API_KEY:
        raise HTTPException(503, "Server environment is incomplete")

    if not message.text.strip():
        raise HTTPException(400, "Message cannot be empty")

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": message.text
            }
        )

    if response.status_code != 200:
        raise HTTPException(502, "Telegram delivery failed")

    return {"ok": True}


@app.post("/api/send")
async def api_send(message: Message, authorization: str = ""):
    if not API_KEY or authorization != f"Bearer {API_KEY}":
        raise HTTPException(401, "Unauthorized")

    return await send_message(message)
