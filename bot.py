import os
import logging
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.critical("❌ BOT_TOKEN is not set")
    exit(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ربات با موفقیت روشن شد")

async def extract_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    file_path = 'downloaded_image.jpg'
    await file.download(file_path)

    img = Image.open(file_path)
    text = pytesseract.image_to_string(img, lang='fas')

    await update.message.reply_text(f"متن استخراج شده از تصویر:\n\n{text}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("extract_text", extract_text))
    app.run_polling()

if __name__ == "__main__":
    main()
