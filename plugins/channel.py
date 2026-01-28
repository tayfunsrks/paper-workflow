# Property of Kor.PiracyTeam - GNU General Public License v2.0

from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from helpers.yardimMesajlari import yardimMesaji
from info import AUTH_CHANNEL, CHANNELS, DISABLE_FILE_SAVE
from pyrogram.types import Message
from database.ia_filterdb import save_file

# Get logging configurations
from info import LOG
from utils import is_subscribed, temp

async def saveFile(message, forcereplace=False):
    """Media Handler"""
    if DISABLE_FILE_SAVE: return
    for file_type in (MessageMediaType.DOCUMENT, MessageMediaType.VIDEO, MessageMediaType.AUDIO):
        media = getattr(message, file_type.value, None)
        if media is not None: break
    else: return

    media.file_type = file_type.value
    media.caption = message.caption
    await save_file(media, forcereplace)

media_filter = filters.chat(CHANNELS) & (filters.document | filters.video | filters.audio)

@Client.on_message(media_filter)
async def channel_handler_newmessage(client, message:Message):
    await saveFile(message, False)

@Client.on_edited_message(media_filter)
async def channel_handler_editedmessage(client, message:Message):
    """force update if edited from channel"""
    await saveFile(message, True)

@Client.on_message(filters.document & filters.private)
async def inline_help_msg(client, message:Message):
    """help messages for inline"""
    if message.from_user.id in temp.BANNED_USERS: return
    if not await is_subscribed(client, message): return
    await yardimMesaji(message.document.file_name, message)
