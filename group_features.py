from __future__ import annotations
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from db import get_settings, set_note, get_note, del_note
from utils import fmt_name, has_link, is_admin
from config import VERIFY_TIMEOUT_SEC

VERIFY_KEY = "verify_pending"  # context.chat_data key

async def on_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    msg = update.effective_message
    if not chat or not msg or not msg.new_chat_members:
        return

    s = get_settings(chat.id)

    for u in msg.new_chat_members:
        if u.is_bot:
            continue

        if s["welcome_enabled"]:
            text = s["welcome_text"].replace("{name}", u.full_name)
            await msg.reply_text(text)

        if s["join_verify"]:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("من انسان هستم ✅", callback_data=f"verify:{u.id}")]])
            note = await msg.reply_text("برای فعال شدن در گروه، روی دکمه تأیید بزن.", reply_markup=kb)

            pending = context.chat_data.get(VERIFY_KEY, {})
            pending[str(u.id)] = {"message_id": note.message_id}
            context.chat_data[VERIFY_KEY] = pending

            await context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=u.id,
                permissions=None,  # None یعنی کامل بسته (PTB خودش مدیریت می‌کند)
            )

            context.job_queue.run_once(
                verify_timeout_job,
                when=VERIFY_TIMEOUT_SEC,
                data={"chat_id": chat.id, "user_id": u.id},
                name=f"verify_timeout:{chat.id}:{u.id}",
            )

async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not update.effective_chat:
        return
    await query.answer()

    data = query.data or ""
    if not data.startswith("verify:"):
        return
    uid = int(data.split(":", 1)[1])
    clicker = update.effective_user.id if update.effective_user else None
    if clicker != uid and not await is_admin(update, context):
        await query.answer("این دکمه برای خودِ همان کاربر است.", show_alert=True)
        return

    from moderation import unmute_user  # reuse default perms
    await unmute_user(update.effective_chat.id, uid, context)

    pending = context.chat_data.get(VERIFY_KEY, {})
    pending.pop(str(uid), None)
    context.chat_data[VERIFY_KEY] = pending

    await query.edit_message_text("تأیید شد ✅ خوش آمدی!")

async def verify_timeout_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.job.data if context.job else {}
    chat_id = data.get("chat_id")
    user_id = data.get("user_id")
    if not chat_id or not user_id:
        return

    pending = context.chat_data.get(VERIFY_KEY, {})
    if str(user_id) not in pending:
        return

    try:
        await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
        await context.bot.unban_chat_member(chat_id=chat_id, user_id=user_id)
    except Exception:
        pass

    pending.pop(str(user_id), None)
    context.chat_data[VERIFY_KEY] = pending

async def anti_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    msg = update.effective_message
    if not chat or not msg or not msg.from_user:
        return
    if await is_admin(update, context):
        return

    s = get_settings(chat.id)

    if s["links_blocked"]:
        text = msg.text or msg.caption
        if has_link(text):
            try:
                await msg.delete()
            except Exception:
                pass
            await msg.reply_text("ارسال لینک در این گروه مجاز نیست.")
            return

    if msg.forward_from_chat and msg.forward_from_chat.type == "channel":
        if s.get("join_verify", True):  # همان سوییچ کلی برای سخت‌گیری
            try:
                await msg.delete()
            except Exception:
                pass
            await msg.reply_text("فوروارد از کانال مجاز نیست.")
            return

async def cmd_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    msg = update.effective_message
    if not chat or not msg:
        return
    s = get_settings(chat.id)
    await msg.reply_text(s["rules_text"])

async def cmd_setrules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_message:
        return
    if not await is_admin(update, context):
        return
    text = " ".join(context.args) if context.args else ""
    if not text:
        await update.effective_message.reply_text("متن قوانین را بعد از دستور بنویس.")
        return
    from db import set_setting
    set_setting(update.effective_chat.id, "rules_text", text)
    await update.effective_message.reply_text("قوانین ذخیره شد.")

async def cmd_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    msg = update.effective_message
    if not chat or not msg:
        return
    if not context.args:
        await msg.reply_text("مثال: /note key متن نوت")
        return
    key = context.args[0].lower()
    value = " ".join(context.args[1:]).strip()
    if not value:
        await msg.reply_text("متن نوت را هم بنویس.")
        return
    if not await is_admin(update, context):
        return
    set_note(chat.id, key, value)
    await msg.reply_text("نوت ذخیره شد.")

async def cmd_get(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    msg = update.effective_message
    if not chat or not msg:
        return
    if not context.args:
        await msg.reply_text("مثال: /get key")
        return
    key = context.args[0].lower()
    v = get_note(chat.id, key)
    await msg.reply_text(v if v else "چیزی پیدا نشد.")

async def cmd_delnote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    msg = update.effective_message
    if not chat or not msg:
        return
    if not await is_admin(update, context):
        return
    if not context.args:
        await msg.reply_text("مثال: /delnote key")
        return
    key = context.args[0].lower()
    del_note(chat.id, key)
    await msg.reply_text("نوت حذف شد.")
