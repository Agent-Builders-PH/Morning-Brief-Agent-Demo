"""Setup helper: print the chat_id for your Telegram bot.

1. Put TELEGRAM_BOT_TOKEN in .env (from @BotFather).
2. Open your bot in Telegram and send it any message, e.g. "hi".
3. Run:  python scripts/get_telegram_chat_id.py
"""

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token:
    sys.exit("Set TELEGRAM_BOT_TOKEN in .env first.")

resp = httpx.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=20)
resp.raise_for_status()

chats = {}
for update in resp.json().get("result", []):
    msg = update.get("message") or update.get("edited_message") or {}
    chat = msg.get("chat")
    if chat:
        chats[chat["id"]] = chat.get("username") or chat.get("first_name") or chat.get("title")

if not chats:
    sys.exit("No messages yet. Send your bot a message in Telegram, then run this again.")
for chat_id, who in chats.items():
    print(f"TELEGRAM_CHAT_ID={chat_id}    ({who})")
