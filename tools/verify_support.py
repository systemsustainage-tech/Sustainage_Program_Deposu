
import requests
import logging
import sys
import re
import urllib3
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://72.62.150.207"
LOGIN_URL = f"{BASE_URL}/login"

USERNAME = "__super__"
PASSWORD = "Kayra_1507"

session = requests.Session()

def check_login():
    logging.info(f"Checking Login at {LOGIN_URL}...")
    try:
        response = session.get(LOGIN_URL, timeout=10, verify=False)
        csrf_token = None
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        if match:
            csrf_token = match.group(1)

        data = {'username': USERNAME, 'password': PASSWORD}
        if csrf_token:
            data['csrf_token'] = csrf_token

        headers = {'Referer': LOGIN_URL}
        response = session.post(LOGIN_URL, data=data, timeout=15, verify=False, allow_redirects=True, headers=headers)
        
        if response.status_code == 200 and ("dashboard" in response.url or "Hoşgeldiniz" in response.text):
            logging.info("Login SUCCESS.")
            return True
        else:
            logging.error(f"Login FAILED. Status: {response.status_code}, URL: {response.url}")
            return False
    except Exception as e:
        logging.error(f"Login Exception: {e}")
        return False

def check_support_routes():
    routes = [
        '/support',
        '/support/create',
        '/help'
    ]
    
    success = True
    for route in routes:
        url = f"{BASE_URL}{route}"
        logging.info(f"Checking {url}...")
        try:
            response = session.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                logging.info(f"PASS: {route}")
            else:
                logging.error(f"FAIL: {route} returned {response.status_code}")
                success = False
        except Exception as e:
            logging.error(f"FAIL: {route} exception: {e}")
            success = False
            
    return success

if __name__ == "__main__":
    if check_login():
        if check_support_routes():
            logging.info("Support System Verification Passed.")
            sys.exit(0)
        else:
            logging.error("Support System Verification Failed.")
            sys.exit(1)
    else:
        sys.exit(1)
