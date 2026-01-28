# Property of Kor.PiracyTeam - GNU General Public License v2.0

import asyncio
import math
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import \
    ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from pyrogram.errors.exceptions.not_acceptable_406 import ChannelPrivate
from pyrogram.enums import MessageMediaType, ChatType
from helpers.guncelTarih import guncelTarih
from info import ADMINS, FINISHED_PROGRESS_STR, LOG_CHANNEL, PROGRESSBAR_LENGTH, UN_FINISHED_PROGRESS_STR

from info import botStartTime
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup as ikm, InlineKeyboardButton as ikb, CallbackQuery, Message
from pyrogram.errors import FloodWait
from utils import temp
from psutil import boot_time
import re, time
from plugins.pm_filter import ReadableTime

# Get logging configurations
from info import LOG

lock = asyncio.Lock()
tg_link_regex = "(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$"

def get_progressbar(current=0, total=0):
    if current == 0 or total == 0:
        return "[{0}]".format(FINISHED_PROGRESS_STR * PROGRESSBAR_LENGTH)
    try:
        return "[{0}{1}]".format(
        ''.join([FINISHED_PROGRESS_STR for _ in range(math.floor(current * 100 / total / (100/PROGRESSBAR_LENGTH)))]),
        ''.join([UN_FINISHED_PROGRESS_STR for _ in range(PROGRESSBAR_LENGTH - math.floor(current * 100 / total / (100/PROGRESSBAR_LENGTH)))])
        )
    except Exception as e:
        LOG.exception(e)
        return "[{0}]".format(FINISHED_PROGRESS_STR * PROGRESSBAR_LENGTH)

@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot:Client, query:CallbackQuery):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    _, raju, chat, lst_msg_id, from_user, fastordb = query.data.split("#")
    if raju == 'reject':
        await query.message.delete()
        if int(from_user) in ADMINS: return
        return await bot.send_message(int(from_user),
                               f'{chat} için indexlemeniz reddedildi.',
                               reply_to_message_id=int(lst_msg_id))
    if lock.locked():
        return await query.answer('Şu anda bir indexleme yapılıyor. O bitmeli.', show_alert=True)
    msg = query.message

    await query.answer('İşleniyor...', show_alert=False)
    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               f'{chat} için indexlemeniz kabul edildi.',
                               reply_to_message_id=int(lst_msg_id))
    await msg.edit("Sıkı tutunun efendimiss",
        reply_markup=ikm(
            [[ikb('❌ İptal', callback_data='index_cancel')]]
        )
    )
    try: chat = int(chat)
    except Exception: chat = chat
    await index_files_to_db(int(lst_msg_id), chat, msg, bot, fastordb == "dbindex")

@Client.on_message((filters.forwarded | ((filters.regex(tg_link_regex)) & filters.text)) & filters.private & filters.incoming)
async def send_for_index(bot:Client, message:Message):
    if message.text:
        regex = re.compile(tg_link_regex)
        match = regex.match(message.text)
        if not match:
            return await message.reply_text(
                'Ya son dosyanı gönder ya da son dosya linkini.' \
                '\nÖrnek: `https://t.me/c/648945648/616`' \
                '\nOlmadı yani bekleme burada boşuna.'
            )
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int(("-100" + chat_id))
    elif message.forward_from_chat.type in [ChatType.CHANNEL, ChatType.GROUP, ChatType.SUPERGROUP]:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return
    # indexleme butonları
    butonlar = [
        [
            ikb('Kabul (VT)', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}#dbindex')
        ],
        [
            ikb('Kabul (Hızlı)', callback_data=f'index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}#fastindex')
        ],
        [
            ikb('Reddet', callback_data=f'index#reject#{chat_id}#{message.id}#{message.from_user.id}#silme'),
        ]
    ]
    reply_markup = ikm(butonlar)

    try:
        cet = await bot.get_chat(chat_id)
    except (ChannelInvalid, ChannelPrivate):
        return await message.reply_text('Beni oraya yönetici olarak ekle ki görebileyim grubunu / kanalını')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply_text('Geçersiz kullanıcı adı.')
    except Exception as e:
        LOG.exception(e)
        return await message.reply_text(f'Errors - {e}')
    if not cet: return await message.reply_text('Çet yok?')
    try: total_users = await bot.get_chat_members_count(chat_id)
    except Exception: total_users = None
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except Exception:
        return await message.reply_text('Kanalın / Grubun gizliyse beni yönetici yapmalısın.')
    if k.empty:
        return await message.reply_text('Kanalın / Grubun gizliyse beni yönetici yapmalısın.')
    tosend = f"#{temp.MY_USERNAME}" \
            "\n#YeniIndexIstegi" \
            f"\n\nSohbet Adı: `{cet.title}`" \
            f"\nSohbet KA: @{cet.username}" \
            f"\nSohbet Kimliği: `{cet.id}`" \
            f"\nSohbet Üyeleri: `{str(total_users)}`" \
            f"\nSohbet DC: `{cet.dc_id}`" \
            f"\n\nİndexleyen Adı: {message.from_user.mention} (`{message.from_user.id}`)" \
            f"\nİndexleyen Soyadı: `{message.from_user.last_name}`" + \
            f"\nİndexleyen Kimliği: @{message.from_user.username}" + \
            f"\nİndexleyen DC: `{message.from_user.dc_id}`" \
            f"\nİndexleyen Dil: `{message.from_user.language_code}`" \
            f"\nİndexleyen Link: tg://user?id={str(message.from_user.id)}" \
            f'\n\nBaş ID: `{str(temp.INDEX_FROM)}`' \
            f'\nSon ID: `{last_msg_id}`' \
            f'\n\n5. mesajdan başla: `/skip 5`' \
            f'\nDetaylar: `/izinler {cet.id}`' \
            f"\nTarih: `{guncelTarih()}`"
    if message.from_user.id in ADMINS:
        return await message.reply_text(tosend, reply_markup=reply_markup)
    if type(chat_id) is int:
        try: link = (await bot.create_chat_invite_link(chat_id)).invite_link
        except ChatAdminRequired:
            return await message.reply_text('Bisi kanalınısda yönetici yapın kıymetlim? Yapınca tekrar deneyin')
    else: link = f"@{message.forward_from_chat.username}"
    tosend += f"\nLink: {link}"
    await bot.send_message(LOG_CHANNEL, tosend, reply_markup=reply_markup)
    await message.reply_text('Katkılarınız için teşekkürler. Moderatörlerimiz içeriğinizi inceledikten sonra size buradan dönüş yapacak.')

@Client.on_message(filters.command('skip') & filters.user(ADMINS))
async def set_skip_number(bot, message:Message):
    if ' ' in message.text:
        _, skip = message.text.split(" ")
        try: skip = int(skip)
        except Exception: return await message.reply_text("Bir sayı ver")
        LOG.info(f'skip set to {skip}')
        await message.reply_text(f"{skip}. mesajdan itibaren kaydetmeye başlayacağım.")
        temp.INDEX_FROM = int(skip)
    else:
        await message.reply_text("Bir sayı ver")

async def index_files_to_db(lst_msg_id, chat, msg:Message, bot:Client, dbindex):
    try:
        cet = await bot.get_chat(chat)
    except (ChannelInvalid, ChannelPrivate):
        return await msg.edit_text('Beni oraya yönetici olarak ekle ki görebileyim grubunu / kanalını')
    except (UsernameInvalid, UsernameNotModified):
        return await msg.edit_text('Geçersiz kullanıcı adı.')
    except Exception as e:
        LOG.exception(e)
        return await msg.edit_text(f'Errors - {e}')
    if not cet: return await msg.edit_text('Çet yok?')
    cetbilgisi = f"Çet: `{cet.title}`" \
            f"\nÇet KA: @{cet.username}" \
            f"\nÇet Kimliği: `{cet.id}`" \
            f"\nÇet DC: `{cet.dc_id}`" \
            f'\nBaş ID: `{str(temp.INDEX_FROM)}`' \
            f'\nSon ID: `{str(lst_msg_id)}`' \
            f"\n\n#{temp.MY_USERNAME}" \
            "\n#Indexleme"
    kaydedilen = klonid = allerr = validerr = deleted = no_media = unsupported = esgec = klonadboyut = hiz = 0
    starting = time.time()
    async with lock:
        LOG.info('INDEXSTART')
        total = lst_msg_id + 1
        current = temp.INDEX_FROM
        temp.CANCEL = False
        try:
            await msg.pin(both_sides=True)
            while current < total:
                try:
                    message = await bot.get_messages(chat_id=chat, message_ids=current, replies=0)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    message = await bot.get_messages(chat_id=chat, message_ids=current, replies=0)
                except Exception as e:
                    LOG.exception(e)
                try:
                    hiz = ((current - temp.INDEX_FROM) / ((time.time() - starting).__round__())).__round__()
                except Exception:
                    hiz = 0
                if temp.CANCEL:
                    tosend = get_progressbar()
                    tosend += f"\n\n{cetbilgisi}\n#IndexlemeIptali" \
                    f"\n\n`{kaydedilen}` Dosya başarıyla kaydedildi!" \
                    f"\nAtlanan Silinen Mesajlar: `{deleted}`" \
                    f"\nAtlanan Medya Dışı: `{no_media}`" \
                    f"\nAtlanan Desteklenmeyen: `{unsupported}`" \
                    f"\nAtlanan Klonlar (dosya kimliği): `{klonid}`" \
                    f"\nAtlanan Klonlar (isim & boyut): `{klonadboyut}`" \
                    f"\nEs Geçilenler: `{esgec}`" \
                    f"\nValid Hataları: `{validerr}`" \
                    f"\nTüm Hatalar: `{allerr}`" \
                    f"\nGeçen Süre: `{ReadableTime(time.time() - starting)}`" \
                    f"\nHız: `{hiz} öge/saniye`" \
                    f"\nSonraki İndex: `/skip {current - 10}`" \
                    f'\nBot Ömrü: `{ReadableTime(time.time() - botStartTime)}`' \
                    f'\nİS Ömrü: `{ReadableTime(time.time() - boot_time())}`'
                    temp.INDEX_FROM = 1
                    await msg.unpin()
                    return await msg.edit_text(tosend)
                current += 1
                # kaçta bir güncellesin
                kactabir = 30 if dbindex else 200
                if current % kactabir == 0:
                    reply = ikm([[ikb('❌ İptal', callback_data='index_cancel')]])
                    try:
                        tosend = f"% {'{:.3f}'.format(((current - temp.INDEX_FROM) * 100 / (total - temp.INDEX_FROM)))} "
                        tosend += get_progressbar(current - temp.INDEX_FROM, total - temp.INDEX_FROM)
                        tosend += f"\n\n{cetbilgisi}\n#IndexlemeSürüyor" \
                        f"\n\nİşlenen İleti: `{current - temp.INDEX_FROM}`" \
                        f"\nİşlenecek İleti: `{total - current}`" \
                        f"\nToplam kaydedilen: `{kaydedilen}`" \
                        f"\nAtlanan Silinen Mesajlar: `{deleted}`" \
                        f"\nAtlanan Medya Dışı: `{no_media}`" \
                        f"\nAtlanan Desteklenmeyen: `{unsupported}`" \
                        f"\nAtlanan Klonlar (dosya kimliği): `{klonid}`" \
                        f"\nAtlanan Klonlar (isim & boyut): `{klonadboyut}`" \
                        f"\nEs Geçilenler: `{esgec}`" \
                        f"\nValid Hataları: `{validerr}`" \
                        f"\nTüm Hatalar: `{allerr}`" \
                        f"\nGeçen Süre: `{ReadableTime(time.time() - starting)}`" \
                        f"\nKalan Süre: `{ReadableTime((total - current) / hiz)}`" \
                        f"\nYüzde: % `{'{:.7f}'.format(((current - temp.INDEX_FROM) * 100 / (total - temp.INDEX_FROM)))}`" \
                        f"\nHız: `{hiz} öge/saniye`" \
                        f"\nSonraki İndex: `/skip {current - 10}`" \
                        f'\nBot Ömrü: `{ReadableTime(time.time() - botStartTime)}`' \
                        f'\nİS Ömrü: `{ReadableTime(time.time() - boot_time())}`'
                        await msg.edit_text(text=tosend, reply_markup=reply)
                    except Exception: pass
                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [MessageMediaType.AUDIO, MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
                    unsupported += 1
                    continue
                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue
                if dbindex:
                    media.file_type = message.media.value
                    media.caption = message.caption
                    res = await save_file(media)
                    if res == 'saved': kaydedilen = kaydedilen + 1
                    elif res == 'klonid': klonid = klonid + 1
                    elif res == 'validerr': validerr = validerr + 1
                    elif res == 'allerr': allerr = allerr + 1
                    elif res == 'esgec': esgec = esgec + 1
                    elif res == 'klonadboyut': klonadboyut = klonadboyut + 1
        except Exception as e:
            LOG.exception(e)
            await msg.edit_text(f'Error: {e}')
            await msg.unpin()
        else:
            tosend = get_progressbar()
            tosend += f"\n\n{cetbilgisi}\n#IndexlemeSonu" \
            f'\n\n`{kaydedilen}` Dosya başarıyla kaydedildi!' \
            f"\nAtlanan Silinen Mesajlar: `{deleted}`" \
            f"\nAtlanan Medya Dışı: `{no_media}`" \
            f"\nAtlanan Desteklenmeyen: `{unsupported}`" \
            f"\nAtlanan Klonlar (dosya kimliği): `{klonid}`" \
            f"\nAtlanan Klonlar (isim & boyut): `{klonadboyut}`" \
            f"\nEs Geçilenler: `{esgec}`" \
            f"\nValid Hataları: `{validerr}`" \
            f"\nTüm Hatalar: `{allerr}`" \
            f'\nGeçen Süre: `{ReadableTime(time.time() - starting)}`' \
            f'\nHız: `{hiz} öge/saniye`' \
            f"\nSonraki İndex: `/skip {current - 10}`" \
            f'\nBot Ömrü: `{ReadableTime(time.time() - botStartTime)}`' \
            f'\nİS Ömrü: `{ReadableTime(time.time() - boot_time())}`'
            await msg.edit_text(tosend)
            temp.INDEX_FROM = 1
            await msg.reply_text('İndexleme bitti.', quote=True, disable_notification=False)
            await msg.unpin()
        LOG.info('INDEXFINISH')
