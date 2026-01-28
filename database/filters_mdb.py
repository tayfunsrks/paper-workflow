# Property of Kor.PiracyTeam - GNU General Public License v2.0

import contextlib
import pymongo
from helpers.guncelTarih import guncelTarih
from database.ia_filterdb import Media
from info import DATABASE_URI, DATABASE_NAME
from pyrogram.types import Message
try:
    myclient = pymongo.MongoClient(DATABASE_URI)
except Exception as e:
    LOG.error(e)
mydb = myclient[DATABASE_NAME]

# Get logging configurations
from info import LOG

async def add_filter(grp_id, text, reply_text, btn, file, alert):
    mycol = mydb[str(grp_id)]
    # mycol.create_index([('text', 'text')])
    data = {
        'text': str(text),
        'reply': str(reply_text),
        'btn': str(btn),
        'file': str(file),
        'alert': str(alert)
    }
    try:
        mycol.update_one({'text': str(text)}, {"$set": data}, upsert=True)
    except Exception:
        LOG.exception('Some error occured!', exc_info=True)

async def find_filter(group_id, name):
    mycol = mydb[str(group_id)]
    query = mycol.find({"text": name})
    # query = mycol.find( { "$text": {"$search": name}})
    try:
        for file in query:
            reply_text = file['reply']
            btn = file['btn']
            fileid = file['file']
            try:
                alert = file['alert']
            except Exception:
                alert = None
        return reply_text, btn, alert, fileid
    except Exception:
        return None, None, None, None

async def get_filters(group_id):
    mycol = mydb[str(group_id)]
    texts = []
    query = mycol.find()
    with contextlib.suppress(Exception):
        texts.extend(file['text'] for file in query)
    return texts

async def delete_filter(message, text, group_id):
    mycol = mydb[str(group_id)]
    myquery = {'text': text}
    query = mycol.count_documents(myquery)
    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`' filtresi silindi. Artık bu filtreye cevap vermeyeceğim.",
            quote=True
        )
    else:
        await message.reply_text("Öyle bir filtre bulamadım.", quote=True)

async def del_all(message, group_id, title):
    if str(group_id) not in mydb.list_collection_names():
        return await message.edit_text(f"{title}'da silinecek filtre yok.")
    mycol = mydb[str(group_id)]
    try:
        mycol.drop()
        await message.edit_text(f"Tüm {title} filtreleri silindi.")
    except Exception as e:
        await message.edit_text(f"Tüm filtreleri silerken hata oluştu\n{str(e)}")

async def delete_all_users(message:Message):
    try:
        mydb['users'].drop()
        await message.edit_text(f"Tüm kullanıcılar silindi.\n{guncelTarih()}")
    except Exception as e:
        await message.edit_text(f"Tüm kullanıcıları silerken hata oluştu\n{str(e)}")

async def delete_all_groups(message:Message):
    try:
        mydb['groups'].drop()
        await message.edit_text(f"Tüm gruplar silindi.\n{guncelTarih()}")
    except Exception as e:
        await message.edit_text(f"Tüm grupları silerken hata oluştu\n{str(e)}")

async def delete_all_files(message:Message):
    try:
        await Media.collection.drop()
        await message.edit_text(f"Tüm dosyalar silindi.\n{guncelTarih()}")
    except Exception as e:
        await message.edit_text(f"Tüm dosyaları silerken hata oluştu\n{str(e)}")

async def count_filters(group_id):
    mycol = mydb[str(group_id)]
    count = mycol.count_documents({})
    return False if count == 0 else count

async def filter_stats():
    collections = mydb.list_collection_names()
    if "CONNECTION" in collections:
        collections.remove("CONNECTION")
    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        count = mycol.count_documents({})
        totalcount += count
    totalcollections = len(collections)
    return totalcollections, totalcount
