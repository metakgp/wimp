import requests
import webbrowser
import erpcreds
import iitkgp_erp_login.erp as erp
from iitkgp_erp_login.endpoints import HOMEPAGE_URL

headers = {
    'timeout': '20',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/51.0.2704.79 Chrome/51.0.2704.79 Safari/537.36',
}
session = requests.Session()

sessionToken, ssoToken = erp.login(headers, session, ERPCREDS=erpcreds, LOGGING=True, SESSION_STORAGE_FILE=".session")

logged_in_url = f"{HOMEPAGE_URL}?ssoToken={ssoToken}"
webbrowser.open(logged_in_url)
