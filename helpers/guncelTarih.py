# Property of Kor.PiracyTeam - GNU General Public License v2.0

import pytz
from datetime import datetime

# Get logging configurations

def guncelTarih(timezone = 'Europe/Istanbul'):
    a = str(datetime.now(pytz.timezone(timezone)))
    return a.replace('\n', '').strip()
