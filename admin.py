from __future__ import annotations
from telegram import Update
from telegram.ext import ContextTypes
from db import get_settings, set_setting
from utils import is_admin

async def cmd_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_message:
        return
    if not await is_admin(update, context):
        return
    s = get_settings(update.effective_chat.id)
    txt = (
        "پنل مدیریت ⚙️\n"
        f"welcome: {'ON' if s['welcome_enabled'] else 'OFF'}\n"
        f"links: {'BLOCK' if s['links_blocked'] else 'FREE'}\n"
        f"verify: {'ON' if s['join_verify'] else 'OFF'}\n"
        "\n"
        "دستورات:\n"
        "/welcome_on\n"
        "/welcome_off\n"
        "/links_on\n"
        "/links_off\n"
        "/verify_on\n"
        "/verify_off\n"
    )
    await update.effective_message.reply_text(txt)

async def _toggle(update: Update, context: ContextTypes.DEFAULT_TYPE, field: str, value: int) -> None:
    if not update.effective_chat or not update.effective_message:
        return
    if not await is_admin(update, context):
        return
    set_setting(update.effective_chat.id, field, value)
    await update.effective_message.reply_text("انجام شد ✅")

async def welcome_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _toggle(update, context, "welcome_enabled", 1)

async def welcome_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _toggle(update, context, "welcome_enabled", 0)

async def links_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _toggle(update, context, "links_blocked", 1)

async def links_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _toggle(update, context, "links_blocked", 0)

async def verify_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _toggle(update, context, "join_verify", 1)

async def verify_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _toggle(update, context, "join_verify", 0)
