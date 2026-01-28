# Property of Kor.PiracyTeam - GNU General Public License v2.0

import io
from pyrogram import filters, Client
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from database.filters_mdb import (
    add_filter,
    get_filters,
    delete_filter,
    count_filters
)
from database.connections_mdb import active_connection
from helpers.unicode_tr_case import unicode_tr
from utils import get_file_id, parser, split_quotes
from info import ADMINS

# Get logging configurations
from info import LOG

@Client.on_message(filters.command(['filter', 'add']) & filters.incoming)
async def addfilter(client:Client, message:Message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply_text(f"Anonim yöneticisin. Bana özelden `/baglan {message.chat.id}` yazarak bu gruba bağlanabilir, ayarları yönetebilirsin.")
    chat_type = message.chat.type
    args = message.text.html.split(None, 1)
    grpid=None
    if chat_type == ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is None:
            return await message.reply_text("Bağlı değilim ki? Grupta `/baglan` yaz da bağlanayım.", quote=True)
        grp_id = grpid
        try:
            chat = await client.get_chat(grpid)
            title = chat.title
        except Exception:
            return await message.reply_text("Grupta olduğuma emin misin?", quote=True)
    elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else: return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != ChatMemberStatus.ADMINISTRATOR
            and st.status != ChatMemberStatus.OWNER
            and int(userid) not in ADMINS
    ):
        return

    if len(args) < 2:
        return await message.reply_text("Ne yazdın anlamadım. Örnek: `/filter esenlikler size de esenlikler`", quote=True)
    extracted = split_quotes(args[1])
    text = unicode_tr(extracted[0]).lower()

    if not message.reply_to_message and len(extracted) < 2:
        return await message.reply_text("Add some content to save your filter!", quote=True)

    if (len(extracted) >= 2) and not message.reply_to_message:
        reply_text, btn, alert = parser(extracted[1], text)
        fileid = None
        if not reply_text:
            return await message.reply_text("Butonları yazısız mı yaratayım? Yazı ver onlara çabuk.", quote=True)

    elif message.reply_to_message and message.reply_to_message.reply_markup:
        try:
            rm = message.reply_to_message.reply_markup
            btn = rm.inline_keyboard
            msg = get_file_id(message.reply_to_message)
            if msg:
                fileid = msg.file_id
                reply_text = message.reply_to_message.caption.html
            else:
                reply_text = message.reply_to_message.text.html
                fileid = None
            alert = None
        except Exception:
            reply_text = ""
            btn = "[]"
            fileid = None
            alert = None

    elif message.reply_to_message and message.reply_to_message.media:
        try:
            msg = get_file_id(message.reply_to_message)
            fileid = msg.file_id if msg else None
            reply_text, btn, alert = parser(message.reply_to_message.caption.html, text)
        except Exception:
            reply_text = ""
            btn = "[]"
            alert = None
    elif message.reply_to_message and message.reply_to_message.text:
        try:
            fileid = None
            reply_text, btn, alert = parser(message.reply_to_message.text.html, text)
        except Exception:
            reply_text = ""
            btn = "[]"
            alert = None
    else: return

    await add_filter(grp_id, text, reply_text, btn, fileid, alert)

    await message.reply_text(
        f"**{title}** için `{text}` filtresi eklendi.",
        quote=True
    )

@Client.on_message(filters.command(['viewfilters', 'filters']) & filters.incoming)
async def get_all(client: Client, message: Message):
    chat_type = message.chat.type
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply_text(f"Anonim yöneticisin. Bana özelden `/baglan {message.chat.id}` yazarak bu gruba bağlanabilir, ayarları yönetebilirsin.")

    if chat_type == ChatType.PRIVATE:
        userid = message.from_user.id
        grpid = await active_connection(str(userid))
        if grpid is None:
            return await message.reply_text("Bağlı değilim ki? Grupta `/baglan` yaz da bağlanayım.", quote=True)

        grp_id = grpid
        try:
            chat = await client.get_chat(grpid)
            title = chat.title
        except Exception:
            return await message.reply_text("Grupta olduğuma emin misin?", quote=True)
    elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title
    else:
        LOG.error(str(chat_type))
        return LOG.error("zortçettayp")
    st = await client.get_chat_member(grp_id, userid)
    if st.status != ChatMemberStatus.ADMINISTRATOR and st.status != ChatMemberStatus.OWNER and int(userid) not in ADMINS:
        return LOG.error("not admin")
    texts = await get_filters(grp_id)
    count = await count_filters(grp_id)
    if count:
        filterlist = f"**{title}** grubundaki toplam filtre: {count}\n\n"
        for text in texts:
            keywords = f" ×  `{text}`\n"
            filterlist += keywords
        if len(filterlist) > 1024:
            with io.BytesIO(str.encode(filterlist.replace("`", ""))) as keyword_file:
                keyword_file.name = "filtreler.txt"
                await message.reply_document(document=keyword_file, quote=True)
            return
    else:
        filterlist = f"**{title}** grubunda hiç filtre yok."
    await message.reply_text(text=filterlist, quote=True)

@Client.on_message(filters.command('del') & filters.incoming)
async def deletefilter(client:Client, message:Message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply_text(f"Anonim yöneticisin. Bana özelden `/baglan {message.chat.id}` yazarak bu gruba bağlanabilir, ayarları yönetebilirsin.")
    chat_type = message.chat.type

    if chat_type == ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except Exception:
                return await message.reply_text("Grupta olduğuma emin misin?", quote=True)
        else:
            await message.reply_text("Bağlı değilim ki? Grupta `/baglan` yaz da bağlanayım.", quote=True)

    elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else: return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != ChatMemberStatus.ADMINISTRATOR
            and st.status != ChatMemberStatus.OWNER
            and int(userid) not in ADMINS
    ):
        return LOG.error("not admin")

    try: cmd, text = message.text.split(" ", 1)
    except Exception:
        return await message.reply_text(
            "Silmek istediğin filtreyi şu şekilde belirt: `/del filtreismi`"
            "\n\nTüm filtreleri görmek için tıkla: /viewfilters",
            quote=True
        )

    query = unicode_tr(text).lower()
    await delete_filter(message, query, grp_id)

@Client.on_message(filters.command('delall') & filters.incoming)
async def delallconfirm(client: Client, message: Message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply_text(f"Anonim yöneticisin. Bana özelden `/baglan {message.chat.id}` yazarak bu gruba bağlanabilir, ayarları yönetebilirsin.")

    chat_type = message.chat.type
    if chat_type == ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is None:
            return await message.reply_text("Bağlı değilim ki? Grupta `/baglan` yaz da bağlanayım.", quote=True)

        grp_id = grpid
        try:
            chat = await client.get_chat(grpid)
            title = chat.title
        except Exception:
            return await message.reply_text("Grupta olduğuma emin misin?", quote=True)
    elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title
    else:
        return
    st = await client.get_chat_member(grp_id, userid)
    if st.status == ChatMemberStatus.OWNER or int(userid) in ADMINS:
        await message.reply_text(f"'{title}' grubundaki tüm filtreleri siliyom emin misin?", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="EVET", callback_data="delallconfirm")], [InlineKeyboardButton(text="HAYIR", callback_data="delallcancel")]]), quote=True)
