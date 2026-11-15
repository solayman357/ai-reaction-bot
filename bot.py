import os
import re
import random
import threading
from flask import Flask
from telegram import Update, ReactionTypeEmoji
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ===== কনফিগারেশন =====
TOKEN = "9241228046:AAGzNtLPGmNMmavg7I4YL2oW5JAh8MV7330"
OWNER_USERNAME = "official_gt"

# ===== Render 24/7 ওয়েব সার্ভার =====
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "GT REACTION BOT IS ALIVE 🔥"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

threading.Thread(target=run_web, daemon=True).start()

# ===== টেলিগ্রাম স্ট্যান্ডার্ড রিঅ্যাকশন লজিক =====
def get_perfect_reaction(text):
    if not text:
        return "❤️"
    t = text.lower().strip()

    # ০. মেসেজে নির্দিষ্ট ইমোজি থাকলে সেটার প্রথমটি ব্যাক করবে
    emojis_in_msg = re.findall(r'[\U0001F000-\U0001FAFF\u2600-\u27BF]+', text)
    if emojis_in_msg:
        # গ্রুপে সাপোর্ট করতে পারে এমন স্ট্যান্ডার্ড ইমোজি ফিল্টার
        allowed_standard = ["👍", "👎", "❤️", "🔥", "🥰", "👏", "😂", "😮", "😢", "😡", "🤔", "🤩", "🎉", "💯", "🙏"]
        for e in emojis_in_msg:
            if e in allowed_standard:
                return e
        return "❤️"

    # ১. ভালোবাসা / Love / Pookie
    if any(w in t for w in ["love","pookie","bhalobashi","ভালোবাসি","jaan","baby","sona","koliza","prem","প্রেম","pyar","dil","❤️"]):
        return random.choice(["❤️", "🥰", "❤️"])

    # ২. হাসি / Funny / Lol
    if any(w in t for w in ["haha", "hehe", "হাহা", "moja", "funny", "lol", "joke", "hashi", "😂"]):
        return random.choice(["😂", "😂"])

    # ৩. রাগ / Angry
    if any(w in t for w in ["rag", "রাগ", "angry", "fuck", "bokachoda", "boka", "faltu", "bal", "pagol", "gussa"]):
        return random.choice(["😡", "😡", "👎"])

    # ৪. কান্না / Sad / Please / Request
    if any(w in t for w in ["kosto", "কষ্ট", "kanna", "sad", "cry", "please", "plz", "request", "🥺", "😢"]):
        return random.choice(["😢", "❤️", "🥰"])

    # ৫. Wow / জোস / How (আশ্চর্যজনক কিছু জানা)
    if any(w in t for w in ["wow", "ওয়াও", "sera", "সেরা", "joss", "osthir", "amazing", "best", "op", "how"]):
        return random.choice(["🔥", "😮", "🤩", "💯"])

    # ६. Hi / হ্যালো / সালাম
    if any(w in t for w in ["hi", "hello", "হাই", "salam", "সালাম", "assalam", "hey", "hlw"]):
        return random.choice(["🥰", "❤️", "👍"])

    # ৭. ধন্যবাদ / Thanks
    if any(w in t for w in ["thank", "ধন্যবাদ", "tnx", "thanks", "shukriya", "dhonnobad"]):
        return random.choice(["🙏", "🥰", "❤️"])

    # ৮. লাইক / সাপোর্ট / Done
    if any(w in t for w in ["like", "লাইক", "boost", "done", "dn", "back", "support", "check"]):
        return random.choice(["👍", "🔥", "💯", "👏"])

    # ৯. গেম / Game
    if any(w in t for w in ["game", "গেম", "ff", "free fire", "pubg", "cricket", "football"]):
        return random.choice(["🔥", "🤩", "💯"])

    # ১০. বিদায় / Bye
    if any(w in t for w in ["bye", "বিদায়", "biday", "allah hafez", "tata", "bye bye"]):
        return random.choice(["😢", "❤️"])

    # ১১. প্রশ্ন / Question
    if "?" in text or any(w in t for w in ["ki", "কি", "keno", "কেন", "kivabe", "kemon"]):
        return random.choice(["🤔", "😮"])

    # ডিফল্ট রিঅ্যাকশন (মেসেজ কোনো ক্যাটাগরিতে ম্যাচ না করলে স্ট্যান্ডার্ড ফ্রি ইমোজিগুলো থেকে র্যান্ডমলি দিবে)
    return random.choice(["❤️", "👍", "🔥", "🥰", "🎉", "🤩", "👏", "😂", "🤔"])

# ===== বট হ্যান্ডেলার্স =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user.username or user.username.lower() != OWNER_USERNAME.lower():
        await update.message.reply_text("আমি শুধু OWNER এর কথা শুনি অন্য কারো না 🙄 আমাকে সেট করতে হলে @official_gt কে লাগবে ।")
        return
    await update.message.reply_text("হ্যালো বস! আমি সচল আছি এবং গ্রুপে রিঅ্যাকশন দেওয়ার জন্য প্রস্তুত। 🔥")

async def handle_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
        
    if update.message.from_user.is_bot:
        return

    text = update.message.text
    emoji = get_perfect_reaction(text)

    try:
        await update.message.set_reaction(reaction=ReactionTypeEmoji(emoji=emoji))
    except Exception as e:
        print(f"Reaction Error: {e}")

# ===== মেইন এক্সিকিউশন =====
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.UpdateType.CHANNEL_POST, handle_reaction))

    print("Bot is polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
