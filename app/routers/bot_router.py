import json
import os
import requests
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/bot", tags=["Bot Operations"])

# Load bot configuration (the JSON you provided)
BOT_CONFIG_PATH = os.getenv("BOT_CONFIG_PATH", "registered.json")
with open(BOT_CONFIG_PATH, "r", encoding="utf-8") as f:
    BOT_FLOW = json.load(f)

# Green API credentials (from env)
GREEN_API_ID_INSTANCE = os.getenv("GREEN_API_ID_INSTANCE")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")
GREEN_API_URL = f"https://api.green-api.com/waInstance{GREEN_API_ID_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"

# Store user sessions to track conversation state
USER_SESSIONS: Dict[str, Dict[str, Any]] = {}

# Pydantic model for incoming WhatsApp webhook
class IncomingMessage(BaseModel):
    chatId: str
    message: str
    timestamp: Optional[int] = None


def send_message(chat_id: str, text: str):
    """Send WhatsApp message via Green API"""
    payload = {
        "chatId": chat_id,
        "message": text
    }
    try:
        res = requests.post(GREEN_API_URL, json=payload)
        res.raise_for_status()
    except Exception as e:
        print("Green API send error:", e)


def get_language_text(node: dict, lang: str = "1") -> str:
    """Get text for a specific language"""
    return node["text"].get(lang) or list(node["text"].values())[0]


def traverse_flow(node, path: list[str]):
    """Recursively find the menu node based on user's path."""
    if not path:
        return node

    current_code = path[0]
    next_nodes = node.get("content", [])

    for child in next_nodes:
        if child.get("code") == current_code:
            return traverse_flow(child, path[1:])

    return node  # fallback to current if no deeper node found


@router.post("/webhook")
async def webhook(payload: IncomingMessage):
    """Receive WhatsApp message and respond based on bot flow."""
    chat_id = payload.chatId
    user_msg = payload.message.strip()

    # Retrieve or initialize user session
    session = USER_SESSIONS.get(chat_id, {"path": [], "lang": "1"})

    # If user sends '99' → go back one level
    if user_msg == "99" and session["path"]:
        session["path"].pop()
        USER_SESSIONS[chat_id] = session

    # Traverse bot flow according to current path
    node = traverse_flow(BOT_FLOW, session["path"])
    options = node.get("content", [])

    # Handle user menu selection
    if user_msg.isdigit():
        for opt in options:
            if opt["code"] == user_msg:
                session["path"].append(user_msg)
                USER_SESSIONS[chat_id] = session
                next_node = traverse_flow(BOT_FLOW, session["path"])
                send_message(chat_id, get_language_text(next_node, session["lang"]))
                return {"status": "ok"}

    # Handle inputs / payload capture
    if node.get("payload"):
        key = node["payload"]
        session[key] = user_msg
        USER_SESSIONS[chat_id] = session
        send_message(chat_id, "✅ Received! Continue...")
        return {"status": "ok"}

    # If initial start or invalid input → show menu
    menu_text = get_language_text(node, session["lang"])
    send_message(chat_id, menu_text)
    USER_SESSIONS[chat_id] = session
    return {"status": "ok"}
