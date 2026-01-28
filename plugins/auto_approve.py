# Property of Kor.PiracyTeam - GNU General Public License v2.0

import asyncio
from pyrogram import Client, filters
from pyrogram.types import ChatJoinRequest
from pyrogram.errors import UserIsBlocked, UserAlreadyParticipant
from info import AUTH_CHANNEL, AUTO_APPROVE
from pyrogram.errors import FloodWait

# Get logging configurations
from info import LOG

@Client.on_chat_join_request(filters.chat(AUTH_CHANNEL))
async def auto_approve(c: Client, m: ChatJoinRequest):
    if not AUTO_APPROVE: return
    if not m.from_user: return
    try:
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)
    except (UserAlreadyParticipant, UserIsBlocked):
        pass
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await c.approve_chat_join_request(m.chat.id, m.from_user.id)
