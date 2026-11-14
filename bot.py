import os
import re
import asyncio
import random
import time
import logging
import threading
from collections import OrderedDict
from flask import Flask
from threading import Thread
from telegram import Update, ReactionTypeEmoji
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from google import genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("ai-reaction")

# --- env vars (set in Render dashboard, NOT in source) ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SELF_PING_URL = os.environ.get("SELF_PING_URL")

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN env var is required")
if not GEMINI_API_KEY:
    raise SystemExit("GEMINI_API_KEY env var is required")

# --- Gemini client ---
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# --- dedupe cache: skip duplicate consecutive messages per chat ---
_recent_cache = OrderedDict()
MAX_CACHE = 200

def _is_duplicate(chat_id: int, text: str) -> bool:
    key = f"{chat_id}:{text[:80]}"
    if key in _recent_cache:
        return True
    _recent_cache[key] = time.time()
    if len(_recent_cache) > MAX_CACHE:
        _recent_cache.popitem(last=False)
    return False

# --- Telegram-supported reaction emoji set ---
VALID_EMOJIS = set("""👍👎❤️🔥😂😮😭😡😍👏🙏🤔🥰😘😎🤩😇🙃🤫🤭🤗😴😜🙄😳😞😟😕🙁😖😣😫😩🥺😢😭😱😨😰😥😓😪😵😐😑😒🙄🤯😬😳""")

def _extract_emoji(text: str) -> str:
    """Extract the first valid Telegram reaction emoji from Gemini's response."""
    if not text:
        return ""
    text = text.strip().strip('"').strip("'").strip()
    # Find any valid emoji in the response
    for ch in text:
        if ch in VALID_EMOJIS:
            return ch
    # Fallback: try to find any emoji-like char
    match = re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]', text)
    if match:
        ch = match.group(0)
        if ch in VALID_EMOJIS:
            return ch
    return ""

# --- system prompt ---
SYSTEM_PROMPT = """You are an intelligent Telegram reaction bot. Analyze the user's message deeply — meaning, emotion, tone, context, sarcasm, intention, and cultural nuance (including Bangla, Banglish, and English).

Return EXACTLY ONE Telegram-supported reaction emoji that best represents a human reaction to this message.

Rules:
- Return ONLY the raw emoji character, nothing else.
- No explanation, no text, no punctuation, no quotes.
- Do NOT return "👍" for every message — pick an emoji that genuinely fits.
- If unsure, pick a contextually appropriate emoji (😊, ❤️, 🤔, 😮, 🔥, etc.).
- Supported emoji only (Telegram reaction set).
"""

# --- Flask keep-alive ---
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "🤖 AI Reaction Bot is live!"

def run_flask():
    port = int(os.environ.get("PORT", "8080"))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()

def _self_ping():
    if not SELF_PING_URL:
        return
    while True:
        try:
            import urllib.request as _urlreq
            _urlreq.urlopen(SELF_PING_URL, timeout=15)
        except Exception:
            pass
        time.sleep(210)

threading.Thread(target=_self_ping, daemon=True).start()

# --- message handler ---
async def analyze_and_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

    # Skip other bots
    if message.from_user and message.from_user.is_bot:
        return

    text = message.text or message.caption or ""
    if not text.strip():
        return

    chat_id = message.chat.id
    msg_id = message.message_id

    # Deduplicate consecutive identical messages
    if _is_duplicate(chat_id, text):
        return

    # --- Gemini analysis ---
    chosen_emoji = ""
    try:
        prompt = f"""{SYSTEM_PROMPT}

Message: "{text}"
"""
        response = None
        last_err = None
        # Use a known-available Gemini model
        candidates = [
            'models/gemini-2.5-flash', 'models/gemini-2.5-pro', 'models/gemini-3.5-flash',
            'models/gemini-3.8-flash', 'models/gemini-3.7-flash', 'models/gemini-3.6-flash',
            'gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-3.5-flash',
            'gemini-3.8-flash', 'gemini-3.7-flash', 'gemini-3.6-flash',
        ]
        # Deduplicate while preserving order
        seen = set()
        candidates = [c for c in candidates if not (c in seen or seen.add(c))]

        for model_name in candidates:
            try:
                response = ai_client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                break
            except Exception as e:
                last_err = e
                log.warning(f"Model {model_name} failed: {e}")
                continue
        if response is None:
            raise last_err or Exception("All Gemini models failed")
        raw = response.text or ""
        chosen_emoji = _extract_emoji(raw)
        log.info(f"Gemini raw='{raw[:60]}' -> emoji='{chosen_emoji}' for text='{text[:40]}'")
    except Exception as e:
        log.error(f"Gemini API error: {e}")
        chosen_emoji = ""

    # If Gemini failed or returned invalid, pick a contextual fallback (not always 👍)
    if not chosen_emoji:
        t = text.lower()
        if any(w in t for w in ["হাসি", "haha", "lol", "😂", "funny", "জোক"]):
            chosen_emoji = "😂"
        elif any(w in t for w in ["ভালোবাসি", "love", "❤️", "baby", "sona"]):
            chosen_emoji = "❤️"
        elif any(w in t for w in ["দুঃখ", "sad", "😢", "কান্না"]):
            chosen_emoji = "😢"
        elif any(w in t for w in ["রাগ", "angry", "😡", "হাঁই"]):
            chosen_emoji = "😡"
        elif any(w in t for w in ["ওও", "wow", "😮", "চমৎকার"]):
            chosen_emoji = "😮"
        elif any(w in t for w in ["ধন্যবাদ", "thanks", "thank", "🙏"]):
            chosen_emoji = "🙏"
        elif "?" in text:
            chosen_emoji = "🤔"
        else:
            chosen_emoji = "😐"  # neutral but not 👍
        log.warning(f"Gemini fallback used emoji='{chosen_emoji}'")

    # --- Set reaction ---
    try:
        await message.set_reaction(reaction=ReactionTypeEmoji(emoji=chosen_emoji))
        log.info(f"✅ Reacted '{chosen_emoji}' to: {text[:50]}")
    except Exception as e:
        log.error(f"Telegram setReaction failed: {e}")

async def post_init(application: Application):
    await application.bot.delete_webhook(drop_pending_updates=True)
    log.info("🗑️ Webhook deleted — polling active")

def main():
    keep_alive()
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, analyze_and_react))
    log.info("🤖 AI Reaction Bot polling started — waiting for group messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
