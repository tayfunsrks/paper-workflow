# Property of Kor.PiracyTeam - GNU General Public License v2.0

import contextlib
from helpers.koleler import add_slave, del_slave, get_slaves, testClient

from info import ADMINS
import hashlib, os, asyncio, re, time, heroku3
from sys import executable
from pyrogram.types.messages_and_media.message import Message
from database.filters_mdb import delete_all_files, delete_all_groups, delete_all_users
from helpers.humanbytes import humanbytes
from helpers.temizleyici import sonsuz_sil
from helpers.timeformat import ReadableTime
from helpers.virustotal import get_result, getResultAsReadable
from helpers.guncelTarih import guncelTarih
from helpers.settings import Settings
from helpers.wayback import saveWebPage
from io import BytesIO
from pyrogram.errors import (
    ChatAdminRequired,
    PeerIdInvalid,
    UserIsBlocked,
    MessageTooLong
)
from helpers.yardimMesajlari import yardimMesaji
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton as ikb, InlineKeyboardMarkup as ikm, CallbackQuery
from pyrogram.enums import ParseMode, ChatType, MessageMediaType
from database.ia_filterdb import Media, get_file_details, get_search_results, unpack_new_file_id
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, CUSTOM_CAPTION, DISABLE_INDEXER, FILE_PROTECTED, \
    GEN_CHAT_LINK_DELAY, HEROKU_API_KEY, HEROKU_APP_NAME, INDEXER_MAX, JOIN_CHANNEL_WARNING, LOG_CHANNEL, LOGIN_MODE, LOGIN_PASSWORD, LOGIN_WARNING, START_TXT, REQUEST_LINK, THUMB_FILE, VIRUSTOTAL_API, VIRUSTOTAL_FREE, YOU_BANNED_MSG
from utils import get_size, is_logged_in, is_subscribed, temp

# Get logging configurations
from info import LOG

@Client.on_message(~filters.channel & filters.command(["start", "help", "h", "y", "yardım", "yardim", "stats"]))
async def start(client: Client, message: Message):
    # kanala katıldı mı & özeli kontrol et
    if message.chat.type == ChatType.PRIVATE:
        if message.from_user.id in temp.BANNED_USERS:
            banstatus = await db.get_ban_status(message.from_user.id)
            return await message.reply_text(f'Banlanmışsın.\nSebep: {banstatus["ban_reason"]}') if YOU_BANNED_MSG else await message.delete(revoke=True)
        elif not await is_subscribed(client, message):
            if JOIN_CHANNEL_WARNING:
                try:
                    link = await client.create_chat_invite_link(
                        chat_id=AUTH_CHANNEL,
                        creates_join_request=REQUEST_LINK,
                        name=temp.MY_USERNAME, member_limit=None if REQUEST_LINK else 1)
                except ChatAdminRequired:
                    return await client.send_message(LOG_CHANNEL, "Auth kanalında admin değilim. Link oluşturamıyorum.")
                except Exception as e:
                    return await client.send_message(LOG_CHANNEL, f'Link oluştururken hata:\n{str(e)}')
                temp.join_chnl_msg = await message.reply_text(
                    "Botu kullanmak için kanalıma abone olmalısınız." + \
                    "\nKatıldıktan sonra tekrar deneyin.", disable_web_page_preview=True,
                    reply_markup=ikm([[ikb('Katıl', url=link.invite_link)]])
                )
            return await message.delete(revoke=True)
        elif not await is_logged_in(message):
            return await message.delete(revoke=True)
        # kullanıcıyı dbye ekle
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            if LOG_CHANNEL:
                yeni = message.from_user
                keyboard = ikm([[ikb("🔥 Yasakla", callback_data=f'ban#{message.from_user.id}'),
                    ikb('❌ Kapat', callback_data='kapat')]])
                await client.send_message(LOG_CHANNEL,
                    f"#{temp.MY_USERNAME}" \
                    "\n#YeniKullanıcı" \
                    f"\n\nAd: `{yeni.first_name}`" \
                    f"\nSoyad: `{yeni.last_name}`" \
                    f"\nKullanıcı Adı: @{yeni.username}" \
                    f"\nID: `{yeni.id}`" \
                    f"\nEtiket: {yeni.mention}" \
                    f"\nDC: `{yeni.dc_id}`" \
                    f"\nDil: `{yeni.language_code}`" \
                    f"\nLink: tg://user?id={str(yeni.id)}" \
                    f"\nTarih: `{guncelTarih()}`",
                    reply_markup=keyboard
                )
    elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        if message.chat.id in temp.BANNED_CHATS:
            k = await client.send_message(
                chat_id=message.chat.id,
                text='Bu sohbeti sahibim yasaklamış. Elveda.'
            )
            try: await k.pin()
            except Exception: pass
            return await client.leave_chat(message.chat.id)
        reply_markup = ikm(temp.start_btns)
        await message.reply_text(START_TXT.format(
            message.from_user.mention if message.from_user else message.chat.title, temp.MY_USERNAME, temp.MY_NAME),
            reply_markup=reply_markup, disable_web_page_preview=True)
        await asyncio.sleep(1)
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            r_j = message.from_user.mention if message.from_user else "Anonim"
            yeni = message.chat
            tosend = f"#{temp.MY_USERNAME}" \
                "\n#YeniGrup" \
                f"\n\nAd: `{yeni.title}`" \
                f"\nKullanıcı Adı: @{yeni.username}" \
                f"\nID: `{yeni.id}`" \
                f"\nÜye: `{total}`" \
                f"\nEkleyen: {r_j} (`{message.from_user.id}`)" \
                f"\nDC: `{yeni.dc_id}`" \
                f"\nTarih: `{guncelTarih()}`"
            await db.add_chat(message.chat.id, message.chat.title)
            grubaeklendi = await client.send_message(LOG_CHANNEL, tosend)
            # grup linki ?s
            await asyncio.sleep(GEN_CHAT_LINK_DELAY*60)
            try: gruplink = await client.create_chat_invite_link(yeni.id)
            except Exception: gruplink = None
            try: silebilir = (await client.get_chat_member(yeni.id,temp.MY_ID)).privileges.can_delete_messages
            except Exception: silebilir = False
            await asyncio.sleep(1)
            if gruplink:
                tosend = f"#{temp.MY_USERNAME}" \
                "\n#YeniLink" \
                f"\n\nLink: {gruplink.invite_link}" \
                f"\nTarih: {gruplink.date}" \
                f"\nSilebilir: {str(silebilir)}"
                await grubaeklendi.reply_text(tosend, quote=True)
        return

    # normal start komutysa start texti gönder
    if len(message.command) != 2:
        reply_markup = ikm(temp.start_btns)
        return await message.reply_text(
            text=START_TXT.format(
            message.from_user.mention if message.from_user else message.chat.title, temp.MY_USERNAME, temp.MY_NAME),
            reply_markup=reply_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    # ayarlar için mi geldi?
    elif message.command[1] == 'settings':
        buttons= [
            [ikb('◀️ Geri', callback_data='start'),
            ikb('😊 Ayarlar', callback_data='settings#0'),
            ikb('❌ Kapat', callback_data='kapat')]
        ]
        return await message.reply_text('Ayarlarınıs için özeli kullanmalısınıs kıymetlim. Tıklayın.',
        reply_markup=ikm(buttons)
        )
    file_id = message.command[1]
    files_ = await get_file_details(file_id)
    if not files_:
        delo = await message.reply_text("Bulamadık bir şey kıymetlim?\nArama ipuçlarını öğrendinis mi?: /yardim")
        await asyncio.sleep(11)
        return await delo.delete()
    files = files_[0]
    f_caption = files.caption
    f_caption += '' if (CUSTOM_CAPTION is None) or (len(f_caption) > 1024) else f'\n{CUSTOM_CAPTION}'
    ho = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=FILE_PROTECTED
    )
    await yardimMesaji(str(files.file_name), ho)
    temp.today_sent_bytes += int(files.file_size)
    await message.delete()

@Client.on_message(filters.private & filters.command('kanal') & filters.user(ADMINS))
async def channel_info(bot:Client, message:Message):
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **İndekslenen kanallar/gruplar**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Toplam:** {len(CHANNELS)}'

    if len(text) < 1024:
        await message.reply_text(text, quote=True)
    else:
        file = 'İndekslenen kanallar.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file, quote=True, thumb=THUMB_FILE)
        os.remove(file)
    await message.delete()

@Client.on_message(filters.private & filters.command('sil') & filters.user(ADMINS))
async def delete(bot, message:Message):
    """Delete file from database"""
    reply = message.reply_to_message
    if not (reply and reply.media):
        return await reply.reply_text('Silmek istediğiniz dosyayı /sil ile yanıtlayın', quote=True)
    msg = await reply.reply_text("İşleniyor...⏳", quote=True)
    for file_type in (MessageMediaType.DOCUMENT, MessageMediaType.VIDEO, MessageMediaType.AUDIO):
        media = getattr(reply, file_type.value, None)
        if media is not None:
            break
    else:
        return await msg.edit('Bu desteklenen bir dosya biçimi değil.')

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('Dosya veritabanından başarıyla silindi.')
    else:
        # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf
        # #diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39
        # have original file name.
        result = await Media.collection.delete_one({
            'file_name': media.file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
        })
        if result.deleted_count:
            await msg.edit('Dosya veritabanından başarıyla silindi.')
        else:
            await msg.edit('Veritabanında dosya bulunamadı.')
    await message.delete()

@Client.on_message(filters.private & filters.regex(r'^\/deleteall+.*$') & filters.user(ADMINS))
async def delete_all_index(bot, message:Message):
    tayp = ''
    if message.text.lower() == '/deleteallfiles': tayp = 'Dosyalar'
    elif message.text.lower() == '/deleteallusers': tayp = 'Kullanıcılar'
    elif message.text.lower() == '/deleteallgroups': tayp = 'Gruplar'
    else: return

    await message.reply_text(
        f'Tüm {tayp.lower()} silinecek.\nDevam etmek istiyor musunuz?',
        reply_markup=ikm(
            [
                [ikb(text=f"Tüm {tayp}ı Sil", callback_data=f"deleteall#{tayp}")],
                [ikb(text="❌ İptal", callback_data="kapat")]
            ]
        ),
        quote=True
    )
    await message.delete()

@Client.on_callback_query(filters.regex(r'^deleteall+.*$'))
async def delete_all_confirm(bot, query:CallbackQuery):
    nesilincek = query.data.split("#")[1]
    if nesilincek == 'Dosyalar':
        await delete_all_files(query.message)
    elif nesilincek == 'Kullanıcılar':
        await delete_all_users(query.message)
    elif nesilincek == 'Gruplar':
        await delete_all_groups(query.message)
    else:
        return query.message.edit(f'deleteall yaparken sorun çıktı ?')
    
@Client.on_message(filters.private & filters.command(['log', 'logs']) & filters.user(ADMINS))
async def log_file(bot, message: Message):
    """Send log file"""
    analogdosyasi = 'log.log.txt'
    try:
        if len(message.command) == 1:
            await message.reply_document(analogdosyasi, quote=True, reply_markup=ikm(temp.kapat_btn), thumb=THUMB_FILE, caption=f'{guncelTarih()}\ntekrar? > /log\nbir de şunu dene > `/log 10`')

        elif len(message.command) == 2:
            try:
                sayi = int(message.command[1])
                with open(analogdosyasi, "r") as dosya:
                    lines = dosya.readlines()
                    son = ''.join(lines[-sayi:])
                    son = sonsuz_sil(son, '\n\n', '\n')
                    if son.endswith('\n'):
                        son = son[:-2]
                dosyaadi = f'son {sayi} satır.log.txt'
                with open(dosyaadi, 'w+') as outfile:
                    outfile.write(son)
                await message.reply_document(dosyaadi, thumb=THUMB_FILE, reply_markup=ikm(temp.kapat_btn), caption=f'{guncelTarih()}\n/log - `/log {sayi}`')

                with contextlib.suppress(Exception):
                    os.remove(dosyaadi)
            except Exception as e:
                await message.reply_document(analogdosyasi, thumb=THUMB_FILE, caption=f'Muhtemelen tamsayı vermediniz. Hata:\n{str(e)}\n{guncelTarih()}', quote=True, reply_markup=ikm(temp.kapat_btn))

    except Exception as e:
        await message.reply_text(e, reply_markup=ikm(temp.kapat_btn))
    await message.delete()

@Client.on_message(filters.private & filters.command(["ayarlar", "settings"]))
async def settings_handler(client: Client, message: Message):
    if not message.from_user:
        return await message.delete(revoke=True)
    elif message.from_user.id in temp.BANNED_USERS:
        return await message.delete(revoke=True)
    elif not await is_subscribed(client, message):
        return await message.delete(revoke=True)
    elif not await is_logged_in(message):
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
    elif not await is_subscribed(client, message):
        return await message.delete(revoke=True)
    elif not await is_logged_in(message):
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
    elif not await is_subscribed(client, message):
        return await message.delete(revoke=True)
    elif not await is_logged_in(message):
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
        LOG.exception(e)
    await message.delete()

@Client.on_message(filters.private & filters.command("virustotal"))
async def virustotal(client: Client, message: Message):
    if not message.from_user:
        return await message.delete(revoke=True)
    elif message.from_user.id in temp.BANNED_USERS:
        return await message.delete(revoke=True)
    elif not await is_subscribed(client, message):
        return await message.delete(revoke=True)
    elif not await is_logged_in(message):
        return await message.delete(revoke=True)
    elif not VIRUSTOTAL_API:
        return LOG.error("VIRUSTOTAL_API not provided.")
    VtPath = os.path.join("Virustotal", str(message.from_user.id))
    if not os.path.exists("Virustotal"):
        os.makedirs("Virustotal")
    if not os.path.exists(VtPath):
        os.makedirs(VtPath)
    link = None
    if message.reply_to_message:
        if message.reply_to_message.document:
            maxsize = 32 * 1024 * 1024 if VIRUSTOTAL_FREE else 210 * 1024 * 1024
            if message.reply_to_message.document.file_size > maxsize:
                return await message.reply_text(f'Dosya limiti {humanbytes(maxsize)}', quote=True, reply_markup=ikm(temp.kapat_btn))

            try:
                sent = await message.reply_text('İndiriyorum efendim birass (10 dk) bekle', quote=True)

                filename = os.path.join(VtPath, message.reply_to_message.document.file_name)
                link = await client.download_media(message=message.reply_to_message.document, file_name=filename)

            except Exception as e:
                LOG.exception(e)
        else:
            link = message.reply_to_message.text
    else:
        if len(message.command) != 2:
            help_msg = "Dosyayı içeren mesaja yanıtla kıymetlim. Ya da hash biliyorsan ona yanıtla."
            return await message.reply_text(help_msg, quote=True, reply_markup=ikm(temp.kapat_btn))
        link = message.command[1]
        sent = await message.reply_text('Kontrol ediyorum efendimiss', quote=True)
    ret = getResultAsReadable(get_result(link))
    with contextlib.suppress(Exception):
        os.remove(link)
    await sent.edit_text(ret, reply_markup=ikm(temp.kapat_btn))
    await message.delete()

@Client.on_message(filters.private & filters.command("hash"))
async def hasher(client:Client, message:Message):
    if not message.from_user:
        return await message.delete(revoke=True)
    elif message.from_user.id in temp.BANNED_USERS:
        return await message.delete(revoke=True)
    elif not await is_subscribed(client, message):
        return await message.delete(revoke=True)
    elif not await is_logged_in(message):
        return await message.delete(revoke=True)
    mediamessage = message.reply_to_message
    help_msg = "Dosyanı bu komutla yanıtla ki hesaplayabileyim efendi"
    if not mediamessage: return await message.reply_text(help_msg, reply_markup=ikm(temp.kapat_btn))
    file = None
    media_array = [mediamessage.document, mediamessage.video, mediamessage.audio, mediamessage.document, \
        mediamessage.video, mediamessage.photo, mediamessage.audio, mediamessage.voice, \
        mediamessage.animation, mediamessage.video_note, mediamessage.sticker]
    for i in media_array:
        if i is not None:
            file = i
            break
    if not file: return await message.reply_text(help_msg, reply_markup=ikm(temp.kapat_btn))
    VtPath = os.path.join("Hasher", str(message.from_user.id))
    if not os.path.exists("Hasher"): os.makedirs("Hasher")
    if not os.path.exists(VtPath): os.makedirs(VtPath)
    sent = await message.reply_text('İndiriyorum efendim birass bekle', quote=True)
    try:
        filename = os.path.join(VtPath, file.file_name)
        inen = await client.download_media(message=file, file_name=filename)
    except Exception as e:
        LOG.exception(e)
        try: os.remove(inen)
        except Exception: pass
        inen = None
    if not inen:
        return await sent.edit_text(
            'İndirirken hata oluştu efendi. Sonra dene',
            quote=True,
            reply_markup=ikm(temp.kapat_btn)
        )
    hashStartTime = time.time()
    try:
        with open(inen, "rb") as f:
            md5 = hashlib.md5()
            sha1 = hashlib.sha1()
            sha224 = hashlib.sha224()
            sha256 = hashlib.sha256()
            sha512 = hashlib.sha512()
            sha384 = hashlib.sha384()
            while chunk := f.read(8192):
                md5.update(chunk)
                sha1.update(chunk)
                sha224.update(chunk)
                sha256.update(chunk)
                sha512.update(chunk)
                sha384.update(chunk)
    except Exception as a:
        LOG.exception(str(a))
        try: os.remove(inen)
        except Exception: pass
        return await sent.edit_text('Hashlerken hata oluştu :(',
            quote=True,
            reply_markup=ikm(temp.kapat_btn)
        )
    try:
        # hash text
        finishedText = "🍆 Dosya: <code>{}</code>\n".format(file.file_name) + \
            "🍇 Boyut: <code>{}</code>\n".format(humanbytes(file.file_size)) + \
            "🍓 MD5: <code>{}</code>\n".format(md5.hexdigest()) + \
            "🍌 SHA1: <code>{}</code>\n".format(sha1.hexdigest()) + \
            "🍒 SHA224: <code>{}</code>\n".format(sha224.hexdigest()) + \
            "🍑 SHA256: <code>{}</code>\n".format(sha256.hexdigest()) + \
            "🍎 SHA384: <code>{}</code>\n".format(sha384.hexdigest()) + \
            "🥭 SHA512: <code>{}</code>\n".format(sha512.hexdigest()) + \
            f"🥚 Geçen Süre: <code>{ReadableTime((time.time() - hashStartTime) * 1000)}</code>"
        await sent.edit_text(finishedText, reply_markup=ikm(temp.kapat_btn))
        try: os.remove(inen)
        except Exception: pass
    except Exception as e:
        LOG.exception(e)
    await message.delete()

@Client.on_message(filters.private & filters.command("json") & filters.user(ADMINS))
async def jsonner(client:Client, message:Message):
    if not message.reply_to_message:
        return await message.reply_text('Bir mesaj seç ki onu jsonlayayım efendimiss')
    json_msg = message.reply_to_message
    try:
        await message.reply_text(
            f"<code>{json_msg}</code>",
            quote=True,
            disable_web_page_preview=True,
            reply_markup=ikm(temp.kapat_btn)
        )
    except (PeerIdInvalid, UserIsBlocked):
        pass
    except MessageTooLong:
        with BytesIO(str.encode(str(json_msg),encoding='utf-8')) as out_file:
            out_file.name = "json.txt"
            await message.reply_document(
                document=out_file,
                caption='jsonladım efendimiss',
                quote=True,
                thumb=THUMB_FILE,
                reply_markup=ikm(temp.kapat_btn)
            )
    except Exception as f:
        LOG.exception(f)
    await message.delete()

@Client.on_message(filters.private & filters.command("index") & filters.text)
async def file_indexer(client:Client, message:Message):
    if not message.from_user: return await message.delete(revoke=True)
    elif message.from_user.id in temp.BANNED_USERS:
        return await message.delete(revoke=True)
    elif DISABLE_INDEXER and message.from_user.id not in ADMINS:
        return await message.delete(revoke=True)
    elif not await is_subscribed(client, message):
        return await message.delete(revoke=True)
    elif not await is_logged_in(message):
        return await message.delete(revoke=True)
    if message.reply_to_message or (not len(message.command) > 1):
        return await message.reply_text(
            'Neyi indexleyim kıymetli?' \
            '\n\nSonuna tip eklersen ona göre bulurum.\n- Tipler: video, document, audio' \
            '\nŞu şekilde belirtebilirsin:\n- Örnek: `/index atsız bozkurtlar | document`' \
            '\nTüm tipler için sadece arama terimini yaz:\n- Örnek: `/index atsız bozkurtlar`' \
            )
    query = message.text.split(' ', 1)[1]
    if '|' in query:
        text, file_type = query.split('|', 1)
        text = text.strip()
        file_type = file_type.strip().lower()
    else:
        text = query.strip()
        file_type = None
    if text.lower() in ['pdf','epub','mobi','exe','doc','docx','pptx','ppt','mp4','mkv','avi','mp3','m4a','flac','rar','zip','7z','0001','0002']:
        return await message.reply_text('Lütfen daha açıklayıcı ol. Örnek: `/index atsız bozkurtlar`')
    if not 3 < len(text) < 100:
        return await message.reply_text('Çok kısa veya ok uzun oldu arama terimin.')
    try:
        bekle = await message.reply_text('İndexlemeye çalışıyorum kıymetlimiss bekle birass', quote=True)
        files, of, total = await get_search_results(text, file_type=file_type, max_results=INDEXER_MAX, offset=0)
        if not files:
            return await bekle.edit_text("Bulamadık bir şey kıymetlim?\nArama ipuçlarını öğrendinis mi?: /yardim")
        indexbilgi = f'Arama Terimi: {text}\nToplam {total} sonuç.'
        tip = file_type if file_type else 'Tümü'
        indexbilgi += f'\nDosya Tipi: {tip}\nTarih: {guncelTarih()}'
        indexbilgi += '\nEn yukarıdakiler en son eklenenlerdir.'
        alllist = indexbilgi
        sira = 0
        for file in files:
            sira = sira + 1
            fn = file.file_name.replace('.', ' ')
            alllist += f'\n\n{sira}: {fn}'
            alllist += f'\nBoyut: {get_size(file.file_size)}, Tip: {file.file_type}'
        try:
            await bekle.edit_text(
                alllist,
                disable_web_page_preview=True,
                reply_markup=ikm(temp.kapat_btn)
            )
        except (PeerIdInvalid, UserIsBlocked):
            pass
        except MessageTooLong:
            with BytesIO(str.encode(str(alllist),encoding='utf-8')) as out_file:
                out_file.name = "index.txt"
                await message.reply_document(
                    document=out_file,
                    caption=indexbilgi,
                    thumb=THUMB_FILE,
                    quote=True,
                    reply_markup=ikm(temp.kapat_btn)
                )
            await bekle.delete()
    except Exception as e:
        LOG.exception(e)

@Client.on_message(filters.private & filters.command(["login", "giris"]))
async def login(client: Client, message: Message):
    if not LOGIN_MODE:
        return
    elif not message.from_user:
        return await message.delete(revoke=True)
    elif message.from_user.id in temp.BANNED_USERS:
        return await message.delete(revoke=True)
    elif not await is_subscribed(client, message):
        return await message.delete(revoke=True)
    elif not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await asyncio.sleep(1)
    yeni = message.from_user
    giris = await db.get_login(message.from_user.id) or message.from_user.id in temp.LOGGED_IN_USERS
    keyboard = ikm([[ikb("🔥 Yasakla", callback_data=f'ban#{message.from_user.id}'),
                    ikb('❌ Kapat', callback_data='kapat')]])
    if giris:
        await message.delete(revoke=True)
        if LOGIN_WARNING:
            go = await message.reply_text('Zaten giriş yaptınız. İyi kullanımlar.')
            await asyncio.sleep(11)
            await go.delete(revoke=True)
        return
    elif len(message.command) <= 1:
        if LOGIN_WARNING:
            await message.reply_text('Boşluk bırakıp parolanızı girin. Örnek: `/giris parooolaaburayaa`')
        return
    elif not message.text.split(' ', 1)[1].strip() in LOGIN_PASSWORD:
        await message.delete(revoke=True)
        if LOGIN_WARNING:
            go = await message.reply_text('Yanlış parola.')
            await asyncio.sleep(11)
            await go.delete(revoke=True)
            tosend = f"#{temp.MY_USERNAME}" \
                "\n#YeniBaşarısızGiriş" \
                f"\n\nAd: `{yeni.first_name}`" \
                f"\nSoyad: `{yeni.last_name}`" \
                f"\nKullanıcı Adı: @{yeni.username}" \
                f"\nID: `{yeni.id}`" \
                f"\nEtiket: {yeni.mention}" \
                f"\nDC: `{yeni.dc_id}`" \
                f"\nDil: `{yeni.language_code}`" \
                f"\nLink: tg://user?id={str(yeni.id)}" \
                f"\nParola: {message.text.split(' ', 1)[1].strip()}" \
                f"\nTarih: `{guncelTarih()}`"
            await asyncio.sleep(1)
            await client.send_message(LOG_CHANNEL, tosend, reply_markup=keyboard)
        return
    await asyncio.sleep(1)
    await db.set_login(message.from_user.id)
    temp.LOGGED_IN_USERS.append(message.from_user.id)
    await message.reply_text('Başarıyla giriş yaptınız. İyi kullanımlar.\nTelegramı kapatıp yeniden girmeni öneririm.\nKullanım için tıklayın: /start')
    
    tosend = f"#{temp.MY_USERNAME}" \
        "\n#YeniBaşarılıGiriş" \
        f"\n\nAd: `{yeni.first_name}`" \
        f"\nSoyad: `{yeni.last_name}`" \
        f"\nKullanıcı Adı: @{yeni.username}" \
        f"\nID: `{yeni.id}`" \
        f"\nEtiket: {yeni.mention}" \
        f"\nDC: `{yeni.dc_id}`" \
        f"\nDil: `{yeni.language_code}`" \
        f"\nLink: tg://user?id={str(yeni.id)}" \
        f"\nParola: {message.text.split(' ', 1)[1].strip()}" \
        f"\nTarih: `{guncelTarih()}`"
    await asyncio.sleep(1)
    await client.send_message(LOG_CHANNEL, tosend, reply_markup=keyboard)

@Client.on_message(~filters.channel & filters.command("id"))
async def aydi(client: Client, message: Message):
    if not message.from_user:
        return await message.delete(revoke=True)
    elif message.from_user.id in temp.BANNED_USERS:
        return await message.delete(revoke=True)
    elif not await is_subscribed(client, message):
        return await message.delete(revoke=True)
    elif not await is_logged_in(message):
        return await message.delete(revoke=True)
    await message.reply_text(f"Buranın ID'si: `{message.chat.id}`", reply_markup=ikm(temp.kapat_btn))

@Client.on_message(filters.private & filters.command("restart") & filters.user(ADMINS))
async def restart(client:Client, message:Message):
    cmd = message.text.split(' ', 1)
    dynoRestart = False
    dynoKill = False
    if len(cmd) == 2:
        dynoRestart = (cmd[1].lower()).startswith('d')
        dynoKill = (cmd[1].lower()).startswith('k')
    if (not HEROKU_API_KEY) or (not HEROKU_APP_NAME):
        LOG.info("If you want Heroku features, fill HEROKU_APP_NAME HEROKU_API_KEY vars.")
        dynoRestart = False
        dynoKill = False
    if dynoRestart:
        LOG.info("Dyno Restarting.")
        await message.reply_text("Dyno Restarting.", reply_markup=ikm(temp.kapat_btn))
        heroku_conn = heroku3.from_key(HEROKU_API_KEY)
        app = heroku_conn.app(HEROKU_APP_NAME)
        app.restart()
    elif dynoKill:
        LOG.info("Killing Dyno. MUHAHAHA")
        await message.reply_text("Killed Dyno.", reply_markup=ikm(temp.kapat_btn))
        heroku_conn = heroku3.from_key(HEROKU_API_KEY)
        app = heroku_conn.app(HEROKU_APP_NAME)
        proclist = app.process_formation()
        for po in proclist:
            app.process_formation()[po.type].scale(0)
    else:
        LOG.info("Normally Restarting.")
        await message.reply_text("Normally Restarting.", reply_markup=ikm(temp.kapat_btn))
        os.execl(executable, executable, "bot.py")

@Client.on_message(filters.private & filters.command(["kole", "slave", "köle"]) & filters.user(ADMINS))
async def koleekle(client:Client, message:Message):
    if message.reply_to_message:
        denemetokeni = message.reply_to_message.text
    else:
        yo = message.command
        if len(yo) != 2:
            return await message.reply_text("/kole kölebotapi\nşeklinde kullanınız.", reply_markup=ikm(temp.kapat_btn))
        denemetokeni = yo[1]
    bekle = await message.reply_text("Bot test ediliyor...")
    kod, hata, kuladi = await testClient(denemetokeni)
    
    if kod == 200:
        add_slave(denemetokeni, kuladi)
        tosend = f"#{temp.MY_USERNAME}" \
            "\n#YeniKöleBot" \
            f"\nKullanıcı adı: @{kuladi}" \
            f"\nTarih: `{guncelTarih()}`" \
            f"\nYeniden başlat: `/restart d`"
        await bekle.delete()
        await client.send_message(LOG_CHANNEL, tosend)
    else:
        await bekle.edit(f"Eklenemedi:\n\n{hata}")

@Client.on_message(filters.private & filters.command(["koleler", "slaves", "köleler"]) & filters.user(ADMINS))
async def klongoster(client:Client, message:Message):
    raju = await message.reply_text('Köle listesini getiriyoruss')
    nesne, sayi = get_slaves()
    out = "Köleler:\n\n"
    say = 0
    for chat in nesne:
        say = say + 1
        out += f"{say}: @{chat['uname']}\n`{chat['id']}`"
        out += '\n'
    out += '\n' + guncelTarih()
    try:
        await raju.edit_text(out,
                reply_markup=ikm(temp.kapat_btn))
    except MessageTooLong:
        dosyaadi = f'{temp.MY_USERNAME} köleler.txt'
        with open(dosyaadi, 'w+') as outfile:
            outfile.write(out)
        await message.reply_document(dosyaadi,
            caption=dosyaadi, thumb=THUMB_FILE,
            reply_markup=ikm(temp.kapat_btn)
        )
        try: os.remove(dosyaadi)
        except Exception: pass
    await message.delete()

@Client.on_message(filters.private & filters.command(["kolesil", "delslave", "kölesil"]) & filters.user(ADMINS))
async def klonsil(client:Client, message:Message):
    if message.reply_to_message:
        silinecek = message.reply_to_message.text
    else:
        yo = message.command
        if len(yo) != 2:
            return await message.reply_text("/kolesil kölebotapi | @botusername\nşeklinde kullanınız.", reply_markup=ikm(temp.kapat_btn))
        silinecek = yo[1]
    bekle = await message.reply_text("Köle siliniyor...")
    del_slave(silinecek)
    await bekle.edit(f"{silinecek} kölesi başarıyla silindi.\nkontrol: /koleler\nyeniden başlat: `/restart d`")
