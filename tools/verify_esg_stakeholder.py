
import requests
import logging
import sys
import urllib3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://72.62.150.207"
LOGIN_URL = f"{BASE_URL}/login"
ESG_URL = f"{BASE_URL}/esg"
ESG_SETTINGS_URL = f"{BASE_URL}/esg/settings"
STAKEHOLDER_URL = f"{BASE_URL}/stakeholder"
REGULATION_URL = f"{BASE_URL}/regulation"

USERNAME = "__super__"
PASSWORD = "Kayra_1507"

session = requests.Session()

def check_login():
    logging.info(f"Checking Login at {LOGIN_URL}...")
    try:
        response = session.get(LOGIN_URL, timeout=10, verify=False)
        if response.status_code != 200:
            logging.error(f"Login Page Load Failed: {response.status_code}")
            return False

        data = {'username': USERNAME, 'password': PASSWORD}
        response = session.post(LOGIN_URL, data=data, timeout=15, verify=False, allow_redirects=True)
        
        if response.status_code == 200 and ("dashboard" in response.url or "Hoşgeldiniz" in response.text):
            logging.info("Login SUCCESS.")
            return True
        else:
            logging.error(f"Login FAILED. URL: {response.url}")
            return False
    except Exception as e:
        logging.error(f"Login Exception: {e}")
        return False

def check_url(url, name):
    logging.info(f"Checking {name} at {url}...")
    try:
        response = session.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            if "Giriş" in response.text and "password" in response.text:
                 logging.error(f"{name}: FAIL (Redirected to Login)")
                 return False
            logging.info(f"{name}: SUCCESS (200 OK)")
            return True
        else:
            logging.error(f"{name}: FAIL ({response.status_code})")
            return False
    except Exception as e:
        logging.error(f"{name}: Exception: {e}")
        return False

def verify_esg_settings_content():
    logging.info("Verifying ESG Settings Content...")
    try:
        response = session.get(ESG_SETTINGS_URL, timeout=10, verify=False)
        if "Ağırlıklar" in response.text or "Weights" in response.text or "Çevresel" in response.text:
             logging.info("ESG Settings Content Verified.")
             return True
        else:
             logging.error("ESG Settings Content Verification Failed (Key terms not found).")
             return False
    except Exception as e:
        logging.error(f"ESG Settings Content Exception: {e}")
        return False

def main():
    if not check_login():
        sys.exit(1)
    
    success = True
    
    if not check_url(ESG_URL, "ESG Module"): success = False
    if not check_url(ESG_SETTINGS_URL, "ESG Settings"): success = False
    if not verify_esg_settings_content(): success = False
    if not check_url(STAKEHOLDER_URL, "Stakeholder Module"): success = False
    if not check_url(REGULATION_URL, "Regulation Module"): success = False
    
    if success:
        logging.info("All checks PASSED.")
        sys.exit(0)
    else:
        logging.error("Some checks FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
