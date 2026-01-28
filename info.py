# Property of Kor.PiracyTeam - GNU General Public License v2.0

import contextlib
import datetime
import re, os, time, requests
import shutil
import pytz
from os import environ
from dotenv import load_dotenv
from pyrogram import __version__

bot_version = 'v2.1.0.1 Alfa'
botStartTime = time.time()

# Get logging configurations
import logging
LOG = logging.getLogger(__name__)

# türkiye zamanı logger +

class Formatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""
    def converter(self, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        tzinfo = pytz.timezone('Europe/Istanbul')
        return tzinfo.localize(dt)
        
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec='milliseconds')
            except TypeError:
                s = dt.isoformat()
        return s

logging.basicConfig(
     level=logging.INFO, 
     format='[%(asctime)s] %(module)s:%(funcName)-s:%(lineno)d %(levelname)-s %(message)s',
     datefmt='%H:%M:%S',
)
console = logging.FileHandler('log.log.txt', 'w', 'utf-8')
cons_formatter = Formatter(
    '[%(asctime)s] %(module)s:%(funcName)-5s:%(lineno)d %(levelname)-5s %(message)s',
    datefmt='%H:%M:%S'
    )
console.setFormatter(cons_formatter)
LOG.addHandler(console)

# türkiye zamanı logger -

def is_enabled(value: str):
    return value.lower() in {"true", "1", "e", "d"}

def get_config_from_url(configurl: str):
    try:
        if os.path.isfile('config.env'):
            with contextlib.suppress(Exception):
                os.remove('config.env')
        if ' ' in configurl:
            LOG.info("Detected gitlab snippet url. Example: 26265 sdg6-626-g6256")
            snipid, apikey = configurl.split(maxsplit=1)
            main_api = f"https://gitlab.com/api/v4/snippets/{snipid}/raw"
            headers = {'content-type': 'application/json', 'PRIVATE-TOKEN': apikey}
            res = requests.get(main_api, headers=headers)
        else:
            res = requests.get(configurl)
        if res.status_code == 200:
            LOG.info("Config uzaktan alındı. Status 200.")
            with open('config.env', 'wb+') as f:
                f.write(res.content)
            load_dotenv('config.env', override=True)
        else:
            LOG.error(f"Failed to download config.env {res.status_code}")
    except Exception as e:
        LOG.exception(f"CONFIG_FILE_URL: {e}")

LOGO_LINK = str(environ.get('LOGO_LINK', 'https://telegra.ph/file/375b69b135524990cb7ca.jpg'))
# about kısmındaki foto linki / dosyaların gönderileceği thumbnail.
THUMB_FILE = None

def get_thumbnail():
    global THUMB_FILE
    try:
        if len(LOGO_LINK) == 0:
            raise Exception
        if os.path.isfile('kucukresim.jpg'):
            with contextlib.suppress(Exception):
                os.remove('kucukresim.jpg')
        res = requests.get(LOGO_LINK, stream=True)
        if res.status_code == 200:
            LOG.info("Küçük resim uzaktan alındı. Status 200.")
            with open('kucukresim.jpg', 'wb+') as f:
                shutil.copyfileobj(res.raw, f)
            THUMB_FILE = 'kucukresim.jpg'
        else:
            LOG.error(f"Failed to download kucukresim.jpg {res.status_code}")
            THUMB_FILE = None
    except Exception as e:
        THUMB_FILE = None
        LOG.exception(e)

if os.path.exists('config.env'): load_dotenv('config.env')
# load heroku from heroku
HEROKU_APP_NAME = str(environ.get("HEROKU_APP_NAME", None))
LOG.info(f"HEROKU_APP_NAME: {str(HEROKU_APP_NAME)}")
# heroku şeyleri için app name, herokuya ekleyin giste değil.
HEROKU_API_KEY = str(environ.get("HEROKU_API_KEY", None))
LOG.info(f"HEROKU_API_KEY: {str(HEROKU_API_KEY)}")
# heroku şeyleri için api, herokuya ekleyin giste değil.
CONFIG_FILE_URL = os.environ.get('CONFIG_FILE_URL', None)
if CONFIG_FILE_URL: get_config_from_url(CONFIG_FILE_URL)
else: LOG.error("Lokal config.env kullanılacak")
get_thumbnail()

id_pattern = re.compile(r'^.\d+$')

LOG.info("--- CONFIGS STARTS HERE ---")

# Bot information
# rastgele string: ''.join(random.choices(string.digits, k=1)
SESSION = environ.get('SESSION', 'PiracyTeamMaria')
LOG.info(f"SESSION: {str(SESSION)}")
try: API_ID = int(environ['API_ID'])
except Exception:
    LOG.info('Galiba config yapmadın. CONFIG_FILE_URL bunu doldur gel.')
    exit(1)
API_HASH = environ['API_HASH']
BOT_TOKEN = environ['BOT_TOKEN']

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = is_enabled(environ.get('USE_CAPTION_FILTER', "true"))
LOG.info(f"USE_CAPTION_FILTER: {str(USE_CAPTION_FILTER)}".encode(
    'UTF-8', errors='replace')
)
BROADCAST_AS_COPY = is_enabled(environ.get("BROADCAST_AS_COPY", "true"))
LOG.info(f"BROADCAST_AS_COPY: {str(BROADCAST_AS_COPY)}")

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) \
    else admin for admin in environ.get('ADMINS', '').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) \
    else ch for ch in environ.get('CHANNELS', '0').split()]
auth_users = [int(user) if id_pattern.search(user) \
    else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL')
AUTH_CHANNEL = int(auth_channel) \
    if auth_channel and id_pattern.search(auth_channel) \
    else None
    
auth_grp = environ.get('AUTH_GROUP')
SINGLE_BUTTON = is_enabled(environ.get("SINGLE_BUTTON", "false"))
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
# düzeltilecek. şimdilik çalışmıyor.
DATABASE_URI = environ.get('DATABASE_URI', "")
# db url.
DATABASE_NAME = environ.get('DATABASE_NAME', "Cluster0")
# db ismi. db oluştururken Cluster0 diye bıraktıysan elleme.
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'dosyalar')
# db koleksiyon ismi. hiç elleme sorun çıkmaz.
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', 0))
# kendi kullanıcı idnizi verin geçin.

MAX_BUTTON_COUNT = int(environ.get('MAX_BUTTON_COUNT', 30))
LOG.info(f"MAX_BUTTON_COUNT: {str(MAX_BUTTON_COUNT)}")
# kullanıcıların ayarlayabileceği max buton sayısı.
MIN_BUTTON_COUNT = int(environ.get('MIN_BUTTON_COUNT', 5))
LOG.info(f"MIN_BUTTON_COUNT: {str(MIN_BUTTON_COUNT)}")
# kullanıcıların ayarlayabileceği min buton sayısı.
DEF_BUTTON_COUNT = int(environ.get('DEF_BUTTON_COUNT', 10))
LOG.info(f"DEF_BUTTON_COUNT: {str(DEF_BUTTON_COUNT)}")
# öntanımlı buton sayısı. yeni kullanıcılara bu atanacak.
BUTTON_COUNT_ENHANCER = int(environ.get('BUTTON_COUNT_ENHANCER', 5))
LOG.info(f"BUTTON_COUNT_ENHANCER: {str(BUTTON_COUNT_ENHANCER)}")
# her tıklamaya buton sayısı kaç artsın? 0: herkese DEF_BUTTON_COUNT geçerli olsun.

FILENAME_SPLITTER = str(environ.get('FILENAME_SPLITTER', '.'))
if len(FILENAME_SPLITTER) == 0: FILENAME_SPLITTER = '.'
LOG.info(f"FILENAME_SPLITTER: {FILENAME_SPLITTER}")
# sonuçlar için dosya adı ayracı: atsız.ruh.adam.pdf / atsız-ruh-adam-pdf / atsız ruh adam pdf
SUPPORT_CHAT = str(environ.get('SUPPORT_CHAT', ''))
if len(SUPPORT_CHAT) == 0: SUPPORT_CHAT = None
LOG.info(f"SUPPORT_CHAT: {bool(SUPPORT_CHAT)}")
# destek chati. başında @ olmadan girin.
CUSTOM_CAPTION = str(environ.get("CUSTOM_CAPTION", ""))
if len(CUSTOM_CAPTION) == 0: CUSTOM_CAPTION = None
LOG.info(f"CUSTOM_CAPTION: {bool(CUSTOM_CAPTION)}")
# dosyanın altında ne yazsın ?
VIRUSTOTAL_API = str(environ.get("VIRUSTOTAL_API", ""))
if len(VIRUSTOTAL_API) == 0: VIRUSTOTAL_API = None
LOG.info(f"VIRUSTOTAL_API: {bool(VIRUSTOTAL_API)}")
# virustotal
VIRUSTOTAL_FREE = is_enabled(environ.get("VIRUSTOTAL_FREE", "true"))
LOG.info(f"VIRUSTOTAL_FREE: {str(VIRUSTOTAL_FREE)}")
# false: virustotal premium
SEND_WITH_BUTTONS = is_enabled(environ.get("SEND_WITH_BUTTONS", "false"))
LOG.info(f"SEND_WITH_BUTTONS: {str(SEND_WITH_BUTTONS)}")
# True: dosyayı butonlarla gönderir
FILE_PROTECTED = is_enabled(environ.get("FILE_PROTECTED", "false"))
LOG.info(f"FILE_PROTECTED: {str(FILE_PROTECTED)}")
# True: dosyayı iletilemez yapar
JOIN_CHANNEL_WARNING = is_enabled(environ.get("JOIN_CHANNEL_WARNING", "true"))
LOG.info(f"JOIN_CHANNEL_WARNING: {str(JOIN_CHANNEL_WARNING)}")
# False: kanalda olmayanlara çalışmaz, True: Kanala katıl diye uyarı verir.
HELP_MESSAGES_AFTER_FILE = is_enabled(environ.get("HELP_MESSAGES_AFTER_FILE", "true"))
LOG.info(f"HELP_MESSAGES_AFTER_FILE: {str(HELP_MESSAGES_AFTER_FILE)}")
# dosya göndedikten sonra yardım mesajları gönderir.
WELCOME_NEW_GROUP_MEMBERS = is_enabled(environ.get("WELCOME_NEW_GROUP_MEMBERS", "true"))
LOG.info(f"WELCOME_NEW_GROUP_MEMBERS: {str(WELCOME_NEW_GROUP_MEMBERS)}")
# gruba gelenleri selamlar
WELCOME_SELF_JOINED = is_enabled(environ.get("WELCOME_SELF_JOINED", "true"))
LOG.info(f"WELCOME_SELF_JOINED: {str(WELCOME_SELF_JOINED)}")
# biri botu gruba ekleyince eklediğin için tşk mesajı.
CLEAN_WELCOME = is_enabled(environ.get("CLEAN_WELCOME", "true"))
LOG.info(f"CLEAN_WELCOME: {str(CLEAN_WELCOME)}")
# grupta en altta tek bir hg mesajı olur
CAPTION_SPLITTER = environ.get("CAPTION_SPLITTER", ' 🔥 ')
LOG.info(f"CAPTION_SPLITTER: {str(CAPTION_SPLITTER)}".encode(
    'UTF-8', errors='replace')
)
# ben bunu kullanıyorum: ' 🔥 ' sebep: daha fazla caption gözüksün. istersen: '\n'
SHARE_BUTTON_TEXT = environ.get('SHARE_BUTTON_TEXT', 'Denemeni öneririm: {username}')
# dosya altındaki paylaş butonu...
REQUEST_LINK = is_enabled(environ.get("REQUEST_LINK", "true"))
LOG.info(f"REQUEST_LINK: {str(REQUEST_LINK)}")
# linki istek katılma isteği olarak oluşturur.
YOU_JOINED = is_enabled(environ.get("YOU_JOINED", "true"))
LOG.info(f"YOU_JOINED: {str(YOU_JOINED)}")
# kanala katıldın beni kullanabilirsin mesajı
AUTO_APPROVE = is_enabled(environ.get("AUTO_APPROVE", "false"))
LOG.info(f"AUTO_APPROVE: {str(AUTO_APPROVE)}")
# katılma isteklerini otomatik onayla
NO_SERVICE = is_enabled(environ.get("NO_SERVICE", "false"))
LOG.info(f"NO_SERVICE: {str(NO_SERVICE)}")
# anti service  messages
SAF_INLINE = is_enabled(environ.get("SAF_INLINE", "false"))
LOG.info(f"SAF_INLINE: {str(SAF_INLINE)}")
# true: sadece inline modu, butonları kapatır
DISABLE_INLINE = is_enabled(environ.get("DISABLE_INLINE", "false"))
LOG.info(f"DISABLE_INLINE: {str(DISABLE_INLINE)}")
# true: inline ı kapatır
DISABLE_FILE_SAVE = is_enabled(environ.get("DISABLE_FILE_SAVE", "false"))
LOG.info(f"DISABLE_FILE_SAVE: {str(DISABLE_FILE_SAVE)}")
# true: kanala atılanları vt'a kaydetME false: oto kaydet
YOU_BANNED_MSG = is_enabled(environ.get("YOU_BANNED_MSG", "true"))
LOG.info(f"YOU_BANNED_MSG: {str(YOU_BANNED_MSG)}")
# true: banlı kişilere banlanmışın diye bas bas bağırır, false: ölü gibi davranır
BAN_QUITERS = is_enabled(environ.get("BAN_QUITERS", "false"))
LOG.info(f"BAN_QUITERS: {str(BAN_QUITERS)}")
# auth kanalınızdan çıkanlar bir daha giremez, dolayısı ile botu da kullanamaz
LOG_JOINERS = is_enabled(environ.get("LOG_JOINERS", "true"))
LOG.info(f"LOG_JOINERS: {str(LOG_JOINERS)}")
# auth kanalınıza katılanları loglar
LOG_QUITERS = is_enabled(environ.get("LOG_QUITERS", "true"))
LOG.info(f"LOG_QUITERS: {str(LOG_QUITERS)}")
# auth kanalınızdan ayrılanları loglar
LOG_NEW_FILES = is_enabled(environ.get("LOG_NEW_FILES", "true"))
LOG.info(f"LOG_NEW_FILES: {str(LOG_NEW_FILES)}")
# dosya kaydedildi / zaten var mesajlarını loglara yazdırır
GEN_CHAT_LINK_DELAY = int(environ.get('GEN_CHAT_LINK_DELAY', 10))
LOG.info(f"GEN_CHAT_LINK_DELAY: {str(GEN_CHAT_LINK_DELAY)}")
# çet içinlink oluşturmadan önce beklenecek süre. dakika cinsinden.
WELCOME_TEXT = environ.get('WELCOME_TEXT', 'Esenlikler {}. Hoş Geldin Sefa Geldin.')
# link vb. girilebilir.
FINISHED_PROGRESS_STR = os.environ.get('FINISHED_PROGRESS_STR','🇹🇷') # ● ■ gibi
UN_FINISHED_PROGRESS_STR = os.environ.get('UN_FINISHED_PROGRESS_STR','🏴‍☠️') # ○ □ gibi
PROGRESSBAR_LENGTH = int(os.environ.get('PROGRESSBAR_LENGTH', 10))
# progresbar ayarları
INDEXER_MAX = int(environ.get('INDEXER_MAX', 1000))
LOG.info(f"INDEXER_MAX: {str(INDEXER_MAX)}")
# /index kaç sonuç çıkarsın max?
DISABLE_INDEXER = is_enabled(environ.get("DISABLE_INDEXER", "false"))
LOG.info(f"DISABLE_INDEXER: {str(DISABLE_INDEXER)}")
# true: sadece adminler kullanabilir, false: üyeler de kullanabilir
NO_SAVE_SUFFIX = [ext for ext in environ.get('NO_SAVE_SUFFIX', ".url .apk .lnk .htm .html .doc .docx .xls .xlsx").split(' ')]
if len(NO_SAVE_SUFFIX) == 0: NO_SAVE_SUFFIX = None
LOG.info(f"NO_SAVE_SUFFIX: {str(', '.join(NO_SAVE_SUFFIX))}")
# vta kaydedilmeyecek suffixler. örnek: .url .apk .lnk .htm aralara boşluk koyarak girin.
NO_SAVE_FULLNAME = [ext for ext in environ.get('NO_SAVE_FULLNAME', "metadata.opf").split(' ')]
if len(NO_SAVE_FULLNAME) == 0: NO_SAVE_FULLNAME = None
LOG.info(f"NO_SAVE_FULLNAME: {str(', '.join(NO_SAVE_FULLNAME))}")
# vta kaydedilmeyecek tam dosya adları.
CREATOR_USERNAME = os.environ.get('CREATOR_USERNAME','') # başına @ koyma
if len(CREATOR_USERNAME) == 0: CREATOR_USERNAME = None
LOG.info(f"CREATOR_USERNAME: {CREATOR_USERNAME}")
# bot yaratıcısının kullanıcı adı. bot banlansa da size tekrar yazabilir böylece kullanıcılar.
LOGIN_MODE = is_enabled(environ.get("LOGIN_MODE", "false"))
LOG.info(f"LOGIN_MODE: {str(LOGIN_MODE)}")
# /login parola ile girişi açar. öntanımlı: false
LOGIN_PASSWORD = [lo for lo in environ.get('LOGIN_PASSWORD', "pasaport,şifre,ikincişifre,boşluklu örnek şifre").split(',')]
LOG.info(f"LOGIN_PASSWORD: {str(LOGIN_PASSWORD)}")
# /login parolası
LOGIN_WARNING = is_enabled(environ.get("LOGIN_WARNING", "true"))
LOG.info(f"LOGIN_WARNING: {str(LOGIN_WARNING)}")
# kullanmadan önce giriş yapın uyarısı
TEMP_CHANNEL = environ.get("TEMP_CHANNEL", "0")
LOG.info(f"TEMP_CHANNEL: {str(bool(TEMP_CHANNEL))}")
# dosya gönderici temp channel

defstarttxt = """Esenlikler {}, ben <a href=https://t.me/{}>{}</a>.
Bana özelden yaz. /start yazsan yeterli.
Arama terimini bana yaz. Örneğin şengör yaz gönder bana.
Yapamadın mı? Diğelerine bakarak kopya çek.

🔥 Boşluklarla aratsan daha iyi olur:
Örnek: "nihalatsız ruh-adam.pdf" gibi yazma.
Şöyle yaz: "nihal atsız ruh adam"
Şöyle yaz: "ruh adam pdf"
Nokta tire gibi şeyler yerine boşluk koyuyoruz.

🔥 Ne kadar az şey yazarsan o kadar çok sonuç çıkar:
Örnek: "celal şengör dahi diktatör" gibi yazma.
Şöyle yaz: "dahi diktatör"
Şöyle yaz: "dahi diktatör epub"

🔥 Eğer Türkçe terimler çalışmazsa Türkçe karakterleri çıkar:
Örnek: "celal şengör dahi diktatör" gibi yazma.
Şöyle yaz: "celal sengor dahi diktator"

🔥 Büyük ve küçük karakterler sonuçları değiştiriyor:
Şöyle dene: "Osmanlı", Şöyle dene: "OSMANLI"
Şöyle dene: "BELGELERİ", Şöyle dene: "Belgeleri"
Şimdilik bu sorun var. Çözebilecek olan varsa ulaşsın.
"""
LINK_FOR_EVERYTHING = str(environ.get('LINK_FOR_EVERYTHING', ''))
# tüm ayrıntılrınızı içeren birlink varsa buraya girin.
START_TXT = environ.get('START_TXT', defstarttxt)
# 3 tane yer tutucu bırakın. örneğin: "selam {} ben {} {}"
if CREATOR_USERNAME:
    START_TXT += f"\n🔥 Bu bot tamamen ücretsiz bir klondur.\nKendi klonunu yaratmak için: @{CREATOR_USERNAME}\n"
if not len(LINK_FOR_EVERYTHING) == 0:
    START_TXT += f"\n🔥 Oku: {LINK_FOR_EVERYTHING}"

defabout = f"[🔥]({LOGO_LINK})" + " {}" + \
    "\n\nİçine gollum kaçmış indexleme botu." \
    "\nAnonim kişiler tarafından geliştirildikss." + \
    "\nTakıl buralarda kıymetli üzümü ye bağını sorma." + \
    f"\nBu bot tamamen ücretsiz bir klondur.\nKendi klonunu yaratmak için: @{CREATOR_USERNAME}" + \
    "\n\n💜 Copyright © **𝐾𝑜𝑟𝑃𝑖𝑟𝑎𝑐𝑦𝑇𝑒𝑎𝑚**" + \
    f"\n💚 Bot Sürümü: {bot_version}"
ABOUT_TXT = environ.get('ABOUT_TXT', defabout)
# bir tane yer tutucu bırakın. botun adı gelecek. örneğin: "bu basit bir hakkında metnidir ve bot adı {} dir."

LOG.info("--- CONFIGS ENDS HERE ---")
