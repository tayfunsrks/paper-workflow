# Property of Kor.PiracyTeam - GNU General Public License v2.0

import hashlib
import os
import re
import requests
from info import VIRUSTOTAL_API

# Get logging configurations
from info import LOG

baseUrlFile = 'https://www.virustotal.com/vtapi/v2/file/'
baseUrlUrl = 'https://www.virustotal.com/vtapi/v2/url/'
apiKey = VIRUSTOTAL_API

def get_report(file_hash, link = False):
    '''
    :param file_hash: md5/sha1/sha256
    :return: json response / None
    '''
    try:
        LOG.info("VirusTotal - Check for existing report")
        url = ""
        url = f'{baseUrlUrl}report' if link else f'{baseUrlFile}report'
        params = {
            'apikey': apiKey,
            'resource': file_hash
        }
        headers = {"Accept-Encoding": "gzip, deflate"}
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 403:
                LOG.error("VirusTotal -  Permission denied, wrong api key?")
                return None
        except Exception:
            LOG.error("VirusTotal -  ConnectionError, check internet connectivity")
            return None
        try:
            return response.json()
        except ValueError:
            return None
    except Exception as e:
        LOG.exception(e)
        return None

def upload_file(file_path, islink=False):
    """
    :param file_path: file path to upload
    :return: json response / None
    """
    try:
        url = ""
        if islink:
            url = f'{baseUrlUrl}scan'
            params = {'apikey': apiKey, 'url': file_path}
            response = requests.post(url, data=params)
        else:
            url = f'{baseUrlFile}scan'
            if os.path.getsize(file_path) > 32 * 1024 * 1024:
                url = 'https://www.virustotal.com/vtapi/v2/file/scan/upload_url'
                params = {'apikey': apiKey}
                response = requests.get(url, params=params)
                upload_url_json = response.json()
                url = upload_url_json['upload_url']
            files = {'file': open(file_path, 'rb')}
            headers = {"apikey": apiKey}
            response = requests.post(url, files=files, data=headers)
        if not response:
            LOG.error("VirusTotal -  ConnectionError, check internet connectivity")
            return None
        if response.status_code == 403:
            LOG.error("VirusTotal -  Permission denied, wrong api key?")
            return None
        return response.json()
    except Exception:
        LOG.exception("VirusTotal -  upload_file")
        return None

def getMD5(path):
    with open(path, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()

def get_result(file_path):
    """
    Uoloading a file and getting the approval msg from VT or fetching existing report
    :param file_path: file's path
    :param file_hash: file's hash - md5/sha1/sha256
    :return: VirusTotal result json / None upon error
    """
    hasho = None
    file = False
    url = False
    try:
        file = bool(os.path.isfile(file_path))
        LOG.info("file was True")
    except Exception as e:
        LOG.exception(e)
        file = False
    if not file:
        try:
            hasho = re.match("((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", file_path)[0]
            url = True
            LOG.info("url was True")
        except Exception:
            hasho = None
            url = False
    if file:
        hasho = getMD5(path=file_path)
    if not (hasho and file):
        hasho = file_path
    try:
        if report := get_report(hasho, url):
            LOG.info("VirusTotal - Report Found.")
            LOG.info(report)
            if int(report['response_code']) == 1:
                return report
            elif file_path:
                LOG.info("VirusTotal -  File Upload")
                return upload_file(file_path, url)
    except Exception as e:
        LOG.error(e)

def validateValue(result, value):
    try: return result[value]
    except Exception: return False

def getResultAsReadable(result):
    if not result:
        LOG.error(result)
        return "Birşeyler ters gitti kıymetli. Bi 3 dakkaya tekrar dene"
    someInfo = ""
    if validateValue(result, 'verbose_msg'):
        go = None if "Scan finished" in result['verbose_msg'] else result['verbose_msg']
        if go: someInfo += f"\nMesaj: <code>{go}</code>"
    if validateValue(result, 'scan_id'): someInfo += f"\nTarama ID: <code>{result['scan_id']}</code>"
    if validateValue(result, 'scan_date'): someInfo += f"\nTarih: <code>{result['scan_date']}</code>"
    if validateValue(result, 'md5'): someInfo += f"\nMD5: <code>{result['md5']}</code>"
    if validateValue(result, 'sha1'): someInfo += f"\nSHA1: <code>{result['sha1']}</code>"
    if validateValue(result, 'sha256'): someInfo += f"\nSHA256: <code>{result['sha256']}</code>"
    if validateValue(result, 'permalink'): someInfo += f"\nLink: {result['permalink']}"
    if validateValue(result, 'scans'):
        pos = []
        neg = []
        scans = result['scans']
        for i in scans:
            if bool((scans[i]['detected'])): pos.append(i) 
            else: neg.append(i)
        tore = someInfo + "\n\nTotal: " + str(result['total'])  + \
            " | Positives: " + str(result['positives']) + \
            " | Negatives: " + str(len(neg))
        if len(pos) > 0: tore += "\nDetections: <code>" + ", ".join(pos) + "</code>"
        return tore
    else: someInfo += '\n\nDosyanısı taranması için gönderdik kıymetli' \
        '\nBasen linkisine girmeyince taramanısı dikkate almayabilir' \
        '\nYa linkisine girin ya da 5 dakkaya tekrar taratın efendimis'
    return someInfo
