# Property of Kor.PiracyTeam - GNU General Public License v2.0

import asyncio
import math
import re
import ast
import time
import psutil
import shutil
from pyrogram.types import Message
from helpers.settings import Settings
from helpers.timeformat import ReadableTime
from helpers.unicode_tr_case import unicode_tr
from helpers.yardimMesajlari import yardimMesaji
from info import BUTTON_COUNT_ENHANCER, DEF_BUTTON_COUNT, MAX_BUTTON_COUNT as mbc, \
    FILE_PROTECTED, MIN_BUTTON_COUNT, SAF_INLINE, START_TXT, botStartTime, ABOUT_TXT, AUTH_CHANNEL
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from info import ADMINS, AUTH_CHANNEL, CUSTOM_CAPTION, bot_version
from pyrogram.types import InlineKeyboardMarkup as ikm, InlineKeyboardButton as ikb, CallbackQuery
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatType
from pyrogram.errors import UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_logged_in, is_subscribed, temp
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import(
   del_all,
   find_filter,
   get_filters,
)

# Get logging configurations
from info import LOG

BUTTONS = {}
SPELL_CHECK = {}

@Client.on_message(~filters.channel & ~filters.command(['giris', 'login']) & filters.text & filters.incoming)
async def give_filter(client:Client, message:Message):
    if message.from_user.id in temp.BANNED_USERS: return
    if message.chat.id in temp.BANNED_CHATS:
        k = await client.send_message(
            chat_id=message.chat.id,
            text='Bu sohbeti sahibim yasaklamış. Elveda.'
        )
        try: await k.pin()
        except Exception: pass
        return await client.leave_chat(message.chat.id)
    await db.add_user(message.from_user.id, message.from_user.first_name)
    if not await is_subscribed(client, message):
        return
    elif not await is_logged_in(message):
        return
    k = await manual_filters(client, message)
    if SAF_INLINE:
        return LOG.info('saf inline modu açık. butonlar çıkmayacak. manuel filtreler çalışır.')
    if not k:
        await auto_filter(client, message)

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(client, query: CallbackQuery):
    if query.from_user.id in temp.BANNED_USERS: return
    elif not await is_subscribed(client, query): return
    ident, req, key, offset = query.data.split("_")
    # arama sayfalarını kimler değiştirebilir?
    user_id = query.from_user.id
    if not int(req) in [user_id, 0] and not user_id in ADMINS:
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
    try:
        await query.edit_message_reply_markup(reply_markup=ikm(btn))
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    if user_id in temp.BANNED_USERS: return
    elif not await is_subscribed(client, query): return
    await db.add_user(user_id, query.from_user.first_name)
    if query.data.startswith('kapat'):
        try:
            uid = query.data.split('#')[1]
            if not int(uid) in [user_id, 0] and not user_id in ADMINS:
                await query.answer("Sisin olmayan şeysleri kapatamasssınıss kıymetli", show_alert=True)
            else:
                await query.message.delete()
        except Exception:
            await query.message.delete()
    elif query.data.startswith('info'):
        uid = query.data.split('#')[1]
        if uid == 'first':
            to = '🐼 Hoş geldin, Şu an ilk sayfadasın.' \
                '\n🦜 Sonraki sayfalar için sağ butonuna tıkla.' \
                '\n🌴 Kapatmak için çarpıya tıkla.' \
                '\n🍍 Kendi ayarların için bana /ayarlar yaz.'
            await query.answer(to, show_alert=True)
        elif uid == 'last':
            to = '🐼 Şu an son sayfadasın.' \
                '\n🦜 Önceki sayfalar için sol butonuna tıkla.' \
                '\n🌴 Kapatmak için çarpıya tıkla.' \
                '\n🍍 Kendi ayarların için bana /ayarlar yaz.'
            await query.answer(to, show_alert=True)
        elif uid == 'one':
            to = '🐼 Tek sayfa sonuç çıktı.' \
                '\n🌴 Kapatmak için çarpıya tıkla.' \
                '\n🍍 Kendi ayarların için bana /ayarlar yaz.'
            await query.answer(to, show_alert=True)
    elif query.data.startswith('settings'):
        uid = query.data.split('#')[1]
        if not int(uid) in [user_id, 0] and not user_id in ADMINS:
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
            tore = "Sahibim bu ayarı herkese kilitlemiş, değiştiremezsin :(" \
                f"\nHerkese: {DEF_BUTTON_COUNT} olarak ayarlanmış."
            return await query.answer(tore, show_alert=True)
        fromdb = await db.get_button_count(user_id)
        if fromdb >= mbc:
            await db.set_button_count(user_id, MIN_BUTTON_COUNT)
        else:
            await db.set_button_count(user_id, int(fromdb) + BUTTON_COUNT_ENHANCER)
        fromdb = await db.get_button_count(user_id)
        await query.answer(f"Buton sayınız artık {str(fromdb)}")
        await Settings(query.message)
    elif query.data.startswith('ban'):
        try: uid = query.data.split('#')[1]
        except Exception as e: return LOG.exception(e)
        ban = bool(await client.ban_chat_member(AUTH_CHANNEL, uid))
        if ban:
            await query.answer("Üye Yasaklandı.")
            keyboard = ikm([
                [
                ikb("🍀 Yasağı Kaldır", callback_data=f'unban#{uid}'),
                ikb('❌ Kapat', callback_data='kapat')
                ]
            ])
            await query.message.edit_reply_markup(keyboard)
        else:
            await query.answer("Yasaklama Başarısız")
            keyboard = ikm([
                [
                ikb("🔥 Yasakla", callback_data=f'ban#{uid}'),
                ikb('❌ Kapat', callback_data='kapat')
                ]
            ])
            await query.message.edit_reply_markup(keyboard)
    elif query.data.startswith('unban'):
        try: uid = query.data.split('#')[1]
        except Exception as e: return LOG.exception(e)
        unban = bool(await client.unban_chat_member(AUTH_CHANNEL, uid))
        if unban:
            await query.answer("Yasak Kaldırıldı.")
            keyboard = ikm([
                [
                ikb("🔥 Yasakla", callback_data=f'ban#{uid}'),
                ikb('❌ Kapat', callback_data='kapat')
                ]
            ])
            await query.message.edit_reply_markup(keyboard)
        else:
            await query.answer("Yasak Kaldırma Başarısız")
            keyboard = ikm([
                [
                ikb("🍀 Yasağı Kaldır", callback_data=f'unban#{uid}'),
                ikb('❌ Kapat', callback_data='kapat')
                ]
            ])
            await query.message.edit_reply_markup(keyboard)
    elif query.data == "about":
        await query.answer("Kıymetlimis hakkısında")
        buttons= [
            [
                ikb('◀️ Geri', callback_data='start'),
                ikb('🔮 İstatistikler', callback_data='stats'),
                ikb('❌ Kapat', callback_data='kapat')
            ]
        ]
        reply_markup = ikm(buttons)
        await query.message.edit_text(
            text=ABOUT_TXT.format(temp.MY_NAME),
            reply_markup=reply_markup
        )
    elif query.data == "delallconfirm":
        chat_type = query.message.chat.type

        if chat_type == "private":
            grpid = await active_connection(str(user_id))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except Exception:
                    return await query.message.edit_text("Grupta olduğuma emin misin?", quote=True)
            else:
                return await query.message.edit_text(
                    "Bağlı değilim ki? Grupta `/baglan` yaz da bağlanayım.\nCheck /connections or connect to any groups",
                    quote=True
                )

        elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return

        st = await client.get_chat_member(grp_id, user_id)
        if (st.status == "creator") or (int(user_id) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("Bu işlem için grup yöneticisi olman gerek",show_alert=True)

    elif query.data == "delallcancel":
        chat_type = query.message.chat.type

        if chat_type == "private":
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, user_id)
            if (st.status == "creator") or (int(user_id) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except Exception:
                    pass
            else:
                await query.answer("Seni ilgilendirmeyen şeylere tıklama. Meraklı melahat.", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = ikm([
            [
                ikb(f"{stat}", callback_data=f"{cb}:{group_id}"),
                ikb("Sil", callback_data=f"deletecb:{group_id}")
            ],
            [
                ikb("Geri", callback_data="backcb")
            ]
        ])

        await query.message.edit_text(
            f"Grup: **{title}**\nGrup ID: `{group_id}`",
            reply_markup=keyboard
        )
        return

    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**"
            )
        else:
            await query.message.edit_text('Some error occured!!')
        return

    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**"
            )
        else:
            return await query.message.edit_text("Azıcık hata oluştu.")
    elif "deletecb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            return await query.message.edit_text(
                f"Some error occured!!"
            )
    elif query.data == "backcb":
        await query.answer()

        groupids = await all_connections(str(user_id))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(user_id), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        ikb(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except Exception:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=ikm(buttons)
            )

    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert,show_alert=True)

    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer("Bulamadık bir şey kıymetlim?\nArama ipuçlarını öğrendinis mi?: /yardim")
        files = files_[0]
        f_caption = files.caption
        f_caption += '' if (CUSTOM_CAPTION is None) or (len(f_caption) > 1024) else f'\n{CUSTOM_CAPTION}'
        try:
            if not await is_subscribed(client, query):
                return await query.answer(url=f"https://t.me/{temp.MY_USERNAME}?start={file_id}")
            else:
                ho = await client.send_cached_media(
                    chat_id=user_id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=FILE_PROTECTED
                )
                # yardim
                await yardimMesaji(str(files.file_name), ho)
                temp.today_sent_bytes += int(files.file_size)
                await query.answer('Özelden sana gönderdim',show_alert = False)
        except UserIsBlocked:
            await query.answer('Beni engellemişsin. Önce engelimi kaldır.',show_alert = True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.MY_USERNAME}?start={file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.MY_USERNAME}?start={file_id}")
    elif query.data.startswith("pages"):
        try: sayi = query.data.split('#')[1]
        except Exception: sayi = 0
        await query.answer(f'Toplam {sayi} sonuç bulduk kıymetlim')
    elif query.data == "start":
        await query.message.edit_text(
            text=START_TXT.format(
                query.message.from_user.mention if query.message.from_user \
                else query.message.chat.title, temp.MY_USERNAME, temp.MY_NAME
            ),
            reply_markup=ikm(temp.start_btns),
            parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )
    elif query.data == "help":
        buttons = [[
            ikb('◀️ Geri', callback_data='settings#0'),
            ikb(f"🍒 Ana Sayfa", callback_data="start"),
            ikb('❌ Kapat', callback_data='kapat')
        ]]
        reply_markup = ikm(buttons)
        await query.message.edit_text(
            text=temp.ADMIN_HELP,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            ikb('◀️ Geri', callback_data='about'),
            ikb('♻️ Yenile', callback_data='stats'),
            ikb('❌ Kapat', callback_data='kapat')
        ]]
        reply_markup = ikm(buttons)
        total = await Media.count_documents()
        users = "2"
        chats = "1"
        if (int(user_id) in ADMINS):
            users = await db.total_users_count() # sadece admine görünsün.
            chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
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
        stats = f"@{temp.MY_USERNAME} 💚 Bot Sürümü: {bot_version}\n\n" \
            f"Dosya: `{total}`\n" \
            f"Kullanıcı: `{users}`\n" \
            f"Sohbet: `{chats}`\n\n" \
            f"Dolu VT: `{monsize}`\n" \
            f"Boş VT: `{free}`\n\n" \
            f'Bot Ömrü: `{currentTime}`\n' \
            f'İS Ömrü: `{os_omru}`\n\n' \
            f'Total Disk: `{totald}`\n' \
            f'- Kullanılan: `{used}`\n' \
            f'- Boşta: `{freeg}`\n\n' \
            f'Ağ Yükleme: `{sent}`\n' \
            f'Ağ İndirme: `{recv}`\n' \
            f'Giden Dosya: `{gond}`\n\n' \
            f'CPU: `%{cpuUsage}` RAM: `%{memory}` DISK: `%{disk}`'
        await query.message.edit_text(
            text=stats,
            reply_markup=reply_markup
        )

async def auto_filter(client, msg: Message):
    if msg.text.startswith(("/", "#")): return # ignore commands
    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", msg.text):
        return
    if 2 < len(msg.text) < 100:
        search = msg.text
        ubc = await db.get_button_count(msg.from_user.id)
        files, offset, total_results = await get_search_results(search, max_results=ubc,offset=0, filtr=True)
        if not files:
            delo = await msg.reply_text("Bulamadık bir şey kıymetlim?\nArama ipuçlarını öğrendinis mi?: /yardim")
            await asyncio.sleep(11)
            return await delo.delete()
    else: return
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

async def manual_filters(client:Client, message:Message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True)
                        else:
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=ikm(eval(btn)),
                                reply_to_message_id = reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id = reply_id,
                            protect_content=FILE_PROTECTED
                        )
                    else:
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=ikm(eval(btn)),
                            reply_to_message_id = reply_id
                        )
                except Exception as e:
                    LOG.exception(e)
                break
    else:
        return False
