# Property of Kor.PiracyTeam - GNU General Public License v2.0

import asyncio
from pyrogram import Client, filters
from info import CLEAN_WELCOME, NO_SERVICE
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from helpers.guncelTarih import guncelTarih
from info import ADMINS, GEN_CHAT_LINK_DELAY, LOG_CHANNEL, SUPPORT_CHAT, \
    WELCOME_NEW_GROUP_MEMBERS, WELCOME_SELF_JOINED, WELCOME_TEXT
from database.users_chats_db import db
from utils import temp

@Client.on_message(filters.group & filters.service & filters.new_chat_members)
async def welcome(bot:Client, message:Message):
    # servisleri sil
    if NO_SERVICE and message.service:
        try: await message.delete()
        except Exception: pass
    # yeni üyelere hoş geldin
    if not message.new_chat_members: return
    yeni = message.from_user
    mensin = yeni.mention if yeni else "Anonim"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Destek', url=f'https://t.me/{SUPPORT_CHAT}')]]) if SUPPORT_CHAT else None

    # gelen sahipse
    if yeni.id in ADMINS: return
    # gelen normal üyeyse
    elif (int(temp.MY_ID) != yeni.id):
        if not WELCOME_NEW_GROUP_MEMBERS: return
        temp.last_welcome = await bot.send_message(
            chat_id=message.chat.id,
            text = WELCOME_TEXT.format(mensin),
            disable_web_page_preview=True
        )
        if not CLEAN_WELCOME: return
        try: await temp.last_welcome.delete()
        except Exception: pass
    # botu biri eklediyse
    else:
        # çet banlıysa
        if message.chat.id in temp.BANNED_CHATS:
            k = await bot.send_message(
                chat_id=message.chat.id,
                text='Bu sohbeti sahibim yasaklamış. Elveda.',
                reply_markup=reply_markup
            )
            try: await k.pin()
            except Exception: pass
            return await bot.leave_chat(message.chat.id)
        # hoş geldim de
        if WELCOME_SELF_JOINED:
            await bot.send_message(
                chat_id=message.chat.id,
                text='Bu gruba beni eklediğin için teşekkürler. kullanım için /start yazabilirsin.',
                reply_markup=reply_markup)
        # dbde çet kayıtlı değil
        if not await db.get_chat(message.chat.id):
            total = await bot.get_chat_members_count(message.chat.id)
            tosend = f"#{temp.MY_USERNAME}" \
                "\n#YeniGrup" \
                f"\n\nAd: `{message.chat.title}`" \
                f"\nKullanıcı Adı: @{yeni.username}" \
                f"\nID: `{yeni.id}`" \
                f"\nÜye: `{total}`" \
                f"\nEkleyen: {mensin} (`{yeni.id}`)" \
                f"\nDC: `{yeni.dc_id}`" \
                f"\nTarih: `{guncelTarih()}`"
            grubaeklendi = await bot.send_message(LOG_CHANNEL, tosend)
            await db.add_chat(message.chat.id, message.chat.title)

            # grup linki oluştur
            await asyncio.sleep(GEN_CHAT_LINK_DELAY*60)
            try: gruplink = await bot.create_chat_invite_link(yeni.id)
            except Exception: gruplink = None
            try: silebilir = (await bot.get_chat_member(yeni.id,temp.MY_ID)).privileges.can_delete_messages
            except Exception: silebilir = False
            await asyncio.sleep(1)
            if gruplink:
                tosend = f"#{temp.MY_USERNAME}" \
                "\n#YeniLink" \
                f"\n\nLink: {gruplink.invite_link}" \
                f"\nTarih: {gruplink.date}" \
                f"\nSilebilir: {str(silebilir)}"
                await grubaeklendi.reply_text(tosend, quote=True)
