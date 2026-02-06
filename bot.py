from __future__ import annotations

import logging
import sys

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, FLOOD_WINDOW_SEC, FLOOD_MAX_MSG, FLOOD_MUTE_SEC, ADMIN_LOG_CHAT_ID
from db import init_db
from filters import FloodGuard
from group_features import (
    on_new_members,
    anti_content,
    cmd_rules,
    cmd_setrules,
    cmd_note,
    cmd_get,
    cmd_delnote,
    verify_callback,
)
from moderation import cmd_warn, cmd_warns, cmd_resetwarns, mute_user
from admin import cmd_panel, welcome_on, welcome_off, links_on, links_off, verify_on, verify_off

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("Mybot")

flood = FloodGuard(window_sec=FLOOD_WINDOW_SEC, max_msgs=FLOOD_MAX_MSG)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Exception while handling an update:", exc_info=context.error)
    if ADMIN_LOG_CHAT_ID:
        try:
            await context.bot.send_message(chat_id=int(ADMIN_LOG_CHAT_ID), text=f"Error: {context.error}")
        except Exception:
            pass

async def flood_guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    if not chat or not msg or not user:
        return

    # پیام‌های سرویس/ادمین‌ها را سخت نگیر
    from utils import is_admin
    if await is_admin(update, context):
        return

    tripped = flood.push(chat.id, user.id)
    if tripped:
        try:
            await mute_user(chat.id, user.id, context, FLOOD_MUTE_SEC)
            await msg.reply_text(f"به دلیل فلود، {FLOOD_MUTE_SEC} ثانیه میوت شدی.")
        except Exception:
            pass

def build_app() -> Application:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set in environment variables.")

    init_db()

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    app.add_error_handler(error_handler)

    # دستورات عمومی
    app.add_handler(CommandHandler("rules", cmd_rules))
    app.add_handler(CommandHandler("get", cmd_get))

    # دستورات ادمین
    app.add_handler(CommandHandler("panel", cmd_panel))
    app.add_handler(CommandHandler("setrules", cmd_setrules))
    app.add_handler(CommandHandler("note", cmd_note))
    app.add_handler(CommandHandler("delnote", cmd_delnote))
    app.add_handler(CommandHandler("warn", cmd_warn))
    app.add_handler(CommandHandler("warns", cmd_warns))
    app.add_handler(CommandHandler("resetwarns", cmd_resetwarns))
    app.add_handler(CommandHandler("welcome_on", welcome_on))
    app.add_handler(CommandHandler("welcome_off", welcome_off))
    app.add_handler(CommandHandler("links_on", links_on))
    app.add_handler(CommandHandler("links_off", links_off))
    app.add_handler(CommandHandler("verify_on", verify_on))
    app.add_handler(CommandHandler("verify_off", verify_off))

    # کال‌بک کپچا
    app.add_handler(CallbackQueryHandler(verify_callback, pattern=r"^verify:\d+$"))

    # خوش‌آمد و تایید ورود
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, on_new_members))

    # گارد فلود (خیلی سریع)
    app.add_handler(MessageHandler(filters.ALL & (~filters.StatusUpdate.ALL), flood_guard), group=0)

    # ضدلینک/ضدفوروارد
    app.add_handler(MessageHandler(filters.TEXT | filters.CaptionRegex(r".*"), anti_content), group=1)

    return app

def main() -> None:
    app = build_app()

    # برای سرعت: drop_pending_updates باعث می‌شود backlog نخورد
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
        close_loop=False,
    )

if __name__ == "__main__":
    main()
