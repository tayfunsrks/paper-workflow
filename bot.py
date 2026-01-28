# Property of Kor.PiracyTeam - GNU General Public License v2.0

from helpers.guncelTarih import guncelTarih
from platform import python_version
from pyrogram import Client, __version__, compose
import pkg_resources, asyncio
from pyrogram.raw.all import layer
from helpers.koleler import del_slave, delete_sessions, get_slaves, testClient
from info import ADMINS, SESSION, API_ID, API_HASH, BOT_TOKEN, bot_version, LOG
from utils import temp
from pyrogram.types import InlineKeyboardButton as ikb, InlineKeyboardMarkup as ikm
from database.users_chats_db import db
from database.ia_filterdb import Media

def get_package_versions(file='requirements.txt'):
    diger = f"Python: {python_version()} - Pyrogram: {__version__} - Layer: {layer}\nBot Sürümü: {bot_version}"
    toret = []
    with open(file, 'r') as file1:
        lines = file1.readlines()
    for line in lines:
        try:
            v = pkg_resources.get_distribution(line.strip()).version
        except Exception as e:
            LOG.exception(e)
            continue
        toret.append(f"{line.strip()}=={v}")
    return f'\n{diger}\n\nPython Paketleri:\n\n' + '\n'.join(toret) + '\n'

class Bot(Client):

    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats
        temp.LOGGED_IN_USERS = await db.get_logged_in_users()
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.MY_ID = me.id
        temp.MY_USERNAME = me.username
        temp.MY_NAME = me.first_name
        # set group button
        temp.start_btns = [
            [
                ikb('➕ Gruba ekle', url=f'http://t.me/{me.username}?startgroup=true'),
                ikb('🔍 Ara', switch_inline_query_current_chat='')
            ],
            [
                ikb('😈 Hakkında', callback_data='about'),
                ikb('😊 Ayarlar', callback_data='settings#0')
            ]
        ]
        self.username = f'@{me.username}'
        temp.info_bot_str = f"{me.username} ({me.id}) {get_package_versions()}"
        LOG.info(f"Started: {temp.info_bot_str}")
        if len(ADMINS) != 0:
            try: await self.send_message(
                text=f"✅ Doğdum @{me.username} (`{me.id}`) \
                    \n\nTarih: {guncelTarih()}{get_package_versions()} \
                    \nTıkla: /start - /log",
                chat_id=ADMINS[0], reply_markup=ikm(temp.kapat_btn))
            except Exception: LOG.warning("Bota start yaz düzgün doğamadım")

    async def stop(self, *args):
        if len(ADMINS) != 0:
            try: await self.send_message(
                text=f"❌ Öldüm @{temp.MY_USERNAME} (`{temp.MY_ID}`) \
                    \n\nTarih: {guncelTarih()} {get_package_versions()}",
                chat_id=ADMINS[0], reply_markup=ikm(temp.kapat_btn))
            except Exception: LOG.warning("Bota start düzgün yaz ölemedim")
        await super().stop()
        LOG.info(f"Stopped: {temp.info_bot_str}")

# sadece master
# app = Bot()
# app.run()

async def main():
    delete_sessions()
    temp.mainapp = Bot()
    koleler = [temp.mainapp]
    SLAVE_BOTS, count = get_slaves()
    if count != 0: LOG.info(f"{count} adet köle bot bulundu. kontrol ediliyor.")
    else: LOG.info("Köle bot yok. Sadece efendi bot modunda çalışıyor.")

    for tek in SLAVE_BOTS:
        key, mes, kuladi = await testClient(tek["id"])
        if key == 200:
            LOG.info(f"{kuladi} kölesi algılandı.")
        else:
            LOG.error(mes)
            del_slave(tek["id"])
            LOG.info(f"{kuladi} kölesi VTdan silindi.")
    
    SLAVE_BOTS, count = get_slaves()
    koleler.extend(
        Client(
            name=f"kolebot{say}",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=a['id'],
            plugins={"root": "kole"}
        ) for say, a in enumerate(SLAVE_BOTS, start=1)
    )

    await compose(koleler)


# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# loop.run_until_complete(main())

asyncio.run(main())
