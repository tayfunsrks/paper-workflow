# Property of Kor.PiracyTeam - GNU General Public License v2.0

import asyncio
from pyrogram.errors import MessageNotModified, FloodWait
from pyrogram.types import Message, InlineKeyboardButton as ikb, InlineKeyboardMarkup as ikm
from pyrogram.enums import MessageEntityType, ChatType
from database.users_chats_db import db
from info import ADMINS
from utils import temp

# Get logging configurations
from info import LOG

async def Settings(message: Message):
    if message.chat.type != ChatType.PRIVATE:
        bm = [
            [
                ikb('◀️ Geri', callback_data='start'),
                ikb('🦄 Özele Gel', url=f"https://t.me/{temp.MY_USERNAME}?start=settings"),
                ikb('❌ Kapat', callback_data='kapat'),
            ]
        ]
        await message.edit_text(
            "Kişisel ayarlarınıs kıymetlim?" \
            "\nBana özelden /ayarlar yasın.." \
            "\nAlttaki butondan da gelebilirsiniss"
            "\nAcele et kıymetli silicem bu mesajı",
            reply_markup=ikm(bm))
        await asyncio.sleep(15)
        return await message.delete()
    user_id = message.chat.id
    if message.entities:
        if message.entities[0].type is MessageEntityType.BOT_COMMAND:
            message = await message.reply_text('Bekle aptal hobbitss',
                reply_to_message_id=message.id)
    user_data = await db.get_user_data(user_id)
    if not user_data:
        return await message.edit_text("Alamadık ayarlarınısı kıymetlim? Yöneticiye bi sor")
    get_notif = user_data.get("notif", False)
    get_bc = user_data.get("button_count", 10)
    buttons_markup = [
        [
            ikb('🔔 Bildirimler Açık' if get_notif else '🔕 Bildirimler Kapalı', callback_data="notifon"),
            ikb(f'🌈 Buton Sayısı: {str(get_bc)}', callback_data="buttoncount")
        ],
        [
            ikb('◀️ Geri', callback_data='start'),
            ikb('❌ Kapat', callback_data='kapat')
        ]
    ]

    if user_id in ADMINS:
        a = [
            [
            ikb(f"👮‍♂ Yardım", callback_data="help"),
            ikb(f"🍒 Ana Sayfa", callback_data="start")
            ]
        ]
        buttons_markup.extend(a)
    try:
        tox = "⚙ Bot Ayarlarınıs Kıymetlimiss\n" \
            "\n🍒 İstediğinis gibi ayarlayın korkmayın. Bu ayarlar size özel." \
            "\n🍄 Buton sayıları çıkacak sonuçlar için kıymetli. Dene ve gör." \
            "\n🍉 Bildirimler sahibimden mesajlar için. İstemiyorsan kapat." \
            "\n🥕 Ayar şu anda ne yazıyorsa odur. Kapalı yazıyorsa kapalıdır."
        await message.edit_text(
            text=tox,
            reply_markup=ikm(buttons_markup),
            disable_web_page_preview=True
        )
    except MessageNotModified: pass
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.edit_text(
            text=tox,
            reply_markup=ikm(buttons_markup),
            disable_web_page_preview=True
        )
    except Exception as err:
        LOG.exception(err)
