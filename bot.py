import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.error import TelegramError

# ---------- LOGGING ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("MyBot")

# ---------- TOKEN ----------
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    logger.critical("❌ BOT_TOKEN is not set")
    exit(1)

# ---------- HANDLERS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ارسال پیام خوشامدگویی با دکمه‌های inline برای منو
    keyboard = [
        [
            InlineKeyboardButton("خلاصه متن", callback_data='summarize'),
            InlineKeyboardButton("استخراج متن از تصویر", callback_data='extract_text'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text="سلام! از ربات ما خوش آمدید 😊\nلطفاً یک گزینه را انتخاب کنید:",
        reply_markup=reply_markup
    )

# ---------- CALLBACK HANDLER ----------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'summarize':
        await query.edit_message_text(text="شما گزینه خلاصه متن را انتخاب کردید.")
    elif query.data == 'extract_text':
        await query.edit_message_text(text="شما گزینه استخراج متن از تصویر را انتخاب کردید.")

# ---------- ERROR HANDLER ----------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    err = context.error
    logger.exception("خطا در ربات:", exc_info=err)

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_error_handler(error_handler)

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
