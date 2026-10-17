import os
import telebot
import yt_dlp
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8823255880:AAHEzXAbs1q1EZZoH2lbWjQEVXPlInHBzno"
bot = telebot.TeleBot(TOKEN)

INSTAGRAM_URL = "https://www.instagram.com/mah__asw?psln=bHVtbTd0NGVkaWh2"
AD_URL = "https://uplcm.com/4/11968073"

# قواميس حفظ النقاط وحالة الإعلانات
user_points = {}

def get_points(user_id):
    return user_points.get(user_id, 0)

def add_point(user_id):
    user_points[user_id] = get_points(user_id) + 1

def deduct_point(user_id):
    if get_points(user_id) > 0:
        user_points[user_id] -= 1

# حفظ بيانات المشتركين
def save_user(user):
    user_id = user.id
    username = f"@{user.username}" if user.username else "لا يوجد يوزر"
    first_name = user.first_name if user.first_name else ""
    last_name = f" {user.last_name}" if user.last_name else ""
    full_name = f"{first_name}{last_name}".strip() or "لا يوجد اسم"
    
    user_entry = f"{user_id} | {username} | {full_name}"
    
    existing_ids = set()
    if os.path.exists('users.txt'):
        with open('users.txt', 'r', encoding='utf-8') as f:
            for line in f:
                if '|' in line:
                    existing_ids.add(line.split('|')[0].strip())
                elif line.strip():
                    existing_ids.add(line.strip())

    if str(user_id) not in existing_ids:
        with open('users.txt', 'a', encoding='utf-8') as f:
            f.write(f"{user_entry}\n")

# أمر عرض الإحصائيات
@bot.message_handler(commands=['stats'])
def show_stats(message):
    if not os.path.exists('users.txt'):
        bot.reply_to(message, "📊 **إحصائيات البوت:**\n\nلا يوجد مستخدمين مسجلين حتى الآن.")
        return
    with open('users.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    count = len(lines)
    recent_users = lines[-20:]
    users_formatted = "\n".join([f"👤 `{u}`" for u in recent_users])

    text = (
        f"📊 **إحصائيات البوت:**\n\n"
        f"عدد المستخدِمين الإجمالي: **{count}** مستخدم.\n\n"
        f"📋 **قائمة أحدث المشتركين:**\n"
        f"{users_formatted}"
    )
    bot.reply_to(message, text, parse_mode="Markdown")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user = message.from_user
    save_user(user)
    if user.id not in user_points:
        user_points[user.id] = 0
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔗 1. تابعنا على إنستغرام (@mah__asw)", url=INSTAGRAM_URL))
    markup.add(InlineKeyboardButton("✅ 2. تم الاشتراك، متابعة", callback_data="done_insta"))
    
    bot.send_message(
        message.chat.id,
        f"مرحباً بك في بوت تحميل الفيديوهات الشامل! 🚀\n\n"
        f"💰 **رصيد نقاطك الحالي:** {get_points(user.id)} نقطة\n\n"
        f"للبدء، يرجى متابعة حسابنا على الإنستغرام أولاً ثم الضغط على زر التأكيد أدناه:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "done_insta")
def after_instagram(call):
    user_id = call.from_user.id
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 مشاهدة إعلان (+1 نقطة)", callback_data="open_ad_and_reward"))
    
    bot.edit_message_text(
        f"ممتاز! تم تأكيد المتابعة بنجاح ✅\n\n"
        f"💰 **نقاطك الحالية:** {get_points(user_id)} نقطة\n"
        f"*(ملاحظة: كل فيديو يتطلب 1 نقطة للتحميل)*.\n\n"
        f"اضغط على زر الإعلان أدناه لكسب نقاط والبدء بالتحميل:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# معالجة الضغط على زر الإعلان (إضافة +1 نقطة فوراً بشكل مخفي وفتح الرابط)
@bot.callback_query_handler(func=lambda call: call.data == "open_ad_and_reward")
def handle_ad_click(call):
    user_id = call.from_user.id
    
    # 1. إضافة 1 نقطة للرصيد تلقائياً في الخلفية
    add_point(user_id)
    
    # 2. تحويل المستخدم لفتح رابط الإعلان
    bot.answer_callback_query(call.id, url=AD_URL)
    
    # 3. تحديث الرسالة بالنقاط الجديدة
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 مشاهدة إعلان آخر (+1 نقطة)", callback_data="open_ad_and_reward"))
    
    try:
        bot.edit_message_text(
            f"✅ **تم إضافة +1 نقطة بنجاح!**\n\n"
            f"💰 **رصيد نقاطك الحالي:** {get_points(user_id)} نقاط.\n\n"
            f"📥 يمكنك الآن إرسال رابط أي فيديو لتحميله، أو الضغط مجدداً لكسب المزيد من النقاط:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    except Exception:
        pass

@bot.message_handler(func=lambda message: True)
def handle_download(message):
    user = message.from_user
    user_id = user.id
    save_user(user)
    text = message.text.strip()
    
    if text.startswith('http'):
        # التحقق من وجود نقطة واحدة على الأقل
        if get_points(user_id) < 1:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📢 مشاهدة إعلان لكسب +1 نقطة", callback_data="open_ad_and_reward"))
            
            bot.reply_to(
                message,
                f"⚠️ **رصيدك غير كافٍ!**\n\n"
                f"💰 **نقاطك الحالية:** {get_points(user_id)} نقطة.\n"
                f"تكلفة تحميل الفيديو: **1 نقطة**.\n\n"
                f"اضغط على زر الإعلان أدناه لكسب نقطة فوراً:",
                reply_markup=markup
            )
            return

        file_name = f"video_{user_id}.mp4"
        msg = bot.reply_to(message, "⏳ جاري تحميل الفيديو، يرجى الانتظار...")
        try:
            ydl_opts = {
                'outtmpl': file_name,
                'format': 'best/bestvideo+bestaudio/best',
                'max_filesize': 50 * 1024 * 1024,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                },
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([text])

            if os.path.exists(file_name):
                with open(file_name, 'rb') as vid:
                    bot.send_video(message.chat.id, vid)
                bot.delete_message(message.chat.id, msg.message_id)

                # خصم 1 نقطة بعد نجاح التحميل
                deduct_point(user_id)

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📢 مشاهدة إعلان (+1 نقطة)", callback_data="open_ad_and_reward"))
            
            bot.send_message(
                message.chat.id,
                f"✅ **تم التحميل بنجاح!** (تم خصم 1 نقطة)\n\n"
                f"💰 **رصيد نقاطك المتبقي:** {get_points(user_id)} نقطة.\n\n"
                f"💡 أرسل رابطاً آخر للتحميل أو شاهد إعلاناً لكسب نقطة جديدة:",
                reply_markup=markup
            )

        except Exception:
            bot.edit_message_text("❌ متعذر التحميل حالياً من هذا الرابط (تأكد من أن الحساب عام وليس خاص).", message.chat.id, msg.message_id)
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
    else:
        bot.reply_to(message, "الرجاء إرسال رابط فيديو صالح يبدأ بـ http أو إرسال /start للبدء.")

bot.infinity_polling(skip_pending=True)
