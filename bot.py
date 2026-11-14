import os
import random
import asyncio
import threading
import time as _time
import urllib.request as _urlreq
from flask import Flask

# ensure an event loop exists in main thread (Pyrogram requirement on py3.14)
try:
    asyncio.get_event_loop()
except RuntimeError:
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

# keep-alive self-ping so Render free plan never spins down
def _self_ping():
    url=os.environ.get("SELF_PING_URL")
    if not url:
        return
    while True:
        try:
            _urlreq.urlopen(url, timeout=15)
        except Exception:
            pass
        _time.sleep(210)
threading.Thread(target=_self_ping, daemon=True).start()


from threading import Thread
from pyrogram import Client, filters
from pyrogram.types import Message
from google import genai

# --- Flask keep-alive server (Render uses PORT env var) ---
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "🔥 AI Reaction Bot is live and running!"

def run_flask():
    port = int(os.environ.get("PORT", 8008))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()

# --- Env vars (set these in Render dashboard) ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID", "0") or "0")
API_HASH = os.environ.get("API_HASH", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

app = Client("ai_reaction_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

print("🤖 AI Reaction Bot starting...")

@app.on_message(filters.group & ~filters.service)
async def analyze_and_react(client: Client, message: Message):
    try:
        text = message.text or message.caption
        if not text:
            return

        prompt = f"""
        Analyze the emotion of the following Telegram message and return ONLY ONE emoji that perfectly represents the reaction a human would give.
        You have access to all emojis in the world. Choose accurately based on hidden sadness, sarcasm, joy, pain, anger, or love.
        Do not include any explanation, text, or punctuation. Just return the raw emoji character.

        Message: "{text}"
        """

        if ai_client:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            chosen_emoji = response.text.strip()
        else:
            chosen_emoji = "👍"

        await asyncio.sleep(random.uniform(1.0, 3.2))
        await message.react(chosen_emoji)
        print(f"📊 '{text[:20]}...' -> {chosen_emoji}")

    except Exception as e:
        print(f"⚠️ Reaction failed: {e}")

if __name__ == "__main__":
    keep_alive()
    threading.Thread(target=_self_ping, daemon=True).start()
    app.run()
