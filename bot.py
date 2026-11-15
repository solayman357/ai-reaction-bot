import os
import re
import random
import threading
from flask import Flask
from telegram import Update, ReactionTypeEmoji
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ===== কনফিগারেশন =====
TOKEN = os.environ.get("BOT_TOKEN", "9241228046:AAGzNtLPGmNMmavg7I4YL2oW5JAh8MV7330")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "official_gt")

if not TOKEN:
    raise SystemExit("BOT_TOKEN env var is required")

# ===== Render 24/7 ওয়েব সার্ভার =====
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "TAMIM REACTION BOT IS ALIVE 🔥"

def run_web():
    port = int(os.environ.get("PORT", "10000"))
    app_web.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ব্যাকগ্রাউন্ড থ্রেডে ওয়েব সার্ভার চালু করা
threading.Thread(target=run_web, daemon=True).start()

# self-ping so Render free plan never spins down
import time as _time, urllib.request as _urlreq
def _self_ping():
    url = os.environ.get("SELF_PING_URL", "https://ai-reaction-bot.onrender.com/")
    while True:
        try:
            _urlreq.urlopen(url, timeout=15)
        except Exception:
            pass
        _time.sleep(210)

threading.Thread(target=_self_ping, daemon=True).start()

# ===== পারফেক্ট Reaction লজিক =====
def get_perfect_reaction(text):
    if not text:
        return "❤️"
    t = text.lower().strip()

    # ০. মেসেজে নির্দিষ্ট ইমোজি থাকলে সেটাই ব্যাক করবে
    emojis_in_msg = re.findall(r'[\U0001F000-\U0001FAFF\u2600-\u27BF]+', text)
    if emojis_in_msg:
        return emojis_in_msg[0]

    # ১. ভালোবাসা / Love
    if any(w in t for w in ["love","ভালোবাসি","bhalobashi","jaan","baby","sona","koliza","prem","প্রেম","pyaar","pyar","mohabbat","ishq","jaanu","meri jaan","dil","❤️","rak","รัก","thii rak","ที่รัก","faen","แฟน","khid thung","คิดถึง"]):
        return random.choice(["❤️","😍","🥰","😘","🫶","❤️‍🔥"])

    # ২. হাসি / Funny
    if any(w in t for w in ["haha","hehe","হাহা","moja","মзақ","funny","lol","joke","hashi","হাসি","hasi","maja","mast","hasa","😂","talok","ตลก","kham","ขำ","sanuk","สนุก","lol555","555"]):
        return random.choice(["😂","🤣","😆","😅","🤭","😜"])

    # ৩. রাগ / Angry
    if any(w in t for w in ["rag","রাগ","angry","fuck","bokachoda","boka","faltu","bal","pagol","harami","kutta","gussa","गुस्सा","chutiya","bakwas","bhenchod","madarchod","pagal","krot","โกรธ","mod","โมโห","hia","เหี้ย"]):
        return random.choice(["😡","🤬","😤","😠","😒","🖕"])

    # ৪. কান্না / Sad
    if any(w in t for w in ["kosto","কষ্ট","kanna","কান্না","sad","cry","mon kharap","depress","breakup","cheka","chere gese","dukh","दुख","rona","रोना","dard","दर्द","akela","udaas","tension","sia jai","เสียใจ","khao jai","เศร้า"]):
        return random.choice(["😢","😭","💔","😔","🥺","🫂"])

    # ৫. Wow / জোস
    if any(w in t for w in ["wow","ওয়াও","sera","সেরা","joss","জোস","osthir","অস্থির","amazing","best","op","shei","mast","बढ़िया","badiya","kamaal","gazab","awesome"]):
        return random.choice(["🔥","😮","🤯","💯","👏","🤩"])

    # ৬. Hi / হ্যালো / সালাম
    if any(w in t for w in ["hi","hello","হাই","salam","সালাম","assalam","hey","hlw","namaste","नमस्ते","sawaddee","สวัสดี"]):
        return random.choice(["👋","😊","🙏","🤝","🫡"])

    # ৭. ধন্যবাদ / Thanks
    if any(w in t for w in ["thank","ধন্যবাদ","tnx","thanks","shukriya","dhonnobad","shukriya","धन्यवाद","dhanyavad","khop khun","ขอบคุณ"]):
        return random.choice(["🙏","❤️","🥰","😊","🤗"])

    # ৮. লাইক / সাপোর্ট / Done
    if any(w in t for w in ["like","লাইক","boost","free","ফ্রি","done","dn","back","support","check","follow"]):
        return random.choice(["❤️","🔥","👏","💯","✅","🙌"])

    # ৯. খাবার / Food
    if any(w in t for w in ["khabar","খাবার","vat","ভাত","biriyani","cha","চা","coffee","fuska","khuda","khana","खाना","bhook","भूख","kin khao","กินข้าว"]):
        return random.choice(["😋","🤤","🙂","☕","🍕"])

    # ১০. ঘুম / Sleep
    if any(w in t for w in ["ghum","ঘুম","sleep","gn","good night","tired","neend","नींद","so jao","non","นอน","fan dee"]):
        return random.choice(["😴","🥱","🌙","💤","🛌"])

    # ১১. সকাল / Morning
    if any(w in t for w in ["good morning","sokal","সকাল","gm","morning","uthlam","subah","सुबह"]):
        return random.choice(["🌅","☀️","🌞","😊","🌻"])

    # ১২. গেম / Game
    if any(w in t for w in ["game","গেম","ff","free fire","pubg","cricket","football","khel","खेल","bgmi","เล่นเกม"]):
        return random.choice(["🎮","🕹️","🔥","🎯","🏆","⚽"])

    # ১৩. টাকা / Money
    if any(w in t for w in ["taka","টাকা","money","tk","cash","paisa","पैसा","rupya","salary","amir","เงิน","baht","บาท"]):
        return random.choice(["💰","💵","💸","🤑"])

    # ১৪. গান / Music
    if any(w in t for w in ["gan","গান","song","music","gaana","गाना","sun","phleng","เพลง","dance"]):
        return random.choice(["🎵","🎶","🎤","🎧","🎸"])

    # ১৫. ধর্ম / Pray
    if any(w in t for w in ["allah","আল্লাহ","dua","দোয়া","namaz","নামাজ","quran","islam","bhagwan","भगवान","ram","puja","masjid","สาธุ"]):
        return random.choice(["🙏","🤍","✨","🕊️"])

    # ১৬. বিদায় / Bye
    if any(w in t for w in ["bye","বিদায়","biday","allah hafez","tata","bye bye","अलविदा","chal bye","ลาก่อน"]):
        return random.choice(["👋","😢","🥺","🌙","✌️"])

    # ১৭. প্রশ্ন / Question
    if "?" in text or any(w in t for w in ["ki","কি","keno","কেন","kivabe","kemon","kya","क्या","kyu","क्यों","kaise","कैसे","ทำไม","อะไร"]):
        return random.choice(["🤔","🤨","🧐","😕","🤷"])

    # ১৮. জন্মদিন / Party
    if any(w in t for w in ["birthday","জন্মদিন","party","পার্টি","biye","বিয়ে","janmdin","shaadi","วันเกิด","ปาร์ตี้"]):
        return random.choice(["🎉","🎊","🥳","🎂","🎁","🎈"])

    # ১৯. ভয় / Scared
    if any(w in t for w in ["voy","ভয়","scared","bhoy","darr","bhoot","dar","डर","ghost","ผี","กลัว"]):
        return random.choice(["😱","😨","😰","👻","💀"])

    # ২০. বন্ধু / Friend
    if any(w in t for w in ["bondhu","বন্ধু","friend","dost","vai","ভাই","yaar","यार","bhai","भाई","เพื่อน"]):
        return random.choice(["🤝","❤️","🫶","👊"])

    # ডিফল্ট রিঅ্যাকশন (মেসেজ ম্যাচ না করলে)
    return random.choice(["❤️","🔥","😍","👏","🥰","💯","✨"])

# ===== বট হ্যান্ডেলার্স =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user.username or user.username.lower() != OWNER_USERNAME.lower():
        await update.message.reply_text("আমি শুধু OWNER এর কথা শুনি অন্য কারো না 🙄 আমাকে সেট করতে হলে @official_gt কে নিয়ে এসো।")
        return
    await update.message.reply_text("হ্যালো বস! আমি সচল আছি এবং গ্রুপে রিঅ্যাকশন দেওয়ার জন্য প্রস্তুত। 🔥")

async def handle_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # শুধুমাত্র টেক্সট মেসেজ থাকলে প্রসেস করবে
    if not update.message or not update.message.text:
        return
        
    # বটের নিজের মেসেজ হলে ইগনোর করবে (লুপ বন্ধ করার জন্য)
    if update.message.from_user.is_bot:
        return

    text = update.message.text
    emoji = get_perfect_reaction(text)

    try:
        # python-telegram-bot v20+ এর সঠিক রিঅ্যাকশন মেথড
        await update.message.set_reaction(reaction=ReactionTypeEmoji(emoji=emoji))
    except Exception as e:
        print(f"Reaction Error: {e}")

# ===== মেইন এক্সিকিউশন =====
def main():
    # অ্যাপ্লিকেশন তৈরি
    application = ApplicationBuilder().token(TOKEN).build()

    # হ্যান্ডেলার অ্যাড করা
    application.add_handler(CommandHandler("start", start))
    
    # মেসেজ ফিল্টার: শুধুমাত্র টেক্সট মেসেজ রিড করবে, কোনো কমান্ড বা বটের মেসেজ নয়
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.UpdateType.CHANNEL_POST, handle_reaction))

    # বট রানিং
    print("Bot is polling...")
    application.run_polling()

if __name__ == '__main__':
    main()
