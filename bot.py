import os
import telebot

TOKEN = os.getenv("8584046657:AAGk-Q65y-pmwr6dnAYiLIl1Oe6nuFaqkOI")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام! ربات فعاله ✅")

print("Bot is running...")
bot.infinity_polling()
