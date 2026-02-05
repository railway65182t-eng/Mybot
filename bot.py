import os
import sys
import logging
import asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.error import (
    TelegramError,
    NetworkError,
    TimedOut,
    RetryAfter,
)

# ================== LOGGING ==================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("MyBot")

# ================== TOKEN ==================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.critical("❌ BOT_TOKEN is not set")
    sys.exit(1)

SUPPORT_ID = "https://t.me/Aliasghar_Darvishpour"

# ================== KEYBOARDS ==================
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 خلاصه متن", callback_data="soon")],
        [InlineKeyboardButton("🖼 استخراج متن از تصویر", callback_data="soon")],
        [InlineKeyboardButton("💬 پشتیبانی", callback_data="support")],
    ])

def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ بازگشت به منو", callback_data="menu")]
    ])

# ================== HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 خوش آمدی!\n\n"
        "این ربات به‌زودی ابزارهای هوشمند برای خلاصه‌سازی متن و استخراج متن از تصویر ارائه می‌دهد.\n\n"
        "از منوی زیر استفاده کن 👇",
        reply_markup=main_menu()
    )

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu":
        await query.edit_message_text(
            "🏠 منوی اصلی",
            reply_markup=main_menu()
        )

    elif query.data == "support":
        await query.edit_message_text(
            "🎧 پشتیبانی\n\n"
            "اگر سوال، مشکل یا پیشنهادی داری از طریق لینک زیر با پشتیبانی در ارتباط باش 👇\n\n"
            "⏱ پاسخگویی معمولاً کمتر از ۲۴ ساعت",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 ارتباط با پشتیبانی", url=SUPPORT_ID)],
                [InlineKeyboardButton("⬅️ بازگشت به منو", callback_data="menu")]
            ])
        )

    else:
        await query.edit_message_text(
            "⏳ این قابلیت به‌زودی فعال می‌شود.",
            reply_markup=back_menu()
        )

# ================== ERROR HANDLER ==================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    err = context.error

    if isinstance(err, RetryAfter):
        logger.warning(f"⏳ Rate limit – sleep {err.retry_after}s")
        await asyncio.sleep(err.retry_after)

    elif isinstance(err, TimedOut):
        logger.warning("⏱ Telegram timeout")

    elif isinstance(err, NetworkError):
        logger.warning("🌐 Network error")

    else:
        logger.exception("🔥 Unexpected error", exc_info=err)

# ================== MAIN ==================
def main():
    while True:
        try:
            app = ApplicationBuilder().token(TOKEN).build()

            app.add_handler(CommandHandler("start", start))
            app.add_handler(CallbackQueryHandler(callbacks))
            app.add_error_handler(error_handler)

            logger.info("✅ Bot started successfully")
            app.run_polling(
                drop_pending_updates=True,
                close_loop=False
            )

        except Exception as e:
            logger.exception("💥 Bot crashed – restarting in 5s", exc_info=e)
            asyncio.sleep(5)

if __name__ == "__main__":
    main()
