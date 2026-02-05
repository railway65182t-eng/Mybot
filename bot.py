import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# تنظیمات لاگ
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات
TOKEN = os.getenv("BOT_TOKEN")

# تعریف دستور استارت و منو
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("خلاصه‌سازی متن", callback_data='summarize')],
        [InlineKeyboardButton("استخراج متن از تصویر", callback_data='extract')],
        [InlineKeyboardButton("پشتیبانی", callback_data='support')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! ربات آماده است. لطفا از منوی زیر یکی از گزینه‌ها را انتخاب کنید.", reply_markup=reply_markup)

# هنگامی که کاربر روی دکمه‌ها کلیک می‌کند
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'summarize':
        await query.edit_message_text("📑 شما گزینه خلاصه‌سازی متن را انتخاب کردید.")
    elif query.data == 'extract':
        await query.edit_message_text("📸 شما گزینه استخراج متن از تصویر را انتخاب کردید.")
    elif query.data == 'support':
        await query.edit_message_text("💬 پشتیبانی در حال آماده‌سازی است.")

# تنظیمات اصلی ربات
def main():
    # ساخت برنامه ربات
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    app = ApplicationBuilder().token(TOKEN).build()

    # افزودن هندلرهای مختلف
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    # شروع ربات
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
