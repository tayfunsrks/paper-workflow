# Property of Kor.PiracyTeam - GNU General Public License v2.0

import contextlib
from pyrogram import filters, Client
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from database.connections_mdb import add_connection, all_connections, if_active, delete_connection
from info import ADMINS

# Get logging configurations
from info import LOG

@Client.on_message((filters.private | filters.group) & filters.command(['connect', 'bağlan', 'baglan']))
async def addconnection(client: Client, message: Message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply_text(f"Anonim yöneticisin. Bana özelden `/baglan {message.chat.id}` yazarak bu gruba bağlanabilir, ayarları yönetebilirsin.")

    chat_type = message.chat.type
    if chat_type == ChatType.PRIVATE:
        try:
            cmd, group_id = message.text.split(" ", 1)
        except Exception:
            return await message.reply_text("Şu şekilde yaz: `/baglan grupidsi`\n\nGrup id'ni bilmiyorsan beni grubuna ekle ve `/id` yaz.", quote=True)

    elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        group_id = message.chat.id
    try:
        st = await client.get_chat_member(group_id, userid)
        if st.status != ChatMemberStatus.ADMINISTRATOR and st.status != ChatMemberStatus.OWNER and int(userid) not in ADMINS:
            await message.reply_text("Bağlanmak için o grupta yönetici olmalısın.", quote=True)

            return
    except Exception as e:
        LOG.exception(e)
        return await message.reply_text("Geçersiz grup id'si. Eğer gerçekten geçerliyse orada olduğuma emin ol.", quote=True)

    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == ChatMemberStatus.ADMINISTRATOR:
            ttl = await client.get_chat(group_id)
            title = ttl.title
            addcon = await add_connection(str(group_id), str(userid))
            if addcon:
                await message.reply_text(f"**{title}** grubuna başarıyla bağlandım.\nŞimdi grubunu buradan yönetebilirsin.", quote=True)

                if chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                    await client.send_message(userid, f"**{title}** grubuna bağlandım.")
            else:
                await message.reply_text("Zaten bu gruba bağlıyım.", quote=True)
        else:
            await message.reply_text("Beni grupta yönetici yapmalısın.", quote=True)
    except Exception as e:
        LOG.exception(e)
        await message.reply_text('Hata. Daha sonra deneyin.', quote=True)

@Client.on_message((filters.private | filters.group) & filters.command('disconnect', 'ayrıl', 'ayril'))
async def deleteconnection(client:Client, message:Message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply_text(f"Anonim yöneticisin. Bana özelden `/baglan {message.chat.id}` yazarak bu gruba bağlanabilir, ayarları yönetebilirsin.")
    chat_type = message.chat.type

    if chat_type == ChatType.PRIVATE:
        await message.reply_text("Bağlı grupları görmek için tıkla: /connections", quote=True)

    elif chat_type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, userid)
        if (
                st.status != ChatMemberStatus.ADMINISTRATOR
                and st.status != ChatMemberStatus.OWNER
                and int(userid) not in ADMINS
        ):
            return

        delcon = await delete_connection(str(userid), str(group_id))
        if delcon:
            await message.reply_text("Bahsettiğin gruptan bağımı kopardım. Şimdilik.", quote=True)
        else:
            await message.reply_text("Bağlı değilim ki? Grupta `/baglan` yaz da bağlanayım.", quote=True)

@Client.on_message(filters.private & filters.command(["connections", "bağlar", "baglar"]))
async def connections(client:Client, message:Message):
    userid = message.from_user.id

    groupids = await all_connections(str(userid))
    if groupids is None:
        await message.reply_text(
            "Şu anda tam olarak sıfır adet gruba bağlıyım. Bir yerlere bağla beni hemen!",
            quote=True
        )
        return
    buttons = []
    for groupid in groupids:
        with contextlib.suppress(Exception):
            ttl = await client.get_chat(int(groupid))
            title = ttl.title
            active = await if_active(str(userid), str(groupid))
            act = " - ACTIVE" if active else ""
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                    )
                ]
            )
    if buttons:
        await message.reply_text(
            "Bağlanan grubun detayları:\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply_text(
            "Hiç aktif bağlantım yok. Grupta `/baglan` yaz da bağlanayım.",
            quote=True
        )
