# Property of Kor.PiracyTeam - GNU General Public License v2.0

import re
from helpers.unicode_tr_case import unicode_tr

# Get logging configurations
from info import CUSTOM_CAPTION, FILENAME_SPLITTER, LOG

def cleanhtml(raw_html):
    if raw_html is None: return raw_html
    try:
        CLEANR = re.compile('<.*?>')
        return re.sub(CLEANR, '', raw_html)
    except Exception:
        return raw_html

def sonsuz_sil(text:str, old:str, new:str):
    if text is None: return text
    try:
        temp = text
        while old in temp:
            temp = temp.replace(old, new)
        return sonsuz_sil(temp, '  ', ' ') # boşlukları teke düşür
    except Exception:
        return text

def clear_caption(abo:str):
    # herkes bilirse boku çıkar :D
    abo = abo.replace("Powered with <3 by @auto forwarder bot", '')
    abo = abo.replace("Powered with <3 by @auto_forwarder_bot", '')
    abo = abo.replace("@auto forwarder bot", '')
    abo = abo.replace("@auto_forwarder_bot", '')
    abo = abo.replace("@BabillKutuphanesi", "")
    abo = sonsuz_sil(abo, 'dosyasını sizinle paylaşıyorum', '')
    o = """--
ReadEra ile kitap okuma
https://play.google.com/store/apps/details?id=org.readera&hl=tr"""
    abo = sonsuz_sil(abo, o, '')
    o = """--
ReadEra ile kitap okuma
https://play.google.com/store/apps/details?id=org.readera"""
    abo = sonsuz_sil(abo, o, '')
    o = """ReadEra ile kitap okuma
https://play.google.com/store/apps/details?id=org.readera&hl=tr"""
    abo = sonsuz_sil(abo, o, '')
    o = """ReadEra ile kitap okuma
https://play.google.com/store/apps/details?id=org.readera"""
    abo = sonsuz_sil(abo, o, '')
    abo = abo.strip(CUSTOM_CAPTION) # caption sonunda eya başında CC varsa sil
    abo = sonsuz_sil(abo, '\n\n\n', '\n\n')
    return abo

def clear_filename(text, splitter=FILENAME_SPLITTER):
    if text is None: return text
    try:
        # deemoji
        regrex_pattern = re.compile(pattern = "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags = re.UNICODE)
        abo = regrex_pattern.sub(r'',text)
        abo = unicode_tr(abo).lower()
        
        abo = sonsuz_sil(abo, 'soru bankası çözümlü', 'çsb')
        abo = sonsuz_sil(abo, 'çözümlü soru bankası', 'çsb')
        abo = sonsuz_sil(abo, 'özetli soru bankası', 'ösb')
        abo = sonsuz_sil(abo, 'konu anlatımlı', 'ka')
        abo = sonsuz_sil(abo, 'konu özetli', 'kö')
        abo = sonsuz_sil(abo, 'sorubankası', 'sb')
        abo = sonsuz_sil(abo, 'soru bankası', 'sb')

        abo = sonsuz_sil(abo, 'final dergisi dershaneleri', 'final yay')
        abo = sonsuz_sil(abo, 'sınav dergisi dershaneleri', 'sınav yay')
        abo = sonsuz_sil(abo, 'dershaneleri', 'drshne')

        abo = sonsuz_sil(abo, '@pdfmekani', '')
        abo = sonsuz_sil(abo, '@pdfmeani', '')
        abo = sonsuz_sil(abo, '@egitimkitaplari', '')
        abo = sonsuz_sil(abo, '@egitimgrup', '')
        abo = sonsuz_sil(abo, 'benim hocam', 'bh')
        abo = sonsuz_sil(abo, '@osymdokuman', '')
        abo = sonsuz_sil(abo, '@yks 2020pdf', '')
        abo = sonsuz_sil(abo, '@gncpdfkanali', '')
        abo = sonsuz_sil(abo, '@trpdfdiyari', '')
        abo = sonsuz_sil(abo, '@ogrencixevi', '')
        abo = sonsuz_sil(abo, '@freexxpdf', '')
        abo = sonsuz_sil(abo, '☺️', '')
        abo = sonsuz_sil(abo, '⭐️', '')
        abo = sonsuz_sil(abo, '@pdfepub', '')
        abo = sonsuz_sil(abo, '@sanalpdftavsiye', '')
        abo = sonsuz_sil(abo, '@ogrencievi', '')
        abo = sonsuz_sil(abo, '@epubsfr', '')
        abo = sonsuz_sil(abo, '@turkleech', '')
        abo = sonsuz_sil(abo, '@kpsspdf2022', '')
        abo = sonsuz_sil(abo, '@ydtteam', '')
        abo = sonsuz_sil(abo, '@kitapdolabi', '')
        abo = sonsuz_sil(abo, '@kitapbol paylaşımıdır', '')
        abo = sonsuz_sil(abo, 'telegram t me kaynakpaylasim', '')
        abo = sonsuz_sil(abo, 'telegram t me', '')
        abo = sonsuz_sil(abo, 'telegram t', '')
        abo = sonsuz_sil(abo, 't me@sarsiv', '')
        abo = sonsuz_sil(abo, '@sarsiv', '')
        abo = sonsuz_sil(abo, 't me@sanalkitap', '')
        abo = sonsuz_sil(abo, '@sanalkitap', '')
        abo = sonsuz_sil(abo, 't me@kitaparsiv', '')
        abo = sonsuz_sil(abo, '@kitaparsiv', '')
        abo = sonsuz_sil(abo, '@behzatlink', '')
        abo = sonsuz_sil(abo, '@ekitappaylasimmmm', '')
        abo = sonsuz_sil(abo, '@ekitappaylasimmm', '')
        abo = sonsuz_sil(abo, '@meet book storage', '')
        abo = sonsuz_sil(abo, '@sanaldunyaarsivi', '')
        abo = sonsuz_sil(abo, '@dev arsiv', '')
        abo = sonsuz_sil(abo, '@pdfkaynaklar', '')
        abo = sonsuz_sil(abo, '@pdfinancial', '')
        abo = sonsuz_sil(abo, 'telegram@ogretmenodasi', '')
        abo = sonsuz_sil(abo, '@ogretmenodasi', '')
        abo = sonsuz_sil(abo, '@ayzpdf', '')
        abo = sonsuz_sil(abo, '@kitbooks', '')
        abo = sonsuz_sil(abo, '@kitapbol', '')
        abo = sonsuz_sil(abo, '@dkitap', '')
        abo = sonsuz_sil(abo, '@yksor2020', '')
        abo = sonsuz_sil(abo, '@yksor2021', '')
        abo = sonsuz_sil(abo, '@yksor2022', '')
        abo = sonsuz_sil(abo, '@yksor2023', '')
        abo = sonsuz_sil(abo, '@yksor2024', '')
        abo = sonsuz_sil(abo, '@yksor2025', '')
        abo = sonsuz_sil(abo, '@yksor', '')
        abo = sonsuz_sil(abo, '@ykspdfler', '')
        abo = sonsuz_sil(abo, '@ykspdfarchive', '')
        abo = sonsuz_sil(abo, '@yks2021pdf', '')
        abo = sonsuz_sil(abo, '@yks pdf', '')
        abo = sonsuz_sil(abo, '@tgarsiv', '')
        abo = sonsuz_sil(abo, '@cinciva', '')
        abo = sonsuz_sil(abo, '@pdfyurdu', '')
        abo = sonsuz_sil(abo, '@pdf kitablar', '')
        abo = sonsuz_sil(abo, '@pdfarsiv2021', '')
        abo = sonsuz_sil(abo, '@pdfarsiv2022', '')
        abo = sonsuz_sil(abo, '@kitupchi', '')
        abo = sonsuz_sil(abo, '@denemeotag', '')
        abo = sonsuz_sil(abo, '@ekipdflgs', '')
        abo = sonsuz_sil(abo, '@skitap', '')
        abo = sonsuz_sil(abo, '@megapack', '')

        abo = sonsuz_sil(abo, 'pdfdrive com', '')
        abo = sonsuz_sil(abo, 'pdfdrive', '')
        abo = sonsuz_sil(abo, 'indirpdf net', '')
        abo = sonsuz_sil(abo, 'compressed', 'kçk')
        abo = sonsuz_sil(abo, 'pdfkitabevim com', '')
        abo = sonsuz_sil(abo, '@akiraninkitapdunyasi', '')
        abo = sonsuz_sil(abo, '@babillkutuphanesi', '')
        abo = sonsuz_sil(abo, '@akirasbookworld', '')
        abo = sonsuz_sil(abo, 'pdf indir', 'pdf')
        abo = sonsuz_sil(abo, 'pdfdrivecom', '')
        abo = sonsuz_sil(abo, 'ekitappdfoku com', '')
        abo = sonsuz_sil(abo, 'www booktandunya com', '')
        abo = sonsuz_sil(abo, 'booktandunya com', '')
        abo = sonsuz_sil(abo, 'bedavapdf com', '')
        abo = sonsuz_sil(abo, 'pdfarsiv com', '')
        abo = sonsuz_sil(abo, 'www arsivciniz com', '')
        abo = sonsuz_sil(abo, 'arsivciniz com', '')
        abo = sonsuz_sil(abo, 'şifre www kitapfan com', '')
        abo = sonsuz_sil(abo, 'www kitapfan com', '')
        abo = sonsuz_sil(abo, 'kitapfan com', '')
        abo = sonsuz_sil(abo, 'şifre www twilightturk com', '')
        abo = sonsuz_sil(abo, 'www twilightturk com', '')
        abo = sonsuz_sil(abo, 'twilightturk com', '')
        abo = sonsuz_sil(abo, 'şifre webcanavari net', '')
        abo = sonsuz_sil(abo, 'webcanavari net', '')
        
        abo = sonsuz_sil(abo, 'bahar dönemi', 'bahar')
        abo = sonsuz_sil(abo, 'güz dönemi', 'güz')

        abo = sonsuz_sil(abo, 'yayınları', 'yay')
        abo = sonsuz_sil(abo, 'yayınevi', 'yay')
        abo = sonsuz_sil(abo, 'yayıncılık', 'yay')
        abo = sonsuz_sil(abo, 'yayınlar', 'yay')
        abo = sonsuz_sil(abo, 'dershaneleri', 'drsahi')
        abo = sonsuz_sil(abo, 'yayın nları', 'yay')
        abo = sonsuz_sil(abo, 'yayınlaır', 'yay')
        abo = sonsuz_sil(abo, 'kitabevi', 'ktbvi')

        abo = sonsuz_sil(abo, 'adlı dosyanın kopyası adlı dosyanın', '')
        abo = sonsuz_sil(abo, 'dosyasının kopyası', '')
        abo = sonsuz_sil(abo, 'adlı dosyanın kopyası', '')
        abo = sonsuz_sil(abo, 'dosyasını sizinle paylaşıyorum', '')
        abo = sonsuz_sil(abo, '· 1 sürümü', '')
        abo = sonsuz_sil(abo, '· 2 sürümü', '')
        abo = sonsuz_sil(abo, 'pdf 1 pdf', 'pdf')
        abo = sonsuz_sil(abo, 'adlı pdf', 'pdf')
        abo = sonsuz_sil(abo, 'pdf pdf', 'pdf')
        abo = sonsuz_sil(abo, 'epub epub', 'epub')
        abo = sonsuz_sil(abo, 'exe exe', 'exe')
        abo = sonsuz_sil(abo, 'pdf indir', '')

        abo = sonsuz_sil(abo, 'paragraf', 'pgrf')
        abo = sonsuz_sil(abo, 'matematik', 'mtik')
        abo = sonsuz_sil(abo, 'geometri', 'gtri')
        abo = sonsuz_sil(abo, 'türkçe', 'trkç')
        abo = sonsuz_sil(abo, 'biyoloji', 'bylj')
        abo = sonsuz_sil(abo, 'edebiyat', 'ebyt')
        abo = sonsuz_sil(abo, 'coğrafya', 'cfya')

        abo = sonsuz_sil(abo, 'eşit ağırlık', 'ea')
        abo = sonsuz_sil(abo, 'sayısal', 'say')
        abo = sonsuz_sil(abo, 'sözel', 'söz')

        abo = sonsuz_sil(abo, 'trigonometri', 'trgnmtri')
        # yan yana bomboş karakterler
        abo = sonsuz_sil(abo, '[]', '')
        abo = sonsuz_sil(abo, '()', '')

        abo = re.sub(r'[\#]+','', abo)
        # boşlukla
        abo = re.sub(r'[\.\+\-_\(\)\s\–\,\^\™\!\0\t]+',' ', abo)
        abo = abo.strip()

        # ikiye böl
        # a = abo.split(' ')
        # s1=s2=""
        # for word in a:
        #     if len(s1) >= 30: s2+=word + " "
        #     else: s1+=word + " "
        # s1=s1.strip(' ').strip()
        # s2=s2.strip(' ').strip()
        # if len(s2) != 0: s1 = s1 + "\n" + s2
        # s1=s1.replace(' ', '.')
        # print(s1)
        # abo = s1
        
        return abo.replace(' ', splitter)
    except Exception as e:
        LOG.exception(e)
        return text
