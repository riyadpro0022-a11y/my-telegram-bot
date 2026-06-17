import telebot
import requests
import io
from PIL import Image # স্টিকার PNG তে কনভার্ট করার জন্য
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- নতুন ইম্পোর্ট (resource code + ultra strong obfuscation এর জন্য) ---
import re
import zipfile
import base64
import zlib
import bz2
import marshal
import os
from urllib.parse import urljoin, urlparse
# ----------------------------------------------------------------

# --- Render-এর জন্য শুধুমাত্র এই ৩টি মডিউল ইম্পোর্ট করা হয়েছে ---
from flask import Flask
from threading import Thread
# ----------------------------------------------------------------

# আপনার বট টোকেন
BOT_TOKEN = "8824965090:AAFbKBCuKjLezl0GNvZ1AyCC5OJa7xH9g2A"
bot = telebot.TeleBot(BOT_TOKEN)

# স্টার্ট কমান্ড (মেইন কীবোর্ডে বাটন থাকবে)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    # মেইন বাটন (RESOURCE CODE বাটন বাদ দেওয়া হয়েছে)
    markup.row(KeyboardButton("🔗 𝗟𝗜𝗡𝗞 𝗧𝗢 𝗖𝗢𝗗𝗘"), KeyboardButton("🛡️ 𝗢𝗕𝗙𝗨𝗦𝗖𝗔𝗧𝗜𝗢𝗡"))
    markup.row(KeyboardButton("🆔 STICKER ID"), KeyboardButton("⬇️ STICKER DOWNLOAD"))

    user_name = message.from_user.first_name if message.from_user.first_name else "User"

    welcome_text = (
        f"👨‍🏫 <b>WELCOME, {user_name}!</b>\n\n"
        "<b>YOUR ULTRA-FAST EXTRACTOR & STICKER TOOL IS READY.</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "🔹 <b>TO GET SOURCE CODE:</b> <b>SEND ANY WEBSITE LINK DIRECTLY.</b>\n"
        "🔹 <b>OBFUSCATION:</b> <b>SEND CODE TO ULTRA-STRONGLY OBFUSCATE IT.</b>\n"
        "🔹 <b>STICKER ID:</b> <b>GET TELEGRAM STICKER FILE IDs.</b>\n"
        "🔹 <b>STICKER DOWNLOAD:</b> <b>DOWNLOAD ANY STICKER IN PNG.</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "⚡ <b>SYSTEM ONLINE & AWAITING COMMANDS...</b>"
    )
    bot.reply_to(message, welcome_text, parse_mode='HTML', reply_markup=markup)

# ----------------- MAIN BUTTON INSTRUCTIONS -----------------

@bot.message_handler(func=lambda m: m.text == "🔗 𝗟𝗜𝗡𝗞 𝗧𝗢 𝗖𝗢𝗗𝗘")
def link_instruction(message):
    bot.reply_to(message, "🌐 <b>SEND LINK:</b>\n<b>Provide any website URL directly (e.g., https://google.com).</b>", parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "🛡️ 𝗢𝗕𝗙𝗨𝗦𝗖𝗔𝗧𝗜𝗢𝗡")
def file_instruction(message):
    msg = bot.reply_to(message, "🛡️ <b>OBFUSCATION ACTIVE:</b>\n<b>Send any Python code now to ultra-strongly obfuscate it.</b>", parse_mode='HTML')
    bot.register_next_step_handler(msg, process_obfuscation)

@bot.message_handler(func=lambda m: m.text == "🆔 STICKER ID")
def sticker_id_instruction(message):
    bot.reply_to(message, "👾 <b>SEND ANY STICKER:</b>\n<b>Send a sticker directly to get ID and Download options.</b>", parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "⬇️ STICKER DOWNLOAD")
def sticker_dl_instruction(message):
    msg = bot.reply_to(message, "⬇️ <b>SEND STICKER ID:</b>\n<b>Paste the Sticker File ID to download it as a PNG file.</b>", parse_mode='HTML')
    bot.register_next_step_handler(msg, process_manual_sticker_download)


# ----------------- CORE FUNCTIONS -----------------

# ১. আল্ট্রা-ফাস্ট লিংক প্রসেসিং (resource থাকলে ZIP, না থাকলে শুধু HTML)
@bot.message_handler(func=lambda message: message.text.startswith("http") or "." in message.text)
def handle_link(message):
    if message.text in ["🔗 𝗟𝗜𝗡𝗞 𝗧𝗢 𝗖𝗢𝗗𝗘", "🛡️ 𝗢𝗕𝗙𝗨𝗦𝗖𝗔𝗧𝗜𝗢𝗡", "🆔 STICKER ID", "⬇️ STICKER DOWNLOAD"]: return

    url = message.text.strip()
    if not url.startswith("http"): url = "https://" + url

    wait_msg = bot.reply_to(message, "🟥⬜⬜⬜")

    try:
        bot.edit_message_text("🟨🟨⬜⬜", chat_id=message.chat.id, message_id=wait_msg.message_id)

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        bot.edit_message_text("🟩🟩🟩⬜", chat_id=message.chat.id, message_id=wait_msg.message_id)

        source_code = response.text
        domain = url.split("//")[-1].split("/")[0]

        # সব CSS এবং JS লিংক খুঁজে বের করা
        css_links = re.findall(r'<link[^>]+href=["\']([^"\']+\.css[^"\']*)["\']', source_code, re.IGNORECASE)
        js_links = re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', source_code, re.IGNORECASE)
        all_links = list(dict.fromkeys(css_links + js_links))  # ডুপ্লিকেট বাদ

        # ----- যদি resource থাকে: ZIP করে পাঠানো -----
        if all_links:
            zip_stream = io.BytesIO()
            count = 0
            with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zf:
                # মূল HTML টাও ZIP এ রাখা
                zf.writestr(f"{domain}_original.html", source_code)
                for link in all_links:
                    full_url = urljoin(url, link)
                    try:
                        r = requests.get(full_url, headers=headers, timeout=10)
                        if r.status_code == 200:
                            name = os.path.basename(urlparse(full_url).path) or f"file_{count}"
                            if not name.endswith(('.css', '.js')):
                                name += ".txt"
                            zf.writestr(f"{count}_{name}", r.content)
                            count += 1
                    except requests.exceptions.RequestException:
                        continue

            zip_stream.seek(0)
            zip_stream.name = f"{domain}_full.zip"
            size_in_bytes = zip_stream.getbuffer().nbytes
            file_size = f"<b>{size_in_bytes / 1024:.2f}</b> KB" if size_in_bytes < 1024 * 1024 else f"<b>{size_in_bytes / (1024 * 1024):.2f}</b> MB"

            caption_text = (
                "✅ <b>SOURCE + RESOURCE EXTRACTED!</b>\n\n"
                "📁 <b>FILE NAME:</b>\n"
                f"<code>{domain}_full.zip</code>\n\n"
                "📦 <b>FILE SIZE:</b>\n"
                f"{file_size}\n\n"
                f"📦 <b>RESOURCE FILES:</b> <code>{count}</code>\n"
                "• 📄 <b>HTML Source</b>\n"
                "• 🎨 <b>CSS Files</b>\n"
                "• ⚙️ <b>JS Files</b>\n"
                "<b>━━━━━━━━━━━━━━━━</b>\n"
                "✅ <b>EVERYTHING IN ONE ZIP!</b>"
            )

            bot.edit_message_text("🟩🟩🟩🟩", chat_id=message.chat.id, message_id=wait_msg.message_id)
            bot.send_document(message.chat.id, zip_stream, caption=caption_text, parse_mode='HTML')
            bot.delete_message(message.chat.id, wait_msg.message_id)

        # ----- যদি resource না থাকে: শুধু HTML source পাঠানো -----
        else:
            file_name = f"{domain}_original.html"
            file_bytes = source_code.encode('utf-8')
            size_in_bytes = len(file_bytes)
            file_size = f"<b>{size_in_bytes / 1024:.2f}</b> KB" if size_in_bytes < 1024 * 1024 else f"<b>{size_in_bytes / (1024 * 1024):.2f}</b> MB"

            file_stream = io.BytesIO(file_bytes)
            file_stream.name = file_name

            caption_text = (
                "✅ <b>HTML EXTRACTION COMPLETE!</b>\n\n"
                "📁 <b>FILE NAME:</b>\n"
                f"<code>{file_name}</code>\n\n"
                "📦 <b>FILE SIZE:</b>\n"
                f"{file_size}\n\n"
                "⚡ <b>EXTRACTED FEATURES:</b>\n"
                "• 🌍 <b>Live URL Fetch</b>\n"
                "• 📄 <b>Clean HTML Export</b>\n"
                "• ⚡ <b>Ultra Fast Processing</b>\n"
                "<b>━━━━━━━━━━━━━━━━</b>\n"
                "✅ <b>YOUR HTML FILE IS READY!</b>"
            )

            bot.edit_message_text("🟩🟩🟩🟩", chat_id=message.chat.id, message_id=wait_msg.message_id)
            bot.send_document(message.chat.id, file_stream, caption=caption_text, parse_mode='HTML')
            bot.delete_message(message.chat.id, wait_msg.message_id)

    except requests.exceptions.RequestException as e:
        bot.edit_message_text(f"❌ <b>ERROR:</b> <code>{e}</code>", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='HTML')


# ১-বি. ULTRA STRONG OBFUSCATION — Python কোড multi-layer obfuscate করে
def process_obfuscation(message):
    if message.text in ["🔗 𝗟𝗜𝗡𝗞 𝗧𝗢 𝗖𝗢𝗗𝗘", "🛡️ 𝗢𝗕𝗙𝗨𝗦𝗖𝗔𝗧𝗜𝗢𝗡", "🆔 STICKER ID", "⬇️ STICKER DOWNLOAD"]:
        return

    code = message.text
    wait_msg = bot.reply_to(message, "🛡️ <b>Ultra-obfuscating your code...</b>", parse_mode='HTML')

    try:
        # ===== ULTRA STRONG MULTI-LAYER OBFUSCATION =====
        # ধাপ ১: compile -> marshal (bytecode)
        layer = marshal.dumps(compile(code, "<obf>", "exec"))
        # ধাপ ২: zlib compress
        layer = zlib.compress(layer, 9)
        # ধাপ ৩: dynamic key দিয়ে multi-round XOR
        key = os.urandom(32)
        xored = bytes(b ^ key[i % len(key)] for i, b in enumerate(layer))
        # ধাপ ৪: bz2 compress
        layer = bz2.compress(xored, 9)
        # ধাপ ৫: base85 encode
        layer = base64.b85encode(layer)
        k_enc = base64.b85encode(key)

        # স্ব-চালিত (self-running) ultra obfuscated র‍্যাপার তৈরি
        obfuscated = (
            "import marshal,zlib,bz2,base64\n"
            f"_k=base64.b85decode({k_enc!r})\n"
            f"_d=bz2.decompress(base64.b85decode({layer!r}))\n"
            "_x=bytes(b^_k[i%len(_k)] for i,b in enumerate(_d))\n"
            "exec(marshal.loads(zlib.decompress(_x)))\n"
        )

        file_stream = io.BytesIO(obfuscated.encode('utf-8'))
        file_stream.name = "obfuscated_by_Professor.py"

        caption_text = (
            "✅ <b>ULTRA STRONG OBFUSCATION COMPLETE!</b>\n\n"
            "🛡️ <b>5 LAYERS APPLIED:</b>\n"
            "• 🧬 <b>Marshal Bytecode</b>\n"
            "• 🗜️ <b>Zlib Compression</b>\n"
            "• 🔐 <b>Dynamic XOR Cipher</b>\n"
            "• 📦 <b>BZ2 Compression</b>\n"
            "• 🧩 <b>Base85 Encoding</b>\n"
            "<b>━━━━━━━━━━━━━━━━</b>\n"
            "👑 <b>Powered by 𝐏𝐑𝐎𝐅𝐄𝐒𝐒𝐎𝐑 ✗</b>"
        )

        bot.send_document(message.chat.id, file_stream, caption=caption_text, parse_mode='HTML')
        bot.delete_message(message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ <b>ERROR: Invalid Python code.</b>\n<code>{e}</code>", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='HTML')


# ২. স্মার্ট স্টিকার সেন্ড করলে ইনলাইন বাটন আসবে
@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    markup = InlineKeyboardMarkup()
    btn_id = InlineKeyboardButton("🆔 GET ID", callback_data="get_id")
    btn_dl = InlineKeyboardButton("⬇️ DOWNLOAD", callback_data="dl_sticker")
    markup.add(btn_id, btn_dl)

    bot.reply_to(message, "👾 <b>STICKER DETECTED!</b>\n<b>Choose an option below:</b>", parse_mode='HTML', reply_markup=markup)


# ৩. ইনলাইন বাটনের কাজ (ID দেখানো এবং Download করা)
@bot.callback_query_handler(func=lambda call: call.data in ["get_id", "dl_sticker"])
def sticker_callback(call):
    try:
        original_msg = call.message.reply_to_message
        if not original_msg or not original_msg.sticker:
            bot.answer_callback_query(call.id, "❌ Error: Sticker not found!", show_alert=True)
            return

        sticker_id = original_msg.sticker.file_id

        # GET ID এ ট্যাপ করলে
        if call.data == "get_id":
            bot.edit_message_text(f"🆔 <b>STICKER ID:</b>\n\n<code>{sticker_id}</code>\n\n💡 <i>Tap the ID above to copy it!</i>",
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  parse_mode='HTML')
            bot.answer_callback_query(call.id)

        # DOWNLOAD এ ট্যাপ করলে
        elif call.data == "dl_sticker":
            bot.answer_callback_query(call.id, "Processing your download...")
            bot.edit_message_text("⏳ <b>Downloading & Processing sticker...</b>",
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  parse_mode='HTML')

            file_info = bot.get_file(sticker_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_ext = file_info.file_path.split('.')[-1]

            if file_ext.lower() == 'webp':
                img = Image.open(io.BytesIO(downloaded_file)).convert("RGBA")
                file_stream = io.BytesIO()
                img.save(file_stream, format="PNG")
                file_stream.seek(0)
                file_name = "Sticker_By_Professor.png"
            else:
                file_stream = io.BytesIO(downloaded_file)
                file_name = f"Sticker_By_Professor.{file_ext}"

            file_stream.name = file_name

            caption_text = (
                "✅ <b>STICKER DOWNLOADED!</b>\n\n"
                f"📥 <b>Format:</b> <code>{file_name.split('.')[-1].upper()}</code>\n"
                "💡 <i>Click the 3 dots (⋮) and select <b>'Save to Downloads'</b>.</i>\n\n"
                "👑 <b>Powered by 𝐏𝐑𝐎𝐅𝐄𝐒𝐒𝐎𝐑 ✗</b>"
            )

            bot.send_document(call.message.chat.id, file_stream, caption=caption_text, parse_mode='HTML')
            bot.delete_message(call.message.chat.id, call.message.message_id)

    except Exception as e:
        bot.answer_callback_query(call.id, "❌ Error processing sticker!", show_alert=True)
        bot.edit_message_text(f"❌ <b>ERROR:</b> <code>{e}</code>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='HTML')


# ৪. ম্যানুয়াল স্টিকার ডাউনলোডার (যদি কেউ "⬇️ STICKER DOWNLOAD" মেইন বাটনে ক্লিক করে আইডি দেয়)
def process_manual_sticker_download(message):
    if message.text in ["🔗 𝗟𝗜𝗡𝗞 𝗧𝗢 𝗖𝗢𝗗𝗘", "🛡️ 𝗢𝗕𝗙𝗨𝗦𝗖𝗔𝗧𝗜𝗢𝗡", "🆔 STICKER ID", "⬇️ STICKER DOWNLOAD"]:
        return

    file_id = message.text.strip()
    wait_msg = bot.reply_to(message, "⏳ <b>Downloading & Processing sticker...</b>", parse_mode='HTML')

    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        file_ext = file_info.file_path.split('.')[-1]

        if file_ext.lower() == 'webp':
            img = Image.open(io.BytesIO(downloaded_file)).convert("RGBA")
            file_stream = io.BytesIO()
            img.save(file_stream, format="PNG")
            file_stream.seek(0)
            file_name = "Sticker_By_Professor.png"
        else:
            file_stream = io.BytesIO(downloaded_file)
            file_name = f"Sticker_By_Professor.{file_ext}"

        file_stream.name = file_name

        caption_text = (
            "✅ <b>STICKER DOWNLOADED!</b>\n\n"
            f"📥 <b>Format:</b> <code>{file_name.split('.')[-1].upper()}</code>\n"
            "💡 <i>Click the 3 dots (⋮) and select <b>'Save to Downloads'</b>.</i>\n\n"
            "👑 <b>Powered by 𝐏𝐑𝐎𝐅𝐄𝐒𝐒𝐎𝐑 ✗</b>"
        )

        bot.send_document(message.chat.id, file_stream, caption=caption_text, parse_mode='HTML')
        bot.delete_message(message.chat.id, wait_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ <b>ERROR: Invalid Sticker ID or file format not supported.</b>", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='HTML')


# ----------------- RENDER DUMMY WEB SERVER -----------------
# Render-এ পোর্ট ওপেন রাখার জন্য এই অংশটুকু যুক্ত করা হয়েছে
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    server_thread = Thread(target=run_server)
    server_thread.start()

    print("SYSTEM READY... WAITING FOR TELEGRAM COMMANDS! 🚀")
    bot.infinity_polling()
