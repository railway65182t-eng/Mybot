from __future__ import annotations
import re
from telegram import ChatMemberAdministrator, ChatMemberOwner, Update
from telegram.ext import ContextTypes

URL_RE = re.compile(r"(https?://|t\.me/|www\.)", re.IGNORECASE)

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int | None = None) -> bool:
    chat = update.effective_chat
    if not chat:
        return False
    uid = user_id if user_id is not None else (update.effective_user.id if update.effective_user else None)
    if uid is None:
        return False
    member = await context.bot.get_chat_member(chat.id, uid)
    return isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))

def has_link(text: str | None) -> bool:
    if not text:
        return False
    return bool(URL_RE.search(text))

def fmt_name(update: Update) -> str:
    u = update.effective_user
    if not u:
        return "کاربر"
    name = (u.full_name or "").strip()
    return name if name else "کاربر"
