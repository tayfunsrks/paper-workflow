# Property of Kor.PiracyTeam - GNU General Public License v2.0

# https://stackoverflow.com/questions/19030948/python-utf-8-lowercase-turkish-specific-letter

# Get logging configurations
from info import LOG

class unicode_tr(str):
    """usage: print unicode_tr("kitap").upper()
    print unicode_tr("KİTAP").lower()"""
    CHARMAP = {
        "to_upper": {
            u"ı": u"I",
            u"i": u"İ",
        },
        "to_lower": {
            u"I": u"ı",
            u"İ": u"i",
        }
    }
    def lower(self):
        for key, value in self.CHARMAP.get("to_lower").items():
            self = self.replace(key, value)
        return self.lower()

    def upper(self):
        for key, value in self.CHARMAP.get("to_upper").items():
            self = self.replace(key, value)
        return self.upper()

