# Property of Kor.PiracyTeam - GNU General Public License v2.0

from urllib.parse import quote
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import CallbackQuery
from database.ia_filterdb import get_search_results
from helpers.temizleyici import sonsuz_sil
from utils import is_logged_in, is_subscribed, get_size, temp
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CAPTION_SPLITTER, \
    CUSTOM_CAPTION, DISABLE_INLINE, JOIN_CHANNEL_WARNING, SEND_WITH_BUTTONS, SHARE_BUTTON_TEXT
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument
from database.users_chats_db import db

# Get logging configurations
from info import LOG

cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME

def get_reply_markup(query):
    if not SEND_WITH_BUTTONS:
        return None
    url = f't.me/share/url?url={quote(SHARE_BUTTON_TEXT.format(username=temp.MY_USERNAME))}'
    buttons = [[
        InlineKeyboardButton('Tekrar Ara', switch_inline_query_current_chat=query),
        InlineKeyboardButton('Botu Paylaş', url=url)
        ]]
    return InlineKeyboardMarkup(buttons)

@Client.on_inline_query(filters.user(AUTH_USERS) if AUTH_USERS else None)
async def answer(bot:Client, query:CallbackQuery):
    if DISABLE_INLINE:
        await query.answer([])
        return LOG.info('inline kapalı.')
    # kanala katıldı mı?
    elif query.from_user.id in temp.BANNED_USERS:
        return await query.answer([])
    elif not await is_subscribed(bot, query):
        if JOIN_CHANNEL_WARNING:
            return await query.answer(results=[],
                           cache_time=0,
                           switch_pm_text='Botu kullanmak için kanalıma abone olmalısın.',
                           switch_pm_parameter="subscribe")
        return await query.answer([])
    elif not await is_logged_in(query):
        await query.answer([])
        return LOG.error(f"Giriş yapmamış kullanıcı inline denemeye çalıştı: {query.from_user.id}")
        
    results = []
    if '|' in query.query:
        text, file_type = query.query.split('|', maxsplit=1)
        text = text.strip()
        file_type = file_type.strip().lower()
    else:
        text = query.query.strip()
        file_type = None

    offset = int(query.offset or 0)
    reply_markup = get_reply_markup(query=text)
    ubc = await db.get_button_count(query.from_user.id)
    files, next_offset, total = await get_search_results(text,
                                                         file_type=file_type,
                                                         max_results=ubc,
                                                         offset=offset)
    for file in files:
        f_caption = file.caption
        f_caption += '' if (CUSTOM_CAPTION is None) or (len(f_caption) > 1024) else f'\n{CUSTOM_CAPTION}'
        altmetin = f'Boyut: {get_size(file.file_size)}, Tip: {file.file_type}'
        inlinecaption = sonsuz_sil(file.caption, '\n', ' ')
        altmetin += f'{CAPTION_SPLITTER}{inlinecaption}'

        results.append(
            InlineQueryResultCachedDocument(
                title=file.file_name,
                document_file_id=file.file_id,
                caption=f_caption,
                description=altmetin,
                reply_markup=reply_markup))

    if results:
        switch_pm_text = f"{emoji.FILE_FOLDER} {total} Sonuç Buldum"
        if text:
            switch_pm_text += f": {text}"
        try:
            await query.answer(results=results,
                               is_personal=True,
                               cache_time=cache_time,
                               switch_pm_text=switch_pm_text,
                               switch_pm_parameter="start",
                               next_offset=str(next_offset))
        except QueryIdInvalid:
            pass
        except Exception as e:
            LOG.exception(str(e))
            await query.answer(results=[], is_personal=True,
                               cache_time=cache_time,
                               switch_pm_text=str(e)[:63],
                               switch_pm_parameter="error")
    else:
        switch_pm_text = f'{emoji.CROSS_MARK} Sonuç yok'
        if text:
            switch_pm_text += f': "{text}"'

        await query.answer(results=[],
                           is_personal=True,
                           cache_time=cache_time,
                           switch_pm_text=switch_pm_text,
                           switch_pm_parameter="okay")
