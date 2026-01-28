# Property of Kor.PiracyTeam - GNU General Public License v2.0

import asyncio
from pyrogram import Client, filters
from helpers.guncelTarih import guncelTarih
from info import AUTH_CHANNEL, BAN_QUITERS, LOG_CHANNEL, LOG_JOINERS, LOG_QUITERS, YOU_JOINED
from pyrogram.types import ChatMemberUpdated
from utils import temp
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import InlineKeyboardButton as ikb, InlineKeyboardMarkup as ikm

# Get logging configurations
from info import LOG

@Client.on_chat_member_updated(filters.chat(AUTH_CHANNEL))
async def join_quit(bot:Client, cmu: ChatMemberUpdated):
    if not cmu.old_chat_member and not cmu.new_chat_member: return
    if cmu.from_user.is_self or cmu.from_user.is_bot: return
    if cmu.new_chat_member and cmu.new_chat_member.status != ChatMemberStatus.MEMBER:
        return
    tip = '#YeniAyrılma' if cmu.old_chat_member else '#YeniKatılma'
    yeni = cmu.old_chat_member.user if cmu.old_chat_member else cmu.new_chat_member.user
    infostr = f"#{temp.MY_USERNAME}" \
            f"\n{tip}" + \
            f"\n\nAd: `{yeni.first_name}`" + \
            f"\nSoyad: `{yeni.last_name}`" + \
            f"\nKullanıcı Adı: @{yeni.username}" + \
            f"\nID: `{yeni.id}`" + \
            f"\nEtiket: {yeni.mention}" + \
            f"\nDC: `{yeni.dc_id}`" + \
            f"\nDil: `{yeni.language_code}`" + \
            f"\nLink: tg://user?id={str(yeni.id)}" + \
            f"\nTarih: {guncelTarih()}"
    buttons = []
    if tip == '#YeniKatılma':
        if temp.join_chnl_msg:
            try: await temp.join_chnl_msg.delete()
            except Exception: pass
        if YOU_JOINED:
            try: await bot.send_message(yeni.id, "Kanala katıldın. Şimdi beni kullanabilirsin.")
            except Exception: pass
        buttons.append(ikb('🔥 Yasakla', callback_data=f'ban#{yeni.id}'))
    else:
        if cmu.old_chat_member.status == ChatMemberStatus.BANNED: return # banlıysa elleme
        if BAN_QUITERS:
            try:
                ban = bool(await bot.ban_chat_member(AUTH_CHANNEL, yeni.id))
            except Exception as e:
                LOG.exception(e)
                ban = False
            if ban:
                buttons.append(ikb('🍀 Yasağı Kaldır', callback_data=f'unban#{yeni.id}'))
            else:
                buttons.append(ikb('🔥 Yasakla', callback_data=f'ban#{yeni.id}'))
            infostr += f"\nAyrılma Yasağı: {'Başarılı ✅' if ban else 'Başarısız ❌'}"
        else:
            buttons.append(ikb('🔥 Yasakla', callback_data=f'ban#{yeni.id}'))
    buttons.append(ikb('❌ Kapat', callback_data='kapat'))
    if LOG_JOINERS and tip == '#YeniKatılma':
        LOG.info(f'{tip} Kullanıcı: {yeni.first_name} ({yeni.id})')
    if LOG_QUITERS and tip == '#YeniAyrılma':
        LOG.info(f'{tip} Kullanıcı: {yeni.first_name} ({yeni.id})')
    try: await bot.send_message(LOG_CHANNEL, infostr, reply_markup=ikm([buttons]))
    except Exception as e:
        LOG.info(e)
        LOG.info(infostr)
