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

# --- ensure an event loop exists in main thread ---
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
        if not message:
            print("⚠️ No effective_message in update")
            return

        # Skip messages from other bots
        if message.from_user and message.from_user.is_bot:
            print("⚠️ Ignoring message from another bot")
            return

        text = message.text or message.caption or ""

        # Choose emoji via Gemini AI
        chosen_emoji = "👍"
        if ai_client:
            try:
                prompt = f"""
Analyze the emotion of the following Telegram message and return ONLY ONE emoji that perfectly represents the reaction a human would give.
You have access to all emojis in the world. Choose accurately based on hidden sadness, sarcasm, joy, pain, anger, or love.
Do not include any explanation, text, or punctuation. Just return the raw emoji character.

Message: "{text}"
"""
                response = ai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                chosen_emoji = response.text.strip()
                # Sanitize: take only first emoji-like char
                import re
                emojis = re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF\U00002702-\U000027B0]', chosen_emoji)
                if emojis:
                    chosen_emoji = emojis[0]
                else:
                    chosen_emoji = "👍"
            except Exception as e:
                print(f"⚠️ Gemini error: {e}")
                chosen_emoji = "👍"

        # Small human-like delay
        await asyncio.sleep(random.uniform(0.5, 1.5))

        # Set reaction
        try:
            await message.set_reaction(reaction=chosen_emoji)
            print(f"✅ Reacted '{chosen_emoji}' to: {text[:40]}")
        except Exception as e:
            print(f"⚠️ set_reaction failed: {e}")

    except Exception as e:
        print(f"⚠️ Handler error: {e}")

async def post_init(application: Application):
    # Explicitly delete webhook to avoid polling conflict
    await application.bot.delete_webhook(drop_pending_updates=True)
    print("🗑️ Webhook deleted — polling is active")

async def post_shutdown(application: Application):
    print("🛑 Bot shutting down")

def main():
    keep_alive()
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    # React to ALL non-command messages (text, photo, video, sticker, voice, etc.)
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, analyze_and_react))
    print("🤖 Bot polling started — waiting for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
