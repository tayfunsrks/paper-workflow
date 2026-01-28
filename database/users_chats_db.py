# Property of Kor.PiracyTeam - GNU General Public License v2.0

# https://github.com/odysseusmax/animated-lamp/blob/master/bot/database/database.py
import datetime
import motor.motor_asyncio
from info import BUTTON_COUNT_ENHANCER, DATABASE_NAME, DATABASE_URI, DEF_BUTTON_COUNT, SINGLE_BUTTON, FILE_PROTECTED

# Get logging configurations
from info import LOG

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups

    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            join_date=datetime.date.today().isoformat(),
            notif=True,
            ban_status=dict(
                is_banned=False,
                ban_reason=""
            )
        )

    def new_group(self, id, title):
        return dict(
            id=id,
            title=title,
            chat_status=dict(
                is_disabled=False,
                reason=""
            )
        )
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)

    async def add_user(self, id, name):
        if await db.is_user_exist(id): return
        user = self.new_user(id, name)
        await self.col.insert_one(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})

    async def ban_user(self, user_id, ban_reason="Sebepsiz"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id': int(id)})
        return user.get('ban_status', default) if user else default

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats

    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id': int(chat)})
        return chat.get('chat_status') if chat else False

    async def add_chat(self, chat, title):
        if await db.get_chat(chat): return
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)

    async def re_enable_chat(self, id):
        chat_status = dict(
            is_disabled=False,
            reason=""
        )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})

    async def get_settings(self, id):
        default = {'button': SINGLE_BUTTON, 'file_secure': FILE_PROTECTED}
        chat = await self.grp.find_one({'id': int(id)})
        return chat.get('settings', default) if chat else default

    async def disable_chat(self, chat, reason="Sebepsiz"):
        chat_status = dict(
            is_disabled=True,
            reason=reason
        )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})

    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count

    async def get_all_chats(self):
        return self.grp.find({})

    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']

    async def set_notif(self, id, notif):
        await self.col.update_one({"id": id}, {"$set": {"notif": notif}})

    async def set_button_count(self, id, bc):
        await self.col.update_one({"id": id}, {"$set": {"button_count": bc}})

    async def get_button_count(self, id):
        if BUTTON_COUNT_ENHANCER == 0:
            return DEF_BUTTON_COUNT
        user = await self.col.find_one({"id": int(id)})
        return user.get("button_count", DEF_BUTTON_COUNT) if user else DEF_BUTTON_COUNT

    async def set_login(self, id):
        await self.col.update_one({"id": id}, {"$set": {"logged_in": True}})

    async def get_login(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("logged_in", False) if user else False
    
    async def get_logged_in_users(self):
        users = self.col.find({'logged_in': True})
        return [user['id'] async for user in users]

    async def get_notif(self, id):
        user = await self.col.find_one({"id": int(id)})
        return user.get("notif", False)

    async def get_all_notif_user(self):
        return self.col.find({"notif": True})

    async def total_notif_users_count(self):
        count = await self.col.count_documents({"notif": True})
        return count

    async def get_user_data(self, id) -> dict:
        user = await self.col.find_one({'id': int(id)})
        return user or None
try:
    db = Database(DATABASE_URI, DATABASE_NAME)
except Exception as e:
    LOG.error(e)
