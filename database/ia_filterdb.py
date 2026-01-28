# Property of Kor.PiracyTeam - GNU General Public License v2.0

from struct import pack
import re, base64
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from helpers.temizleyici import cleanhtml, clear_caption, clear_filename, sonsuz_sil
from info import DATABASE_URI, DATABASE_NAME, COLLECTION_NAME, DEF_BUTTON_COUNT, LOG_NEW_FILES, NO_SAVE_FULLNAME, NO_SAVE_SUFFIX, USE_CAPTION_FILTER

# Get logging configurations
from info import LOG

try:
    client = AsyncIOMotorClient(DATABASE_URI)
except Exception as e:
    LOG.error(e)

db = client[DATABASE_NAME]
instance = Instance.from_db(db)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME

async def get_clone(query: str, file_size, file_type):
    """Find really duplicated files with file_name and file_size"""
    # https://www.mongodb.com/docs/manual/reference/operator/#AdvancedQueries-$in
    if not query:
        raw_pattern = '.'
    elif ' ' in query:
        raw_pattern = query.replace(' ', '.*[\s\.\+\-_]')
    else:
        raw_pattern = '(\b|[\.\+\-_]|[ığüşöçİĞÜŞÖÇ]?)' + query + '(\b|[\.\+\-_]|[ığüşöçİĞÜŞÖÇ]?)'

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except Exception as e:
        LOG.exception(f"{str(e)} {query}")
        return None
    filt = {'$and': [{'file_name': regex}, {'file_size': file_size}, {'file_type': file_type}]}

    cursor = Media.find(filt)
    files = await cursor.to_list(length=1)
    return None if len(files) == 0 else files[0]

async def save_file(media, forceReplace=False):
    """Save file in database"""
    if media.file_name:
        saf_filename = str(media.file_name)
    elif media.caption:
        saf_filename = str(media.caption)
    else:
        saf_filename = 'ismi ve açıklaması olmayan dosya'
    # vta kaydedilecek dosya adı
    file_name = re.sub("(\s|_|\-|\.|\)|\(|\[|\]|\+|\{|\})", " ", saf_filename)
    file_name = sonsuz_sil(file_name, '  ', ' ')
    file_name = file_name.strip()
    # saçma sapan dosyalar +
    if (NO_SAVE_FULLNAME and saf_filename in NO_SAVE_FULLNAME) or (NO_SAVE_SUFFIX and saf_filename.endswith(tuple(NO_SAVE_SUFFIX))):
        if LOG_NEW_FILES:
            LOG.info(f"Es Geçildi: {saf_filename}")
        return 'esgec'
    # aynı dosya adı ve boyut 15.05.2022 zorgof
    klon = await get_clone(file_name, media.file_size, media.file_type)
    if klon:
        medcap = media.caption.html if media.caption else ''
        kloncap = klon.caption or ''
        # vt klonun açıklaması gelenden büyük - eşitse
        if (not forceReplace) and (len(kloncap) >= len(medcap)):
            if LOG_NEW_FILES:
                LOG.warning(f'VTda daha iyi: "{file_name}" vt c: {len(kloncap)} gelen c: {len(medcap)}')

            return 'klonadboyut'
        else:
            # vt klon kötüyse sil
            if LOG_NEW_FILES:
                if forceReplace:
                    # forceReplace admin kanaldan editlediyse
                    LOG.info(f'Yönetici düzenledi: "{file_name}" vt c: {len(kloncap)} gelen c: {len(medcap)}')

                else:
                    LOG.info(f'VTdaki değiştirildi: "{file_name}" vt c: {len(kloncap)} gelen c: {len(medcap)}')

            result = await Media.collection.delete_one({'_id': klon.file_id})
            if not result.deleted_count:
                result = await Media.collection.delete_one({'file_name': klon.file_name, 'file_size': klon.file_size, 'mime_type': klon.mime_type})

            if not result.deleted_count and LOG_NEW_FILES:
                LOG.error('Dosyayı tam silecekken yok oldu.')
    file_id, file_ref = unpack_new_file_id(media.file_id)
    try:
        file = Media(file_id=file_id, file_ref=file_ref, file_name=file_name, file_size=media.file_size, file_type=media.file_type, mime_type=media.mime_type, caption=media.caption.html if media.caption else None)

    except ValidationError as e:
        LOG.exception(e)
        return 'validerr'
    except Exception as y:
        LOG.exception(y)
        return 'allerr'
    else:
        try:
            await file.commit()
        except DuplicateKeyError:
            if LOG_NEW_FILES:
                LOG.warning(f'Klon file-id: "{file_name}"')
            return 'klonid'
        else:
            if LOG_NEW_FILES and not forceReplace and not klon:
                LOG.info(f'Yeni dosya kaydı: "{file_name}"')
            return 'saved'

async def clear_filelist(filelist): # genel temizleyici
    for file in filelist:
        if str(file.file_name).lower() == 'none' or not str(file.caption):
            file.file_name = str(file.caption)
        if str(file.caption).lower() == 'none' or not str(file.caption):
            file.caption = str(file.file_name)
        file.caption = cleanhtml(file.caption)
        file.caption = clear_caption(str(file.caption))
        file.file_name = clear_filename(file.file_name)
    return filelist

async def get_search_results(query, file_type=None, max_results=DEF_BUTTON_COUNT, offset=0, filtr=False):
    """For given query return (results, next_offset)"""

    query = sonsuz_sil(query, '  ', ' ') # tek boşluğa indir
    query = query.strip()
    # if filter:
    # better ?
    # query = query.replace(' ', r'(\s|\.|\+|\-|_)')
    # raw_pattern = r'(\s|_|\-|\.|\+)' + query + r'(\s|_|\-|\.|\+)'
    if not query:
        raw_pattern = '.'
    elif ' ' in query:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')
    else:
        raw_pattern = r'(\b|[\.\+\-_]|[ığüşöçİĞÜŞÖÇ]?)' + query + r'(\b|[\.\+\-_]|[ığüşöçİĞÜŞÖÇ]?)'
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except Exception as e:
        LOG.exception(f"{str(e)} {query}")
        return [], ''

    if USE_CAPTION_FILTER:
        filtr = {'$or': [{'file_name': regex}, {'caption': regex}]}
    else:
        filtr = {'file_name': regex}

    if file_type:
        filtr['file_type'] = file_type

    total_results = await Media.count_documents(filtr)
    next_offset = offset + max_results

    if next_offset > total_results:
        next_offset = ''

    cursor = Media.find(filtr)
    # Sort by recent
    cursor.sort('$natural', -1)
    # Slice files according to offset and max results
    cursor.skip(offset).limit(max_results)
    # Get list of files
    files = await cursor.to_list(length=max_results)
    files = await clear_filelist(files) # temizle
    return files, next_offset, total_results

async def get_file_details(query):
    filtr = {'file_id': query}
    cursor = Media.find(filtr)
    filedetails = await cursor.to_list(length=1)
    filedetails = await clear_filelist(filedetails) # temizle
    return filedetails

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
