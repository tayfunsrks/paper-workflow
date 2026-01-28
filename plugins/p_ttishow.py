# Property of Kor.PiracyTeam - GNU General Public License v2.0

import os
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from helpers.guncelTarih import guncelTarih
from info import ADMINS, AUTH_CHANNEL, SUPPORT_CHAT, THUMB_FILE
from database.users_chats_db import db
from utils import temp
from pyrogram.types import InlineKeyboardButton as ikb, InlineKeyboardMarkup as ikm, Message
# Get logging configurations
from info import LOG

# https://t.me/GetTGLink/4179
@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot:Client, message:Message):
    if len(message.command) == 1:
        return await message.reply_text('Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except Exception:
        chat = chat
    try:
        reply_markup = ikm([[ikb('Destek', url=f'https://t.me/{SUPPORT_CHAT}')]]) if SUPPORT_CHAT else None
        await bot.send_message(
            chat_id=chat,
            text='Bu sohbeti sahibim yasaklamış. Elveda.',
            reply_markup=reply_markup,
        )
        await bot.leave_chat(chat)
    except Exception as e:
        await message.reply_text(f'Error - {e}')

@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot: Client, message: Message):
    if len(message.command) == 1:
        return await message.reply_text('Yanında idsini de verinis kıymetli böyle nerden bilelim?')

    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "Sebepsiz"
    try:
        chat_ = int(chat)
    except Exception:
        return await message.reply_text('Geçerli bi sohbet idsi ver kıymetli')
    cha_t = await db.get_chat(chat_)
    if not cha_t:
        return await message.reply_text("Sohbet veritabanında yok kıymetli?")
    if cha_t['is_disabled']:
        return await message.reply_text(f"Zaten devredışı kıymetli?\Sebep: <code>{cha_t['reason']}</code>")

    await db.disable_chat(chat_, reason)
    temp.BANNED_CHATS.append(chat_)
    await message.reply_text('Devredışı bıraktık bunu kıymetli')
    try:
        reply_markup = ikm([[ikb('Destek', url=f'https://t.me/{SUPPORT_CHAT}')]]) if SUPPORT_CHAT else None

        await bot.send_message(chat_id=chat_, text=f'Bu sohbeti sahibim yasaklamış. Elveda.\nSebep: <code>{reason}</code>', reply_markup=reply_markup)

        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply_text(f"Error - {e}")

@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message:Message):
    if len(message.command) == 1:
        return await message.reply_text('Yanında idsini de verinis kıymetli böyle nerden bilelim?')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except Exception:
        return await message.reply_text('Geçerli bi sohbet idsi ver kıymetli')
    sts = await db.get_chat(chat)
    if not sts:
        return await message.reply_text("Sohbet veritabanında yok kıymetli?")
    if not sts.get('is_disabled'):
        return await message.reply_text('Zaten devredışı değil ki?')
    await db.re_enable_chat(chat_)
    temp.BANNED_CHATS.remove(chat_)
    await message.reply_text("Yeniden aktif ettik efendimiss")

# a function for trespassing into others groups, Inspired by a Vazha
# Not to be used , But Just to showcase his vazhatharam.
@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot: Client, message: Message):
    if len(message.command) == 1:
        return await message.reply_text('Yanında idsini de verinis kıymetli böyle nerden bilelim?')

    chat = message.command[1]
    try:
        chat = int(chat)
    except Exception:
        return await message.reply_text('Geçerli bi sohbet idsi ver kıymetli')
    try:
        gruplink = await bot.create_chat_invite_link(chat)
    except Exception:
        gruplink = None
    try:
        silebilir = (await bot.get_chat_member(chat, temp.MY_ID)).privileges.can_delete_messages

    except Exception:
        silebilir = False
    if gruplink:
        tosend = f"#{temp.MY_USERNAME}\n#YeniLink\n\nLink: {gruplink.invite_link}\nTarih: {gruplink.date}\nSilebilir: {silebilir}"

        await message.reply_text(tosend, quote=True)

@Client.on_message(filters.command('izinler') & filters.user(ADMINS))
async def get_privileges(bot: Client, message: Message):
    if len(message.command) == 1:
        return await message.reply_text('Yanında idsini de verinis kıymetli böyle nerden bilelim?')

    chat = message.command[1]
    try:
        chat = int(chat)
    except Exception:
        return await message.reply_text('Geçerli bi sohbet idsi ver kıymetli')
    try:
        silebilir = (await bot.get_chat_member(chat, temp.MY_ID)).privileges
    except Exception:
        silebilir = False
    try:
        cet = await bot.get_chat(chat)
    except Exception:
        cet = ''
    if silebilir:
        tosend = f"#{temp.MY_USERNAME}\n#YeniIzinListesi\n\nİzinlerim:\n\n{silebilir}\n\nÇet:\n\n{cet}"

        await message.reply_text(tosend, quote=True)

@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot:Client, message:Message):
    # https://t.me/GetTGLink/4185
    if len(message.command) == 1:
        return await message.reply_text('id ya da kullanıcı adı ver pis hobbit')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "Sebepsiz"
    try:
        chat = int(chat)
    except Exception:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply_text("Geçersiz kullanıcı. Daha önce göslerimisle gördük m?")
    except IndexError:
        return await message.reply_text("Bu bir kanal idsine benziyor daha çok.")
    except Exception as e:
        return await message.reply_text(f'Hata:\n\n{e}')
    else:
        try: await bot.ban_chat_member(AUTH_CHANNEL, k.id)
        except Exception: pass
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply_text(f"{k.mention} ({k.id}) zaten engelli.\nNeden: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply_text(f"{k.mention} ({k.id}) engellendi.")

@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot:Client, message:Message):
    if len(message.command) == 1:
        return await message.reply_text('id ya da kullanıcı adı ver pis hobbit')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "Sebepsiz"
    try:
        chat = int(chat)
    except Exception:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply_text("Geçersiz kullanıcı. Daha önce göslerimisle gördük m?")
    except IndexError:
        return await message.reply_text("Bu bir kanal idsine benziyor daha çok.")
    except Exception as e:
        return await message.reply_text(f'Hata:\n\n{e}')
    else:
        try: await bot.unban_chat_member(AUTH_CHANNEL, k.id)
        except Exception: pass
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply_text(f"{k.mention} ({k.id}) engellenmemiş.")
        await db.remove_ban(k.id)
        try: temp.BANNED_USERS.remove(k.id)
        except ValueError: pass
        await message.reply_text(
            f"{k.mention} ({k.id}) banı kaldırıldı.\nEngelleme sebebi şuydu: {reason}"
        )

@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message:Message):
    # https://t.me/GetTGLink/4184
    raju = await message.reply_text('Kullanıcı listesini getiriyoruss')
    users = await db.get_all_users()
    out = "Veritabanındaki kullanıcısılarımıss:\n\n"
    say = 0
    async for user in users:
        say = say + 1
        out += f"{say}: <a href=tg://user?id={user['id']}>{user['name']}</a> (<code>{user['id']}</code>)"
        if user['ban_status']['is_banned']:
            out += ' (Yasaklı)'
        out += '\n'
    out += '\n' + guncelTarih()
    try:
        await raju.edit_text(out,
                reply_markup=ikm(temp.kapat_btn))
    except MessageTooLong:
        dosyaadi = f'{temp.MY_USERNAME} kullanıcılar.txt'
        with open(dosyaadi, 'w+') as outfile:
            outfile.write(out)
        await message.reply_document(dosyaadi,
            caption=dosyaadi, thumb=THUMB_FILE,
            reply_markup=ikm(temp.kapat_btn)
        )
        try: os.remove(dosyaadi)
        except Exception: pass
    await message.delete()

@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message:Message):
    raju = await message.reply_text('Sohbet listesini getiriyoruss')
    chats = await db.get_all_chats()
    out = "Veritabanındaki sohbetlerimiss:\n\n"
    say = 0
    async for chat in chats:
        say = say + 1
        out += f"{say}: {chat['title']} (`{chat['id']}`)"
        if chat['chat_status']['is_disabled']:
            out += ' (Yasaklı)'
        out += '\n'
    out += '\n' + guncelTarih()
    try:
        await raju.edit_text(out,
                reply_markup=ikm(temp.kapat_btn))
    except MessageTooLong:
        dosyaadi = f'{temp.MY_USERNAME} sohbetler.txt'
        with open(dosyaadi, 'w+') as outfile:
            outfile.write(out)
        await message.reply_document(dosyaadi,
            caption=dosyaadi, thumb=THUMB_FILE,
            reply_markup=ikm(temp.kapat_btn)
        )
        try: os.remove(dosyaadi)
        except Exception: pass
    await message.delete()
