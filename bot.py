import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from google import genai

# Key গুলো Render থেকে আসবে (নিরাপদ!)
TELEGRAM_TOKEN = os.environ.get("8799723853:AAFaGSUneNpvDGgPTosCw0mZC5M5EHCgnjc")
GEMINI_API_KEY = os.environ.get("AIzaSyDdEjCOdYEGJMZnr0T-rYWwvcvIWl7Bg-M")

client = genai.Client(api_key=GEMINI_API_KEY)
chat_histories = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"হ্যালো {name}! 👋\n"
        f"আমি AI চ্যাটবট! 🤖\n"
        f"আমাকে কিছু জিজ্ঞেস করো!\n\n"
        f"/clear - আগের কথা মুছো"
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in chat_histories:
        del chat_histories[user_id]
    await update.message.reply_text("✅ আগের কথা মুছেছি!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    if user_id not in chat_histories:
        chat_histories[user_id] = []

    chat_histories[user_id].append({
        "role": "user",
        "parts": [{"text": user_message}],
    })

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=chat_histories[user_id],
            config={
                "system_instruction": "তুমি বাংলায় উত্তর দাও।",
                "temperature": 0.7,
                "max_output_tokens": 2048,
            },
        )

        bot_reply = response.text

        chat_histories[user_id].append({
            "role": "model",
            "parts": [{"text": bot_reply}],
        })

        if len(chat_histories[user_id]) > 20:
            chat_histories[user_id] = chat_histories[user_id][-20:]

        if len(bot_reply) > 4096:
            for i in range(0, len(bot_reply), 4096):
                await update.message.reply_text(bot_reply[i:i + 4096])
        else:
            await update.message.reply_text(bot_reply)

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("😥 সমস্যা! আবার চেষ্টা করো।")


def main():
    print("Bot ON! ✅")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    app.run_polling()


if __name__ == "__main__":
    main()
