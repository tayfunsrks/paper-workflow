# Property of Kor.PiracyTeam - GNU General Public License v2.0

from pyrogram.types import Message
from info import HELP_MESSAGES_AFTER_FILE, VIRUSTOTAL_API
from pyrogram.types import InlineKeyboardMarkup as ikm

# Get logging configurations
from info import LOG
from utils import temp

async def yardimMesaji(dosyaadi: str, message: Message):
    if not HELP_MESSAGES_AFTER_FILE:
        return
    if dosyaadi:
        if dosyaadi.endswith(("00", "01", "02", "03", "04", "05")):
            await message.reply_text(("Bölümlü arşiv tespit ettim (sanırım)\naçmak için şunlara ihtiyacın olacak:\n\nhttps://telegra.ph/0-a%C3%A7mak-ve-olu%C5%9Fturmak-04-05\nhttps://www.youtube.com/watch?v=2dfRvBNjZIk\n\nrica ederim."), disable_web_page_preview=True, quote=True, reply_markup=ikm(temp.kapat_btn))

        elif dosyaadi.endswith(("rar", "zip", "7z", "tar", "gz")):
            await message.reply_text("Arşiv tespit ettim (sanırım)\n\narşivleri telegram içinden çıkartmak için bazı botlar:\n\n@unziprobot @UnzipinBot @UnArchiveBot @ExtractProBot @ExtractorRobot\n\nrica ederim.", disable_web_page_preview=True, quote=True, reply_markup=ikm(temp.kapat_btn))

        elif dosyaadi.endswith(("exe", "msi", "jar")):
            infostr = "Program tespit ettim (sanırım)\nözellikle bu dosya türünde dikkatli olmalısın.\n\nVirüs tarama botları: @VirusTotalAV_bot @VirusTotal_AVBot"
            if VIRUSTOTAL_API:
                infostr += "\nAyrıca ben de dosya(ları)nı tarayabilirim. Dosyanı /virustotal diye yanıtla."
            await message.reply_text(infostr, disable_web_page_preview=True, quote=True, reply_markup=ikm(temp.kapat_btn))
    # - 001 gibi arşivse tuto gönder
