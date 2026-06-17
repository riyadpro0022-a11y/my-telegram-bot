import telebot
import requests
import io
from PIL import Image # স্টিকার PNG তে কনভার্ট করার জন্য
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- নতুন ইম্পোর্ট ---
import re
import zipfile
import base64
import zlib
import bz2
import lzma
import marshal
import hashlib
import os
from urllib.parse import urljoin, urlparse

# --- AES-256 এর জন্য (যেকোনো ভাষা সাপোর্ট) ---
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad
# ----------------------------------------------------------------

# --- Render-এর জন্য ---
from flask import Flask
from threading import Thread
# ----------------------------------------------------------------

BOT_TOKEN = "8824965090:AAFbKBCuKjLezl0GNvZ1AyCC5OJa7xH9g2A"
bot = telebot.TeleBot(BOT_TOKEN)

BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# obfuscation এর গোপন পাসফ্রেজ (চাইলে বদলান)
SECRET_PASSPHRASE = "PROFESSOR_X_ULTRA_SECRET_2024"


# স্টার্ট কমান্ড
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🔗 𝗟𝗜𝗡𝗞 𝗧𝗢 𝗖𝗢𝗗𝗘"), KeyboardButton("🛡️ 𝗢𝗕𝗙𝗨𝗦𝗖𝗔𝗧𝗜𝗢𝗡"))
    markup.row(KeyboardButton("🆔 STICKER ID"), KeyboardButton("⬇️ STICKER DOWNLOAD"))

    user_name = message.from_user.first_name if message.from_user.first_name else "User"

    welcome_text = (
        f"👨‍🏫 <b>WELCOME, {user_name}!</b>\n\n"
        "<b>YOUR ULTRA-FAST EXTRACTOR & STICKER TOOL IS READY.</b>\n"
        "<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>\n"
        "🔹 <b>TO GET SOURCE CODE:</b> <b>SEND ANY WEBSITE LINK DIRECTLY.</b>\n"
        "🔹 <b>OBFUSCATION:</b> <b>SEND CODE OR ANY FILE (ANY LANGUAGE) TO ENCRYPT IT.</b>\n"
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
    msg = bot.reply_to(message, "🛡️ <b>OBFUSCATION ACTIVE:</b>\n<b>Send any code or upload ANY file (Python, JS, PHP, etc.) to ultra-strongly encrypt it.</b>", parse_mode='HTML')
    bot.register_next_step_handler(msg, process_obfuscation_text)

@bot.message_handler(func=lambda m: m.text == "🆔 STICKER ID")
def sticker_id_instruction(message):
    bot.reply_to(message, "👾 <b>SEND ANY STICKER:</b>\n<b>Send a sticker directly to get ID and Download options.</b>", parse_mode='HTML')

@bot.message_handler(func=lambda m: m.text == "⬇️ STICKER DOWNLOAD")
def sticker_dl_instruction(message):
    msg = bot.reply_to(message, "⬇️ <b>SEND STICKER ID:</b>\n<b>Paste the Sticker File ID to download it as a PNG file.</b>", parse_mode='HTML')
    bot.register_next_step_handler(msg, process_manual_sticker_download)


# ----------------- CORE FUNCTIONS -----------------

# ১. লিংক প্রসেসিং (resource থাকলে ZIP, না থাকলে শুধু HTML)
@bot.message_handler(func=lambda message: message.text.startswith("http") or "." in message.text)
def handle_link(message):
    if message.text in ["🔗 𝗟𝗜𝗡𝗞 𝗧𝗢 𝗖𝗢𝗗𝗘", "🛡️ 𝗢𝗕𝗙𝗨𝗦𝗖𝗔𝗧𝗜𝗢𝗡", "🆔 STICKER ID", "⬇️ STICKER DOWNLOAD"]: return

    url = message.text.strip()
    if not url.startswith("http"): url = "https://" + url

    wait_msg = bot.reply_to(message, "🟥⬜⬜⬜")

    try:
        bot.edit_message_text("🟨🟨⬜⬜", chat_id=message.chat.id, message_id=wait_msg.message_id)

        headers = dict(BROWSER_HEADERS)
        headers['Referer'] = url

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        bot.edit_message_text("🟩🟩🟩⬜", chat_id=message.chat.id, message_id=wait_msg.message_id)

        source_code = response.text
        domain = url.split("//")[-1].split("/")[0]

        css_links = re.findall(r'<link[^>]+href=["\']([^"\']+\.css[^"\']*)["\']', source_code, re.IGNORECASE)
        js_links = re.findall(r'<script[^>]+src=["\']([^"\']+\.js[^"\']*)["\']', source_code, re.IGNORECASE)
        all_links = list(dict.fromkeys(css_links + js_links))

        if all_links:
            zip_stream = io.BytesIO()
            count = 0
            with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(f"{domain}_original.html", source_code)
                for link in all_links:
                    full_url = urljoin(url, link)
                    try:
                        r = requests.get(full_url, headers=headers, timeout=15)
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

    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        if status in (401, 403):
            err_txt = (
                f"🚫 <b>ACCESS BLOCKED (Error {status})</b>\n\n"
                "<b>This website blocks bots/automated requests.</b>\n"
                "<i>Try another URL, or a site that allows direct fetching.</i>"
            )
        else:
            err_txt = f"❌ <b>HTTP ERROR {status}:</b> <code>{e}</code>"
        bot.edit_message_text(err_txt, chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='HTML')

    except requests.exceptions.RequestException as e:
        bot.edit_message_text(f"❌ <b>ERROR:</b> <code>{e}</code>", chat_id=message.chat.id, message_id=wait_msg.message_id, parse_mode='HTML')


# ============================================================
#   ULTRA STRONG OBFUSCATION (যেকোনো ভাষা / যেকোনো ফাইল)
# ============================================================

def _multi_layer_encrypt(raw_bytes):
    """raw bytes কে multi-layer (compress + AES-256 + XOR + encode) এনক্রিপ্ট করে।"""
    # ১: triple compression (zlib -> bz2 -> lzma)
    data = zlib.compress(raw_bytes, 9)
    data = bz2.compress(data, 9)
    data = lzma.compress(data)

    # ২: dynamic salt + AES-256 (CBC) — পাসফ্রেজ থেকে কী derive
    salt = os.urandom(16)
    aes_key = PBKDF2(SECRET_PASSPHRASE, salt, dkLen=32, count=200000)
    iv = os.urandom(16)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    data = cipher.encrypt(pad(data, AES.block_size))

    # ৩: multi-round XOR (random 64-byte key)
    xkey = os.urandom(64)
    data = bytes(b ^ xkey[i % len(xkey)] for i, b in enumerate(data))

    # ৪: base85 encode সব অংশ
    return {
        'salt': base64.b85encode(salt).decode(),
        'iv': base64.b85encode(iv).decode(),
        'xkey': base64.b85encode(xkey).decode(),
        'data': base64.b85encode(data).decode(),
    }


def obfuscate_python(code_str):
    """Python হলে: bytecode + AES multi-layer — self-running .py ফেরত।"""
    bytecode = marshal.dumps(compile(code_str, "<obf>", "exec"))
    p = _multi_layer_encrypt(bytecode)

    return (
        "import marshal,zlib,bz2,lzma,base64\n"
        "from Crypto.Cipher import AES\n"
        "from Crypto.Protocol.KDF import PBKDF2\n"
        "from Crypto.Util.Padding import unpad\n"
        f"_p={SECRET_PASSPHRASE!r}\n"
        f"_s=base64.b85decode({p['salt']!r})\n"
        f"_iv=base64.b85decode({p['iv']!r})\n"
        f"_xk=base64.b85decode({p['xkey']!r})\n"
        f"_d=base64.b85decode({p['data']!r})\n"
        "_d=bytes(b^_xk[i%len(_xk)] for i,b in enumerate(_d))\n"
        "_k=PBKDF2(_p,_s,dkLen=32,count=200000)\n"
        "_d=unpad(AES.new(_k,AES.MODE_CBC,_iv).decrypt(_d),16)\n"
        "_d=lzma.decompress(_d);_d=bz2.decompress(_d);_d=zlib.decompress(_d)\n"
        "exec(marshal.loads(_d))\n"
    )


def obfuscate_any(raw_bytes, original_name):
    """যেকোনো ভাষা/ফাইল হলে: AES multi-layer encrypt + Python decryptor সহ ফেরত।"""
    p = _multi_layer_encrypt(raw_bytes)
    safe_name = original_name.replace("'", "")

    # self-decrypting Python script যা ডিক্রিপ্ট করে আসল ফাইল ফিরিয়ে দেয়
    return (
        "# Run this file with Python to restore the original protected file.\n"
        "import zlib,bz2,lzma,base64\n"
        "from Crypto.Cipher import AES\n"
        "from Crypto.Protocol.KDF import PBKDF2\n"
        "from Crypto.Util.Padding import unpad\n"
        f"_p={SECRET_PASSPHRASE!r}\n"
        f"_name={safe_name!r}\n"
        f"_s=base64.b85decode({p['salt']!r})\n"
        f"_iv=base64.b85decode({p['iv']!r})\n"
        f"_xk=base64.b85decode({p['xkey']!r})\n"
        f"_d=base64.b85decode({p['data']!r})\n"
        "_d=bytes(b^_xk[i%len(_xk)] for i,b in enumerate(_d))\n"
        "_k=PBKDF2(_p,_s,dkLen=32,count=200000)\n"
        "_d=unpad(AES.new(_k,AES.MODE_CBC,_iv).decrypt(_d),16)\n"
        "_d=lzma.decompress(_d);_d=bz2.decompress(_d);_d=zlib.decompress(_d)\n"
        "open('restored_'+_name,'wb').write(_d)\n"
        "print('Restored ->','restored_'+_name)\n"
    )


def send_obfuscated_text(chat_id, code_str, wait_msg_id=None):
    """text ইনপুট: Python হলে python-obfuscate, না হলে generic encrypt।"""
    try:
        try:
            obfuscated = obfuscate_python(code_str)  # Python হিসেবে চেষ্টা
            mode = "PYTHON (Bytecode + AES-256)"
        except SyntaxError:
            obfuscated = obfuscate_any(code_str.encode('utf-8'), "code.txt")  # অন্য ভাষা
            mode = "ANY LANGUAGE (AES-256)"

        file_stream = io.BytesIO(obfuscated.encode('utf-8'))
        file_stream.name = "obfuscated_by_Professor.py"
        _send_obf_doc(chat_id, file_stream, mode, wait_msg_id)
    except Exception as e:
        _obf_error(chat_id, e, wait_msg_id)


def _send_obf_doc(chat_id, file_stream, mode, wait_msg_id):
    caption_text = (
        "✅ <b>ULTRA STRONG ENCRYPTION COMPLETE!</b>\n\n"
        f"🔧 <b>MODE:</b> <code>{mode}</code>\n"
        "🛡️ <b>LAYERS APPLIED:</b>\n"
        "• 🗜️ <b>Zlib + BZ2 + LZMA (Triple Compress)</b>\n"
        "• 🔐 <b>AES-256 (PBKDF2, 200k rounds)</b>\n"
        "• 🧬 <b>64-byte Dynamic XOR Cipher</b>\n"
        "• 🧩 <b>Base85 Multi-Encoding</b>\n"
        "<b>━━━━━━━━━━━━━━━━</b>\n"
        "👑 <b>Powered by 𝐏𝐑𝐎𝐅𝐄𝐒𝐒𝐎𝐑 ✗</b>"
    )
    bot.send_document(chat_id, file_stream, caption=caption_text, parse_mode='HTML')
    if wait_msg_id:
        bot.delete_message(chat_id, wait_msg_id)


def _obf_error(chat_id, e, wait_msg_id):
    err = f"❌ <b>ERROR during obfuscation.</b>\n<code>{e}</code>"
    if wait_msg_id:
        bot.edit_message_text(err, chat_id=chat_id, message_id=wait_msg_id, parse_mode='HTML')
    else:
        bot.send_message(chat_id, err, parse_mode='HTML')


# OBFUSCATION বাটন থেকে আসা ইনপুট হ্যান্ডেল
def process_obfuscation_text(message):
    if message.content_type == 'document':
        handle_document(message)
        return
    if not message.text or message.text in ["🔗 𝗟𝗜𝗡𝗞 𝗧𝗢 𝗖𝗢𝗗𝗘", "🛡️ 𝗢𝗕𝗙𝗨𝗦𝗖𝗔𝗧𝗜𝗢𝗡", "🆔 STICKER ID", "⬇️ STICKER DOWNLOAD"]:
        return
    wait_msg = bot.reply_to(message, "🛡️ <b>Ultra-encrypting your code...</b>", parse_mode='HTML')
    send_obfuscated_text(message.chat.id, message.text, wait_msg.message_id)


# যেকোনো FILE আপলোড করলেই auto-obfuscate (বাটন না টিপেও, যেকোনো ভাষা)
@bot.message_handler(content_types=['document'])
def handle_document(message):
    wait_msg = bot.reply_to(message, "🛡️ <b>File received! Ultra-encrypting (any language)...</b>", parse_mode='HTML')
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        original_name = message.document.file_name or "file.txt"

        # Python ফাইল হলে bytecode obfuscation চেষ্টা, নাহলে generic AES encrypt
        is_py = original_name.lower().endswith('.py')
        try:
            if is_py:
                obfuscated = obfuscate_python(downloaded.decode('utf-8', errors='strict'))
                mode = "PYTHON (Bytecode + AES-256)"
            else:
                raise SyntaxError  # generic পথে যাওয়ার জন্য
        except (SyntaxError, UnicodeDecodeError):
            obfuscated = obfuscate_any(downloaded, original_name)
            mode = "ANY LANGUAGE (AES-256)"

        file_stream = io.BytesIO(obfuscated.encode('utf-8'))
        file_stream.name = "obfuscated_by_Professor.py"
        _send_obf_doc(message.chat.id, file_stream, mode, wait_msg.message_id)

    except Exception as e:
        _obf_error(message.chat.id, e, wait_msg.message_id)


# ২. স্টিকার সেন্ড করলে ইনলাইন বাটন
@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    markup = InlineKeyboardMarkup()
    btn_id = InlineKeyboardButton("🆔 GET ID", callback_data="get_id")
    btn_dl = InlineKeyboardButton("⬇️ DOWNLOAD", callback_data="dl_sticker")
    markup.add(btn_id, btn_dl)
    bot.reply_to(message, "👾 <b>STICKER DETECTED!</b>\n<b>Choose an option below:</b>", parse_mode='HTML', reply_markup=markup)


# ৩. ইনলাইন বাটনের কাজ
@bot.callback_query_handler(func=lambda call: call.data in ["get_id", "dl_sticker"])
def sticker_callback(call):
    try:
        original_msg = call.message.reply_to_message
        if not original_msg or not original_msg.sticker:
            bot.answer_callback_query(call.id, "❌ Error: Sticker not found!", show_alert=True)
            return

        sticker_id = original_msg.sticker.file_id

        if call.data == "get_id":
            bot.edit_message_text(f"🆔 <b>STICKER ID:</b>\n\n<code>{sticker_id}</code>\n\n💡 <i>Tap the ID above to copy it!</i>",
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  parse_mode='HTML')
            bot.answer_callback_query(call.id)

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


# ৪. ম্যানুয়াল স্টিকার ডাউনলোডার
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
