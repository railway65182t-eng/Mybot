from __future__ import annotations
from datetime import datetime, timedelta, timezone
from telegram import ChatPermissions, Update
from telegram.ext import ContextTypes
from db import add_warn, get_warns, reset_warns
from utils import is_admin

DEFAULT_PERMS = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_voice_notes=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
    can_manage_topics=False,
)

MUTED_PERMS = ChatPermissions(
    can_send_messages=False,
    can_send_audios=False,
    can_send_documents=False,
    can_send_photos=False,
    can_send_videos=False,
    can_send_video_notes=False,
    can_send_voice_notes=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
    can_invite_users=False,
    can_pin_messages=False,
    can_change_info=False,
    can_manage_topics=False,
)

async def mute_user(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE, seconds: int) -> None:
    until = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    await context.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, permissions=MUTED_PERMS, until_date=until)

async def unmute_user(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.restrict_chat_member(chat_id=chat_id, user_id=user_id, permissions=DEFAULT_PERMS)

async def ban_user(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)

async def kick_user(chat_id: int, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
    await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)

async def cmd_warn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user:
        return
    if not await is_admin(update, context):
        return
    msg = update.effective_message
    if not msg or not msg.reply_to_message or not msg.reply_to_message.from_user:
        await msg.reply_text("برای اخطار دادن باید روی پیام کاربر ریپلای کنید.")
        return
    target = msg.reply_to_message.from_user
    if await is_admin(update, context, target.id):
        await msg.reply_text("به ادمین اخطار نمی‌دهم.")
        return

    count = add_warn(update.effective_chat.id, target.id, 1)
    await msg.reply_text(f"اخطار ثبت شد. تعداد اخطارهای این کاربر: {count}")

    if count >= 3:
        await mute_user(update.effective_chat.id, target.id, context, 600)
        await msg.reply_text("به دلیل ۳ اخطار، کاربر ۱۰ دقیقه میوت شد.")

async def cmd_warns(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_message:
        return
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.from_user:
        target = msg.reply_to_message.from_user
        count = get_warns(update.effective_chat.id, target.id)
        await msg.reply_text(f"اخطارهای کاربر: {count}")
        return
    await msg.reply_text("برای دیدن اخطارها روی پیام کاربر ریپلای کنید.")

async def cmd_resetwarns(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user or not update.effective_message:
        return
    if not await is_admin(update, context):
        return
    msg = update.effective_message
    if not msg.reply_to_message or not msg.reply_to_message.from_user:
        await msg.reply_text("برای پاک کردن اخطارها روی پیام کاربر ریپلای کنید.")
        return
    target = msg.reply_to_message.from_user
    reset_warns(update.effective_chat.id, target.id)
    await msg.reply_text("اخطارهای کاربر پاک شد.")
