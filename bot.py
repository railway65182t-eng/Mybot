import os
import sys
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from telegram.error import (
    NetworkError,
    TimedOut,
    RetryAfter,
    TelegramError,
)

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
    sys.exit(1)

# ---------- HANDLERS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("✅ ربات با موفقیت روشن شد")
    except TelegramError as e:
        logger.warning(f"Reply failed: {e}")

# ---------- ERROR HANDLER ----------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    err = context.error

    if isinstance(err, RetryAfter):
        logger.warning(f"⏳ Rate limit – sleep {err.retry_after}s")
        await asyncio.sleep(err.retry_after)

    elif isinstance(err, TimedOut):
        logger.warning("⏱ Telegram timeout")

    elif isinstance(err, NetworkError):
        logger.warning("🌐 Network error – retrying")

    else:
        logger.exception("🔥 Unexpected error", exc_info=err)

# ---------- MAIN ----------
def main():
    while True:
        try:
            app = ApplicationBuilder().token(TOKEN).build()

            app.add_handler(CommandHandler("start", start))
            app.add_error_handler(error_handler)

            logger.info("🚀 Bot started successfully")
            app.run_polling(
                drop_pending_updates=True,
                close_loop=False
            )

        except Exception as e:
            logger.exception("💥 Bot crashed – restarting in 5s", exc_info=e)
            time.sleep(5)

if __name__ == "__main__":
    main()
