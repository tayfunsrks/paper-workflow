# Property of Kor.PiracyTeam - GNU General Public License v2.0

import contextlib
from pyrogram import Client
from pyrogram.errors import UserNotParticipant
from info import AUTH_CHANNEL, AUTH_USERS, LOG_CHANNEL, LOGIN_MODE, LOGIN_WARNING
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from typing import Union
import re
from typing import List
from pyrogram.types import InlineKeyboardButton as ikb

# Get logging configurations
from info import LOG

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)

class temp(object):
    mainapp:Client = None

    BANNED_USERS = []
    BANNED_CHATS = []
    LOGGED_IN_USERS = []

    MY_USERNAME = None # username
    MY_NAME = None
    MY_ID = None

    INDEX_FROM = 1
    CANCEL = False

    info_bot_str = ""
    last_welcome:Message = None
    join_chnl_msg:Message = None
    today_sent_bytes=0

    start_btns = None # coming from bot start

    kapat_btn = [[ikb(text="❌ Kapat", callback_data="kapat")]]

    ADMIN_HELP = """Help: <b>BOT HELP FOR ADMIN</b>

Help: <b>Manual Filter</b>
- Filter is the feature were users can set automated replies for a particular keyword and KitapMaria will respond whenever a keyword is found the message
<b>NOTE:</b>
1. eva maria should have admin privillage.
2. only admins can add filters in a chat.
3. alert buttons have a limit of 64 characters.
<b>Commands and Usage:</b>
• /filter - <code>add a filter in chat</code>
• /filters - <code>list all the filters of a chat</code>
• /del - <code>delete a specific filter in chat</code>
• /delall - <code>delete the whole filters in a chat (chat owner only)</code>
• /delusers - <code>delete the whole users (chat owner only)</code>
• /delgroups - <code>delete the whole groups (chat owner only)</code>

Help: <b>Buttons</b>
- Eva Maria Supports both url and alert inline buttons.
<b>NOTE:</b>
1. Telegram will not allows you to send buttons without any content, so content is mandatory.
2. Eva Maria supports buttons with any telegram media type.
3. Buttons should be properly parsed as markdown format
<b>URL buttons:</b>
<code>[Button Text](buttonurl:https://t.me/KitapMariaBot)</code>
<b>Alert buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>

Help: <b>Auto Filter</b>
<b>NOTE:</b>
1. Make me the admin of your channel if it's private.
2. make sure that your channel does not contains camrips, porn and fake files.
3. Forward the last message to me with quotes.
 I'll add all the files in that channel to my db.
 
 Help: <b>Connections</b>
- Used to connect bot to PM for managing filters 
- it helps to avoid spamming in groups.
<b>NOTE:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to ur PM
<b>Commands and Usage:</b>
• /connect  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>

<b>Commands and Usage:</b>
• /log - <code>to get the rescent errors</code>
• /sil - <code>to delete a specific file from db.</code>
• /users - <code>to get list of my users and ids.</code>
• /skip - <code>set index from id.</code>
• /chats - <code>to get list of the my chats and ids </code>
• /leave  - <code>to leave from a chat.</code>
• /disable  -  <code>do disable a chat.</code>
• /ban  - <code>to ban a user.</code>
• /unban  - <code>to unban a user.</code>
• /channel - <code>to get list of total connected channels</code>
• /yay - <code>to broadcast a message to all users</code>
• /deleteallfiles - <code>delete all saved files from database</code>
• /deleteallusers - <code>delete all saved users from database</code>
• /deleteallgroups - <code>delete all saved groups from database</code>
• /wayback - <code>wayback any link</code>
• /virustotal - <code>virustotal for files and md5 sha1 etc.</code>
• /hash - <code>file hasher: md5, sha1, sha256 etc.</code>
• /json - <code>reply a message to print json</code>
• /ping - <code>simple ping to bot</code>
"""

async def is_subscribed(bot: Client, query):
    if not AUTH_CHANNEL or query.from_user.id in AUTH_USERS:
        return True
    try:
        user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        return False
    except Exception as e:
        LOG.exception(e)
        await bot.send_message(LOG_CHANNEL, f"is_subscribed hatası: {str(e)} True döndürüldü.")
        return True
    else:
        if user.status != ChatMemberStatus.BANNED:
            return True
    return False

async def is_logged_in(message):
    if not LOGIN_MODE or message.from_user.id in AUTH_USERS:
        return True
    elif message.from_user.id in temp.LOGGED_IN_USERS:
        return True
    else:
        if LOGIN_WARNING and type(message) == Message:
            await message.reply_text('Giriş yapmalısın.\nDiyelim ki parola 1234. Bana şunu yazacaksın: `/giris 1234`')
        return False

def get_size(size):
    """Get size in readable format"""

    units = ["b", "k", "m", "g", "t", "p", "e"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.0f%s" % (size, units[i])

def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_file_id(msg: Message):
    if msg.media:
        for message_type in ("photo", "animation", "audio", "document", "video", "video_note", "voice", "sticker"):
            if obj := getattr(msg, message_type):
                setattr(obj, "message_type", message_type)
                return obj

def extract_user(message: Message) -> Union[int, str]:
    """extracts the user from a message"""
    user_id = None
    user_first_name = None
    # https://github.com/SpEcHiDe/PyroGramBot/blob/f30e2cca12002121bad1982f68cd0ff9814ce027/pyrobot/helper_functions/extract_user.py#L7
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name
    elif len(message.command) > 1:
        if len(message.entities) > 1 and message.entities[1].type == "text_mention":
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            user_first_name = user_id
        with contextlib.suppress(ValueError):
            user_id = int(user_id)
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return user_id, user_first_name

def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1  # ignore first char -> is some kind of quote
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    # 1 to avoid starting quote, and counter is exclusive so avoids ending
    key = remove_escapes(text[1:counter].strip())
    # index will be in range, or `else` would have been executed and returned
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))

def parser(text, keyword):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                # create a thruple with button label, url, and newline status
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(ikb(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    ))
                else:
                    buttons.append([ikb(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(ikb(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([ikb(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])

        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        return note_data, buttons, alerts
    except Exception:
        return note_data, buttons, None

def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res
