# Property of Kor.PiracyTeam - GNU General Public License v2.0

import asyncio
import contextlib
from email import message
import math
import re
import ast
import time
import psutil
import shutil
from pyrogram.types import Message
from helpers.settings import Settings
from helpers.timeformat import ReadableTime
from helpers.yardimMesajlari import yardimMesaji
from info import BUTTON_COUNT_ENHANCER, CREATOR_USERNAME, DEF_BUTTON_COUNT, MAX_BUTTON_COUNT as mbc, \
    FILE_PROTECTED, MIN_BUTTON_COUNT, START_TXT, TEMP_CHANNEL, botStartTime, ABOUT_TXT
from info import ADMINS, AUTH_CHANNEL, CUSTOM_CAPTION, bot_version
from pyrogram.types import InlineKeyboardMarkup as ikm, InlineKeyboardButton as ikb, CallbackQuery
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.errors import UserIsBlocked, MessageNotModified, PeerIdInvalid, FloodWait
from utils import get_size, temp
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import(
   find_filter,
)
# Get logging configurations

BUTTONS = {}
SPELL_CHECK = {}

@Client.on_message(~filters.channel & ~filters.command(['giris', 'login']) & filters.text & filters.incoming)
async def give_filter(client:Client, message:Message):
    await auto_filter(client, message)

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(client, query: CallbackQuery):
    if query.from_user.id in temp.BANNED_USERS: return
    ident, req, key, offset = query.data.split("_")
    # arama sayfalarını kimler değiştirebilir?
    user_id = query.from_user.id
    if int(req) not in [user_id, 0] and user_id not in ADMINS:
        return await query.answer("Senin değil. Kendin arat :P", show_alert=True)
    try: offset = int(offset)
    except Exception: offset = 0
    search = BUTTONS.get(key)
    if not search:
        return await query.answer("O çok eskimiş. Yeniden arat aynı şeyi.",show_alert=True)
    ubc = await db.get_button_count(user_id)
    files, n_offset, total = await get_search_results(search, max_results=ubc, offset=offset, filtr=True)
    try: n_offset = int(n_offset)
    except Exception: n_offset = 0

    if not files: return
    btn = [[
            ikb(
                text=f"{get_size(file.file_size)} {file.file_name}", callback_data=f'files#{file.file_id}'
        )]
        for file in files
    ]

    if 0 < offset <= ubc:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - ubc
    if n_offset == 0 or math.ceil(offset/ubc+1) == math.ceil(total/ubc): # son sayfa
        btn.append(
            [
                ikb("◀️", callback_data=f"next_{req}_{key}_{off_set}"),
                ikb(f"📃 {math.ceil(total/ubc)} / {math.ceil(total/ubc)}", callback_data=f"pages#{total}"),
                ikb('ℹ️', callback_data='info#last'),
                ikb('❌', callback_data=f'kapat#{req}')
            ]
        )
    elif off_set is None: # ilk sayfa
        btn.append(
            [
                ikb(f"🗓 {math.ceil(offset/ubc+1)} / {math.ceil(total/ubc)}", callback_data=f"pages#{total}"),
                ikb("▶️", callback_data=f"next_{req}_{key}_{n_offset}"),
                ikb('ℹ️', callback_data='info#first'),
                ikb('❌', callback_data=f'kapat#{req}')
            ]),
    else: # orta sayfalar
        btn.append(
            [
                ikb("◀️", callback_data=f"next_{req}_{key}_{off_set}"),
                ikb(f"🗓 {math.ceil(offset/ubc+1)} / {math.ceil(total/ubc)}", callback_data=f"pages#{total}"),
                ikb("▶️", callback_data=f"next_{req}_{key}_{n_offset}"),
                ikb('❌', callback_data=f'kapat#{req}')
            ]
        )
    with contextlib.suppress(MessageNotModified):
        await query.edit_message_reply_markup(reply_markup=ikm(btn))
    await query.answer()

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    myusername = (await client.get_me()).username
    if user_id in temp.BANNED_USERS: return
    await db.add_user(user_id, query.from_user.first_name)
    if query.data.startswith('kapat'):
        try:
            uid = query.data.split('#')[1]
            if int(uid) not in [user_id, 0] and user_id not in ADMINS:
                await query.answer("Sisin olmayan şeysleri kapatamasssınıss kıymetli", show_alert=True)
            else:
                await query.message.delete()
        except Exception:
            await query.message.delete()
    elif query.data.startswith('info'):
        uid = query.data.split('#')[1]
        if uid == 'first':
            to = '🐼 Hoş geldin, Şu an ilk sayfadasın.\n🦜 Sonraki sayfalar için sağ butonuna tıkla.\n🌴 Kapatmak için çarpıya tıkla.\n🍍 Kendi ayarların için bana /ayarlar yaz.'

            await query.answer(to, show_alert=True)
        elif uid == 'last':
            to = '🐼 Şu an son sayfadasın.\n🦜 Önceki sayfalar için sol butonuna tıkla.\n🌴 Kapatmak için çarpıya tıkla.\n🍍 Kendi ayarların için bana /ayarlar yaz.'

            await query.answer(to, show_alert=True)
        elif uid == 'one':
            to = '🐼 Tek sayfa sonuç çıktı.\n🌴 Kapatmak için çarpıya tıkla.\n🍍 Kendi ayarların için bana /ayarlar yaz.'

            await query.answer(to, show_alert=True)
    elif query.data.startswith('settings'):
        uid = query.data.split('#')[1]
        if int(uid) not in [user_id, 0] and user_id not in ADMINS:
            return await query.answer("Bana özelden /ayarlar yaz.", show_alert=True)
        await query.answer("Sizin ayarlarınız kıymetlimis")
        await Settings(query.message)
    elif query.data == "notifon":
        notif = await db.get_notif(user_id)
        if notif:
            await query.answer("Bot bildirimleri kapatıldı.")
            await db.set_notif(user_id, False)
        else:
            await query.answer("Bot bildirimleri etkinleştirildi.")
            await db.set_notif(user_id, True)
        await Settings(query.message)
    elif query.data == "buttoncount":
        if BUTTON_COUNT_ENHANCER == 0:
            tore = f"Sahibim bu ayarı herkese kilitlemiş, değiştiremezsin :(\nHerkese: {DEF_BUTTON_COUNT} olarak ayarlanmış."

            return await query.answer(tore, show_alert=True)
        fromdb = await db.get_button_count(user_id)
        if fromdb >= mbc:
            await db.set_button_count(user_id, MIN_BUTTON_COUNT)
        else:
            await db.set_button_count(user_id, int(fromdb) + BUTTON_COUNT_ENHANCER)
        fromdb = await db.get_button_count(user_id)
        await query.answer(f"Buton sayınız artık {str(fromdb)}")
        await Settings(query.message)
    elif query.data == "about":
        await query.answer("Kıymetlimis hakkısında")
        buttons = [[ikb('◀️ Geri', callback_data='start'), ikb('🔮 İstatistikler', callback_data='stats'), ikb('❌ Kapat', callback_data='kapat')]]

        reply_markup = ikm(buttons)
        await query.message.edit_text(text=ABOUT_TXT.format("KorPiracy.Kitap"), reply_markup=reply_markup)

    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer("Bulamadık bir şey kıymetlim?\nArama ipuçlarını öğrendinis mi?: /yardim")

        files = files_[0]
        f_caption = files.caption
        f_caption += '' if CUSTOM_CAPTION is None or len(f_caption) > 1024 else f'\n{CUSTOM_CAPTION}'

        try:
            await query.answer('Dosya veritabanından aktarılıyor. Bekle.', show_alert=False)
            try:
                git = await temp.mainapp.send_cached_media(chat_id=TEMP_CHANNEL, file_id=file_id, caption=f_caption, protect_content=FILE_PROTECTED)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                git = await temp.mainapp.send_cached_media(chat_id=TEMP_CHANNEL, file_id=file_id, caption=f_caption, protect_content=FILE_PROTECTED)
            except Exception as e:
                return print(e)
            await asyncio.sleep(0.5)
            try:
                gel = await client.get_messages(chat_id=TEMP_CHANNEL, message_ids=git.id, replies=0)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                gel = await client.get_messages(chat_id=TEMP_CHANNEL, message_ids=git.id, replies=0)
            except Exception as e:
                return print(e)

            try:
                gel = await gel.copy(chat_id=user_id, protect_content=FILE_PROTECTED)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                gel = await gel.copy(chat_id=user_id, protect_content=FILE_PROTECTED)
            except Exception as e:
                return print(e)

            await yardimMesaji(str(files.file_name), gel)
            temp.today_sent_bytes += int(files.file_size)

            await asyncio.sleep(5)
            await git.delete()
        except UserIsBlocked:
            await query.answer('Beni engellemişsin. Önce engelimi kaldır.', show_alert=True)

        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{myusername}?start={file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{myusername}?start={file_id}")
    elif query.data.startswith("pages"):
        try:
            sayi = query.data.split('#')[1]
        except Exception:
            sayi = 0
        await query.answer(f'Toplam {sayi} sonuç bulduk kıymetlim')
    elif query.data == "start":
        await query.message.edit_text(text=START_TXT.format(query.message.from_user.mention if query.message.from_user else query.message.chat.title, myusername, temp.MY_NAME), reply_markup = ikm(
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
    ), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    elif query.data == "stats":
        buttons = [[ikb('◀️ Geri', callback_data='about'), ikb('♻️ Yenile', callback_data='stats'), ikb('❌ Kapat', callback_data='kapat')]]

        reply_markup = ikm(buttons)
        total = await Media.count_documents()
        
        
        currentTime = ReadableTime(time.time() - botStartTime)
        os_omru = ReadableTime(time.time() - psutil.boot_time())
        totald, used, freeg = shutil.disk_usage('.')
        totald = get_size(totald)
        used = get_size(used)
        freeg = get_size(freeg)
        sent = get_size(psutil.net_io_counters().bytes_sent)
        recv = get_size(psutil.net_io_counters().bytes_recv)
        cpuUsage = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        gond = temp.today_sent_bytes
        gond = get_size(gond)
        stats = f"@{myusername} 💚 Bot Sürümü: {bot_version}\n\nDosya: `{total}`\nBot Ömrü: `{currentTime}`\nİS Ömrü: `{os_omru}`\n\nTotal Disk: `{totald}`\n- Kullanılan: `{used}`\n- Boşta: `{freeg}`\n\nAğ Yükleme: `{sent}`\nAğ İndirme: `{recv}`\nGiden Dosya: `{gond}`\n\nCPU: `%{cpuUsage}` RAM: `%{memory}` DISK: `%{disk}`\n\nKorPiracy tarafından sunulan KitapBot'un ücretsiz bir klonudur.\nKendi klonunuzu yaratmak için mesaj atın: @{CREATOR_USERNAME}"

        await query.message.edit_text(text=stats, reply_markup=reply_markup)

async def auto_filter(client, msg: Message):
    if msg.text.startswith(("/", "#")): return # ignore commands
    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", msg.text):
        return
    if not 2 < len(msg.text) < 100:
        return
    search = msg.text
    ubc = await db.get_button_count(msg.from_user.id)
    files, offset, total_results = await get_search_results(search, max_results=ubc,offset=0, filtr=True)
    if not files:
        delo = await msg.reply_text("Bulamadık bir şey kıymetlim?\nArama ipuçlarını öğrendinis mi?: /yardim")
        await asyncio.sleep(11)
        return await delo.delete()
    btn = [
        [
            ikb(text=f"{get_size(file.file_size)} {file.file_name}", callback_data=f'files#{file.file_id}')
        ]
        for file in files
    ]
    pagecount = math.ceil(total_results/ubc)
    req = msg.from_user.id if msg.from_user else 0
    if offset != "" and pagecount != 1:
        key = f"{msg.chat.id}-{msg.id}"
        BUTTONS[key] = search
        btn.append(
            [
                ikb(text=f"🗓 1 / {pagecount}", callback_data=f"pages#{total_results}"),
                ikb(text="▶️", callback_data=f"next_{req}_{key}_{offset}"),
                ikb('ℹ️', callback_data='info#first'),
                ikb('❌', callback_data=f'kapat#{req}')
            ]
        )
    else:
        btn.append(
            [
                ikb(text=f"🗓 1 / {pagecount}", callback_data=f"pages#{total_results}"),
                ikb('ℹ️', callback_data='info#one'),
                ikb('⚙️', callback_data=f'settings#{req}'),
                ikb('❌', callback_data=f'kapat#{req}')
            ]
        )
    toko = f"Arama Terimi: `{search}`" \
        f"\nSonuç Sayısı: `{total_results}`" \
        f"\nSayfa Sayısı: `{pagecount}`" \
        f"\nHer Sayfadaki Buton: `{ubc}`" \
        "\n\nİpucu: Bana özelden /start yazın, ayarlara gidin." \
        "\nButon sayısını ve diğer ayarlarınızı özelleştirebilirsiniz."
    await msg.reply_text(toko, reply_markup=ikm(btn))

