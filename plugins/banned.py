# Property of Kor.PiracyTeam - GNU General Public License v2.0

import contextlib
from pyrogram import Client, filters
from utils import temp
from pyrogram.types import Message
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import SUPPORT_CHAT, YOU_BANNED_MSG

# Get logging configurations
from info import LOG

async def banned_users(_, client, message: Message):
    return (message.from_user is not None or not message.sender_chat
           ) and message.from_user.id in temp.BANNED_USERS

banned_user = filters.create(banned_users)

async def disabled_chat(_, client, message: Message):
    return message.chat.id in temp.BANNED_CHATS

disabled_group = filters.create(disabled_chat)

@Client.on_message(filters.private & banned_user & filters.incoming)
async def ban_reply(bot, message):
    if not YOU_BANNED_MSG: return
    ban = await db.get_ban_status(message.from_user.id)
    await message.reply_text(f'Banlanmışsın.\nSebep: {ban["ban_reason"]}')

@Client.on_message(filters.group & disabled_group & filters.incoming)
async def grp_bd(bot: Client, message: Message):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Destek', url=f'https://t.me/{SUPPORT_CHAT}')]]) if SUPPORT_CHAT else None
    vazha = await db.get_chat(message.chat.id)
    k = await message.reply_text(text=f"Bu sohbeti sahibim yasaklamış. Elveda.\nSebep: <code>{vazha['reason']}</code>.", reply_markup=reply_markup)
    with contextlib.suppress(Exception): await k.pin()
    await bot.leave_chat(message.chat.id)
