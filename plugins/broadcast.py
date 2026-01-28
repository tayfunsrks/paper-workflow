# Property of Kor.PiracyTeam - GNU General Public License v2.0

from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid, UserNotParticipant
from pyrogram.enums import ChatMemberStatus
from info import ADMINS, AUTH_CHANNEL, BROADCAST_AS_COPY
import asyncio
from utils import temp

# Get logging configurations
from info import LOG

async def broadcast_messages(bot:Client, user_id, message:Message):
    if AUTH_CHANNEL:
        try:
            user = await bot.get_chat_member(AUTH_CHANNEL, user_id)
        except UserNotParticipant:
            await db.delete_user(int(user_id))
            LOG.info(f"{user_id} - Kanalda olmadığı için veritabanından kaldırıldı.")
            return False, "Banned"
        except Exception as e:
            LOG.exception(e)
        else:
            if user.status == ChatMemberStatus.BANNED:
                await db.delete_user(int(user_id))
                LOG.info(f"{user_id} - Kanaldan engellendiği için veritabanından kaldırıldı.")
                return False, "Banned"
    # db banlıysa
    if user_id in temp.BANNED_USERS:
        await db.delete_user(int(user_id))
        LOG.info(f"{user_id} - VTda engellendiği için veritabanından kaldırıldı.")
        return False, "Banned"
    try:
        if BROADCAST_AS_COPY:
            await message.copy(chat_id=user_id, protect_content=True, disable_notification=True)
        else:
            await message.forward(chat_id=user_id, disable_notification=True)
        return True, "Succes"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await broadcast_messages(bot, user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        LOG.info(f"{user_id} - Hesap silindiği için veritabanından kaldırıldı.")
        return False, "Deleted"
    except UserIsBlocked:
        LOG.info(f"{user_id} - Botu engelledi.")
        await db.delete_user(int(user_id))
        LOG.info(f"{user_id} - Botu engellediği için veritabanından kaldırıldı.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        LOG.info(f"{user_id} - Kimliği geçersiz olduğu için veritabanından kaldırıldı.")
        return False, "Error"
    except Exception as e:
        return False, "Error"

@Client.on_message(filters.command(['yay', 'broadcast']) & filters.user(ADMINS))
async def broadcast_handler(bot, message):
    if not message.reply_to_message:
        return await message.reply('yayınlamak istediğin mesajı bu komutla yanıtla.')
    message = message.reply_to_message
    await message.reply(
        text='__Bunu yayınlamak istediğinden emin misin kıymetlim?__',
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text='Evet (Herkese)', callback_data='bdcast#all')],
                [InlineKeyboardButton(text='Evet (Üyelere)', callback_data='bdcast#vip')],
                [InlineKeyboardButton(text='Hayır', callback_data='kapat')]
            ]
        )
    )

@Client.on_callback_query(filters.user(ADMINS) &filters.regex(r'^bdcast+.*$'))
async def broadcast_confrm(bot:Client, query):
    bcst_tipi = query.data.split("#")[1]
    message = query.message
    b_msg = message.reply_to_message
    if not b_msg:
        await query.answer(
            text='Mesaj bulunamadı.',
            show_alert=True
        )
        return await message.delete()
    await message.edit(text='Mesajı yayınlıyorum.', reply_markup=None)

    tosend = f"#{temp.MY_USERNAME}\n#YeniYayın"

    start_time = time.time()
    if bcst_tipi == 'vip':
        users = await db.get_all_notif_user()
        total_users = await db.total_notif_users_count()
        tosend += "\n#ÜyelereYayın\n\n"
    elif bcst_tipi == 'all':
        users = await db.get_all_users()
        total_users = await db.total_users_count()
        tosend += "\n#HerkeseYayın\n\n"
    else: return LOG.error('error #416')
    done = blocked = deleted = failed = success = banned = 0
    async for user in users:
        pti, sh = await broadcast_messages(bot, int(user['id']), b_msg)
        if pti:
            success += 1
        elif not pti:
            if sh == "Blocked":
                blocked += 1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
            elif sh == "Banned":
                banned += 1
        done += 1
        await asyncio.sleep(1)
        if not done % 20:
            await message.edit(tosend + 
                f"Yayın devam ediyor:\n\n"
                f"Toplam Kullanıcılar: {total_users}\n"
                f"Tamamlanan: {done} / {total_users}\n"
                f"Başarılı: {success}\n"
                f"Botu Engelleyen: {blocked}\n"
                f"Engelli: {banned}\n"
                f"Silinen: {deleted}")
    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
    await message.edit(tosend + 
        f"Yayın {time_taken} saniyede tamamlandı.\n\n"
        f"Toplam Kullanıcı: {total_users}\n"
        f"Tamamlanan: {done} / {total_users}\n"
        f"Başarılı: {success}\n"
        f"Botu Engelleyen: {blocked}\n"
        f"Engelli: {banned}\n"
        f"Silinen: {deleted}")
