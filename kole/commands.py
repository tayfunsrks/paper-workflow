# Property of Kor.PiracyTeam - GNU General Public License v2.0

import re
import time
from pyrogram.types import InlineKeyboardButton as ikb, InlineKeyboardMarkup as ikm
from utils import temp
from pyrogram.types.messages_and_media.message import Message
from pyrogram import Client, filters
from info import START_TXT
from helpers.settings import Settings
from database.users_chats_db import db
from helpers.wayback import saveWebPage

@Client.on_message(~filters.channel & filters.command(["start", "help", "h", "y", "yardım", "yardim", "stats"]))
async def start(client: Client, message: Message):
    if not message.from_user:
        return await message.delete(revoke=True)
    elif message.from_user.id in temp.BANNED_USERS:
        return await message.delete(revoke=True)
    myusername = (await client.get_me()).username
    reply_markup = ikm(
        [
            [
                ikb('➕ Gruba ekle', url=f'http://t.me/{myusername}?startgroup=true'),
                # ikb('🔍 Ara', switch_inline_query_current_chat='')
                ikb('🔮 İstatistikler', callback_data='stats')
            ],
            [
                ikb('😈 Hakkında', callback_data='about'),
                ikb('😊 Ayarlar', callback_data='settings#0')
            ]
        ]
    )
    username = (await client.get_me()).username
    await message.reply_text(START_TXT.format(
        message.from_user.mention if message.from_user else message.chat.title, username, "KorPiracy.Kitap"),
        reply_markup=reply_markup, disable_web_page_preview=True)

@Client.on_message(~filters.channel & filters.command("id"))
async def aydi(client: Client, message: Message):
    if not message.from_user:
        return await message.delete(revoke=True)
    elif message.from_user.id in temp.BANNED_USERS:
        return await message.delete(revoke=True)
    await message.reply_text(f"Buranın ID'si: `{message.chat.id}`", reply_markup=ikm(temp.kapat_btn))

@Client.on_message(filters.private & filters.command(["ayarlar", "settings"]))
async def settings_handler(client: Client, message: Message):
    if not message.from_user:
        return await message.delete(revoke=True)
    elif message.from_user.id in temp.BANNED_USERS:
        return await message.delete(revoke=True)
    await db.add_user(message.from_user.id, message.from_user.first_name)
    await Settings(message)
    await message.delete()

@Client.on_message(filters.private & filters.command("ping"))
async def ping(client: Client, message: Message):
    if not message.from_user:
        return await message.delete(revoke=True)
    elif message.from_user.id in temp.BANNED_USERS:
        return await message.delete(revoke=True)

    start_time = int(round(time.time() * 1000))
    reply = await message.reply_text("Ping", quote=True)
    end_time = int(round(time.time() * 1000))
    await reply.edit_text(f"Pong {end_time - start_time} ms", reply_markup=ikm(temp.kapat_btn))
    await message.delete()

@Client.on_message(filters.private & filters.command(["wayback", "wb"]))
async def wayback(client: Client, message: Message):
    if not message.from_user:
        return await message.delete(revoke=True)
    elif message.from_user.id in temp.BANNED_USERS:
        return await message.delete(revoke=True)
    try:
        link = None
        if message.reply_to_message:
            link = message.reply_to_message.text
        elif len(message.command) == 2:
            link = message.command[1]
        else:
            return await message.reply_text("Yanında linkisini verin efendi", quote=True, reply_markup=ikm(temp.kapat_btn))

        try:
            link = re.match("((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", link)[0]

        except TypeError:
            return await message.reply_text("Linkinis geçerli değil", quote=True, reply_markup=ikm(temp.kapat_btn))

        sent = await message.reply_text("Bi 20 saniye bekleyin efendimis", quote=True)
        if retLink := saveWebPage(link):
            await sent.edit_text(f'Yedekledim: {retLink}', reply_markup=ikm(temp.kapat_btn))

        else:
            return await sent.edit_text("Olmadı efendi smeagol üzüldü :(")
    except Exception as e:
        print(e)
    await message.delete()
