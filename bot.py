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
user_ad_status = {}

def get_points(user_id):
    return user_points.get(user_id, 0)

def add_point(user_id):
    user_points[user_id] = get_points(user_id) + 1

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
    # زر الإعلان المربوط بـ Callback للزيادة المخفية
    markup.add(InlineKeyboardButton("📢 اضغط هنا لمشاهدة الإعلان وتفعيل التحميل", callback_data="open_ad_and_reward"))
    
    bot.edit_message_text(
        "ممتاز! تم تأكيد المتابعة بنجاح ✅\n\n"
        "الآن اضغط على زر الإعلان أدناه لفتحه كشرط إجباري وتفعيل التحميل تلقائياً:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# معالجة ضغطة زر الإعلان (إضافة النقطة خفية + فتح الرابط)
@bot.callback_query_handler(func=lambda call: call.data == "open_ad_and_reward")
def handle_ad_click(call):
    user_id = call.from_user.id
    
    # 1. إضافة النقطة والسماح بالتحميل في الخلفية
    add_point(user_id)
    user_ad_status[user_id] = True
    
    # 2. فتح رابط الإعلان فوراً للمستخدم عبر التلغرام
    bot.answer_callback_query(call.id, url=AD_URL)
    
    # 3. تحديث نص الرسالة لعرض النقاط الجديدة وتوجيهه للتحميل
    try:
        bot.edit_message_text(
            f"✅ **تم تسجيل مشاهدة الإعلان وإضافة +1 نقطة!**\n\n"
            f"💰 **نقاطك الحالية:** {get_points(user_id)} نقطة.\n\n"
            f"📥 يمكنك الآن إرسال رابط أي فيديو لتحميله مباشرة:",
            call.message.chat.id,
            call.message.message_id
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
        # التحقق من أن المستخدم ضغط على زر الإعلان
        if not user_ad_status.get(user_id, False):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📢 اضغط هنا لمشاهدة الإعلان أولاً", callback_data="open_ad_and_reward"))
            
            bot.reply_to(
                message,
                f"⚠️ **عذراً!** لا يمكنك تحميل الفيديو حتى تضغط على زر الإعلان أدناه أولاً:\n\n"
                f"💰 **نقاطك الحالية:** {get_points(user_id)} نقطة.",
                reply_markup=markup
            )
            return

        # إعادة ضبط حالة الإعلان للمرة القادمة
        user_ad_status[user_id] = False

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

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("📢 مشاهدة إعلان جديد كسب نقطة إضافية", callback_data="open_ad_and_reward"))
            
            bot.send_message(
                message.chat.id,
                f"✅ **تم التحميل بنجاح!**\n"
                f"💰 **رصيد نقاطك:** {get_points(user_id)} نقطة.\n\n"
                f"💡 لتحميل فيديو آخر، اضغط على زر الإعلان أدناه ثم أرسل الرابط:",
                reply_markup=markup
            )

        except Exception:
            user_ad_status[user_id] = True  # إرجاع الصلاحية في حال فشل التحميل
            bot.edit_message_text("❌ متعذر التحميل حالياً من هذا الرابط (تأكد من أن الحساب عام وليس خاص).", message.chat.id, msg.message_id)
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
    else:
        bot.reply_to(message, "الرجاء إرسال رابط فيديو صالح يبدأ بـ http أو إرسال /start للبدء.")

bot.infinity_polling(skip_pending=True)
        
