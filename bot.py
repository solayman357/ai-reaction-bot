from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random, re, os, threading, asyncio
from flask import Flask

TOKEN = os.environ.get("BOT_TOKEN")
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "official_gt")

if not TOKEN:
    raise SystemExit("BOT_TOKEN env var is required")

# ===== Render 24/7 এর জন্য - বটকে জাগিয়ে রাখবে =====
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "TAMIM REACTION BOT IS ALIVE 🔥"

def run_web():
    port = int(os.environ.get("PORT", "8080"))
    app_web.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# self-ping so Render free plan never spins down
import time as _time, urllib.request as _urlreq
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

# ===== সব ভাষার পারফেক্ট Reaction =====
def get_perfect_reaction(text):
    """Choose a fitting emoji based on message content."""
    if not text:
        return random.choice(["❤️","🔥","😍","👏","🥰","😮","🤩","💯","🫶","✨","🌸","🎉","😂","😊","🙏","💪","🎯","🌟","🍀","🎁"])
    t = text.lower().strip()

    # 0. If message contains an emoji, return the first one
    emojis_in_msg = re.findall(r'[🀀-🫿☀-➿]+', text)
    if emojis_in_msg:
        return emojis_in_msg[0]

    # --- Category checks ---
    def any_word(words):
        return any(w in t for w in words)

    # 1. Kiss / Baby / Like-niba — kiss emoji first
    if any_word(["baby","বেবি","like niba","লাইক নিবা","like niba","hum baby","আমি বেবি",
        "kiss","চুম্বন","chumban","mwah","xoxo","💋","😘","give kiss","take kiss","send kiss"]):
        return random.choice(["💋","😘","💘","💖","💝","❤️","🥰","😍"])

    # 1b. Love / Romance (general)
    if any_word(["love","ভালোবাসি","bhalobashi","jaan","sona","koliza","prem","প্রেম",
        "pyaar","pyar","mohabbat","ishq","jaanu","meri jaan","dil","❤️",
        "rak","รัก","thii rak","ที่รัก","faen","แฟน","khid thung","คิดถึง"]):
        return random.choice(["❤️","😍","🥰","💋","💘","💖","💝","💞","💕","😘","🫶","❤️‍🔥"])

    # 2. Funny / Laugh
    if any_word(["haha","hehe","হাহা","moja","মজা","funny","lol","joke","hashi","হাসি",
        "hasi","maja","mast","hasa","😂",
        "talok","ตลก","kham","ขำ","sanuk","สนุก","lol555","555"]):
        return random.choice(["😂","🤣","😆","😅","🤭","😜","😝","🤪","😹","🤡"])

    # 3. Angry
    if any_word(["rag","রাগ","angry","fuck","bokachoda","boka","faltu","bal","pagol","harami","kutta",
        "gussa","गुस्सा","chutiya","bakwas","bhenchod","madarchod","pagal","kutta",
        "krot","โกรธ","mod","โมโห","hia","เหี้ย","sat","สัตว์","ba","บ้า"]):
        return random.choice(["😡","🤬","😤","😠","👿","💢","🖕","😒","🙅","🍌","☠️","🐸"])

    # 4. Sad / Cry
    if any_word(["kosto","কষ্ট","kanna","কান্না","sad","cry","mon kharap","depress","breakup","cheka","chere gese",
        "dukh","दुख","rona","रोना","dard","दर्द","akela","udaas","tension",
        "sia jai","เสียใจ","khao jai","เศร้า","rong hai","ร้องไห้","khit","คิด","ngao","เหงา"]):
        return random.choice(["😢","😭","💔","😔","😞","🥺","🫂","🖤","🌧️","😿"])

    # 5. Wow / Amazing
    if any_word(["wow","ওয়াও","sera","সেরা","joss","জোস","osthir","অস্থির","amazing","best","op","shei",
        "mast","बढ़िया","badiya","kamaal","gazab","awesome",
        "sud yod","สุดยอด","dii mak","ดีมาก","waw","เจ๋ง","thep","เทพ"]):
        return random.choice(["🔥","😮","🤯","😲","💥","⭐","💯","👏","🤩","👑"])

    # 6. Greetings
    if any_word(["hi","hello","হাই","salam","সালাম","assalam","hey","hlw",
        "namaste","नमस्ते","hello bhai","kaise ho","kaisa hai","hi bhai",
        "sawaddee","สวัสดี","watdee","หวัดดี","sabai dee","สบายดี"]):
        return random.choice(["👋","🙋","🤚","😊","🙏","🤝","🫡"])

    # 7. Thanks
    if any_word(["thank","ধন্যবাদ","tnx","thanks","shukriya","dhonnobad",
        "shukriya","धन्यवाद","dhanyavad","thanks yaar",
        "khop khun","ขอบคุณ","khop jai","ขอบใจ"]):
        return random.choice(["🙏","❤️","🥰","😊","🤗","🫶"])

    # 8. Like / Boost — enthusiastic reactions, NOT just thumbs up
    if any_word(["like","লাইক","boost","free","ফ্রি","done","dn","back","support","check","insta","follow",
        "like karo","follow karo","back to back",
        "lai","ไลค์","free like","bp","ติดตาม"]):
        return random.choice(["🔥","❤️","👏","💯","✅","🎁","🙌","🫠","😬","💥","⭐","💪","🎯","🌟"])

    # 9. Food
    if any_word(["khabar","খাবার","vat","ভাত","biriyani","cha","চা","coffee","fuska","khuda",
        "khana","खाना","bhook","भूख","biryani","chai","samosa","paneer",
        "kin khao","กินข้าว","ahan","อาหาร","hio","หิว","khao","ข้าว","tom yum","ต้มยำ"]):
        return random.choice(["😋","🤤","😵","🐸","🌚","😬","🤧","🚀","🙂"])

    # 10. Sleep
    if any_word(["ghum","ঘুম","sleep","gn","good night","tired",
        "neend","नींद","so jao","sone ja",
        "nguang","ง่วง","non","นอน","fan dee","ฝันดี","raatri sawas","ราตรีสวัสดิ์"]):
        return random.choice(["😴","🥱","🌙","💤","🛌","😌"])

    # 11. Morning
    if any_word(["good morning","sokal","সকাল","gm","morning","uthlam",
        "subah","सुबह","good morning bhai",
        "arun sawas","อรุณสวัสดิ์","sao chao","เช้า"]):
        return random.choice(["🌅","☀️","🌞","😊","🌻","🙈"])

    # 12. Game
    if any_word(["game","গেম","ff","free fire","pubg","cricket","football",
        "game","게임","khel","खेल","bgmi","cricket",
        "len gem","เล่นเกม","free fire","rov","เกม"]):
        return random.choice(["🎮","🕹️","🔥","🎯","🏆","⚽","🏏","🎲"])

    # 13. Money
    if any_word(["taka","টাকা","money","tk","cash",
        "paisa","पैसा","rupya","salary","amir",
        "ngoen","เงิน","baht","บาท","ruay","รวย"]):
        return random.choice(["💰","💵","💸","🤑"])

    # 14. Music
    if any_word(["gan","গান","song","music","gaana","गाना","sun",
        "phleng","เพลง","rong phleng","ร้องเพลง","dance","เต้น"]):
        return random.choice(["🎵","🎶","🎤","🎧","🎸","💃"])

    # 15. Religion / Pray
    if any_word(["allah","আল্লাহ","dua","দোয়া","namaz","নামাজ","quran","islam",
        "bhagwan","भगवान","ram","puja","mandir","masjid",
        "phra","พระ","tham bun","ทำบุญ","wat","วัด","sathu","สาธุ"]):
        return random.choice(["🙏","🤍","✨","🕊️"])

    # 16. Bye
    if any_word(["bye","বিদায়","biday","allah hafez","tata",
        "bye bye","अलविदा","chal bye",
        "la kon","ลาก่อน","bai","บาย","pai laew","ไปแล้ว"]):
        return random.choice(["👋","😢","🥺","💔","🌙","✌️"])

    # 17. Question
    if "?" in text or any_word(["ki","কি","keno","কেন","kivabe","kemon",
        "kya","क्या","kyu","क्यों","kaise","कैसे","kahan","कहाँ",
        "tham mai","ทำไม","yang ngai","ยังไง","thii nai","ที่ไหน","arai","อะไร"]):
        return random.choice(["🤔","🤨","🧐","😕","❓","🤷"])

    # 18. Birthday / Party
    if any_word(["birthday","জন্মদিন","party","পার্টি","biye","বিয়ে",
        "janmdin","जन्मदिन","shaadi","शादी","party",
        "wan koet","วันเกิด","ngan liang","งานเลี้ยง","paartii","ปาร์ตี้"]):
        return random.choice(["🎉","🎊","🥳","🎂","🎁","🎈","🥂"])

    # 19. Scared
    if any_word(["voy","ভয়","scared","bhoy","darr","bhoot",
        "dar","डर","bhoot","भूत",
        "klua","กลัว","phii","ผี"]):
        return random.choice(["😱","😨","😰","👻","💀","🙀"])

    # 20. Friend
    if any_word(["bondhu","বন্ধু","friend","dost","vai","ভাই",
        "dost","दोस्त","yaar","यार","bhai","भाई",
        "phuean","เพื่อน","phii","พี่","nong","น้อง"]):
        return random.choice(["🤝","👯","❤️","🫶","👊","🤜🤛"])

    # Default diverse fallback (never just 👍)
    return random.choice(["❤️","🔥","😍","👏","🥰","😮","🤩","💯","🫶","✨","🌸","🎉","😂","😊","🙏","💪","🎯","🌟","🍀","🎁","🎊","🥳","🎂","🎈","🥂","😱","😨","😰","👻","💀","🙀","🤝","👯","🫶","👊","🤜🤛","😴","🥱","🌙","💤","🛌","😌","🌅","☀️","🌞","🌻","🙈","🎮","🕹️","🎯","🏆","⚽","🏏","🎲","💰","💵","💸","🤑","🎵","🎶","🎤","🎧","🎸","💃","🙏","🤍","✨","🕊️","👋","😢","🥺","💔","🌙","✌️","🤔","🤨","🧐","😕","❓","🤷","😱","😨","😰","👻","💀","🙀"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user.username or user.username.lower() != OWNER_USERNAME.lower():
        await update.message.reply_text("আমি শুধু OWNER এর কথা শুনি অন্য কারো না 🙄 আমাকে সেট করতে হলে @official_gt কে নিয়ে এসো")
        return
    await update.message.reply_text("Yes Boss ✅ Reaction Bot Ready 🔥 BOT OWNER : @official_gt")

async def auto_reaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return
    if msg.from_user and msg.from_user.is_bot:
        return
    text = msg.text or msg.caption or ""

    # Fast human-like delay (300-800ms) - quick but natural
    await asyncio.sleep(random.uniform(0.3, 0.8))
    if msg.sticker:
        emoji = msg.sticker.emoji or "😍"
    elif msg.photo or msg.video:
        emoji = get_perfect_reaction(text) if text else "🔥"
    elif msg.voice or msg.audio or msg.video_note:
        emoji = "🎵"
    else:
        emoji = get_perfect_reaction(text)
    try:
        await msg.set_reaction(reaction=emoji)
    except Exception:
        # If the chosen emoji is invalid for some reason, fall back
        try:
            await msg.set_reaction(reaction="❤️")
        except Exception:
            try:
                await msg.set_reaction(reaction="👍")
            except Exception:
                pass

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, auto_reaction))
    print("TAMIM REACTION BOT Running 24/7...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
