import asyncio
import contextlib
import random
import string
from pyrogram import Client
from info import API_HASH, API_ID, LOG
import os
from database.connections_mdb import mydb
slaves = mydb['slaves']

async def testClient(bottoken):
    """durum kodu, hata mesajı, bot username"""
    cli = Client(name="deneme", api_id=API_ID, api_hash=API_HASH, bot_token=bottoken, no_updates=True)
    try:
        await cli.start()
        print(cli.me.username)
        await cli.stop()
        with contextlib.suppress(Exception):
            os.remove('deneme.session')
        return 200, None, cli.me.username
    except Exception as e:
        with contextlib.suppress(Exception):
            os.remove('deneme.session')
        return 400, e, None

def add_slave(token, uname):
    token = str(token)
    LOG.info(f"trying to add: {token} {uname}")
    # veri
    data = {
        'id': token,
        'uname': uname
    }
    try:
        sonuc = slaves.update_one(data, {"$set": data}, upsert=True)
        print(sonuc.raw_result)
    except Exception as e: LOG.exception(f'error add_slave {e}', exc_info=True)

def del_slave(token):
    token = str(token)
    LOG.info(f"trying to del: {token}")
    silmeterimi = {'uname': token.lstrip('@')} if token.startswith('@') else {'id': token}
    try:
        sonuc = slaves.delete_one(silmeterimi)
        print(sonuc.raw_result)
    except Exception as e: LOG.exception(f'error add_chat {e}', exc_info=True)

def get_slaves():
    return slaves.find({}), slaves.count_documents({})

def delete_sessions():
    liste = os.listdir('.')
    for a in liste:
        if not a.endswith('.session'): continue
        with contextlib.suppress(Exception):
            os.remove(a)