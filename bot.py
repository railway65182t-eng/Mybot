import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ----------- LOGGING -----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

# ----------- HANDLERS -----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # پیامی که به محض ورود کاربر ظاهر می‌شود
    welcome_message = "سلام و خوش آمدید! 🎉\n\nامکانات ربات ما به شرح زیر است:\n"
    menu = [["خلاصه‌سازی متن 📝", "استخراج متن از تصویر 🖼️"], ["پشتیبانی 💬", "راهنمایی و آموزش 🧑‍🏫"]]

    # ارسال پیام خوش آمدگویی و نمایش منو
    await update.message.reply_text(
        welcome_message,
        reply_markup=ReplyKeyboardMarkup(menu, one_time_keyboard=True)
    )

# ----------- MAIN ----------
def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()

if __name__ == "__main__":
    main()
