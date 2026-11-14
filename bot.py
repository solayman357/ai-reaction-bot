import os
import random
import asyncio
import threading
import time as _time
import urllib.request as _urlreq
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google import genai

# ensure an event loop exists in main thread (Pyrogram/PTB requirement)
try:
    asyncio.get_event_loop()
except RuntimeError:
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

# --- Flask keep-alive server (Render uses PORT env var) ---
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "🔥 AI Reaction Bot is live!"

def run_flask():
    port = int(os.environ.get("PORT", "8080"))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()

# self-ping so Render free plan never spins down
def _self_ping():
    url = os.environ.get("SELF_PING_URL")
    if not url:
        return
    while True:
        try:
            _urlreq.urlopen(url, timeout=15)
        except Exception:
            pass
        _time.sleep(210)

threading.Thread(target=_self_ping, daemon=True).start()

# --- Only 2 env vars needed ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

print("🤖 AI Reaction Bot starting (token-only, no API_ID needed)...")

async def analyze_and_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.effective_message
        if not message or not (message.text or message.caption):
            return
        text = message.text or message.caption
        prompt = f"""
Analyze the emotion of the following Telegram message and return ONLY ONE emoji that perfectly represents the reaction a human would give.
You have access to all emojis in the world. Choose accurately based on hidden sadness, sarcasm, joy, pain, anger, or love.
Do not include any explanation, text, or punctuation. Just return the raw emoji character.

Message: "{text}"
"""
        if ai_client:
            response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            chosen_emoji = response.text.strip()
        else:
            chosen_emoji = "👍"
        await asyncio.sleep(random.uniform(1.0, 3.2))
        await message.set_reaction(reaction=chosen_emoji)
        print(f"📊 '{text[:20]}...' -> {chosen_emoji}")
    except Exception as e:
        print(f"⚠️ Reaction failed: {e}")

def main():
    keep_alive()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, analyze_and_react))
    application.run_polling()

if __name__ == "__main__":
    main()
