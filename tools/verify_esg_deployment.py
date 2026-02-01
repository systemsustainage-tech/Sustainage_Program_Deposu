
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
ESG_URL = f"{BASE_URL}/esg"

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

        # Extract CSRF token
        csrf_token = None
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        if match:
            csrf_token = match.group(1)
        else:
            logging.warning("CSRF token NOT found in login page.")

        data = {'username': USERNAME, 'password': PASSWORD}
        if csrf_token:
            data['csrf_token'] = csrf_token

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': LOGIN_URL
        }

        response = session.post(LOGIN_URL, data=data, timeout=15, verify=False, allow_redirects=True, headers=headers)
        
        if response.status_code == 200 and ("dashboard" in response.url or "Dashboard" in response.text or "Hoşgeldiniz" in response.text):
            logging.info("Login SUCCESS.")
            return True
        else:
            logging.error(f"Login FAILED: {response.status_code} URL: {response.url}")
            return False
    except Exception as e:
        logging.error(f"Login Exception: {e}")
        return False

def verify_esg_module():
    logging.info(f"Checking ESG Module at {ESG_URL}...")
    try:
        response = session.get(ESG_URL, timeout=10, verify=False)
        if response.status_code == 200:
            content = response.text
            
            # Check for specific new content
            if "Veri Kaynakları ve Bonuslar" in content:
                logging.info("ESG Module content verification: SUCCESS (Found 'Veri Kaynakları ve Bonuslar')")
                
                # Optional: Check if stats are rendered
                if "Karbon Ayak İzi" in content:
                    logging.info("ESG Module detailed stats verification: SUCCESS")
                
                return True
            else:
                logging.warning("ESG Module content verification: WARNING (Did not find 'Veri Kaynakları ve Bonuslar' - Old template might be cached or deployment failed)")
                # Log a snippet
                logging.info(f"Content snippet: {content[:500]}...")
                return False
        else:
            logging.error(f"ESG Module Failed: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"ESG Module Exception: {e}")
        return False

if __name__ == '__main__':
    if check_login():
        if verify_esg_module():
            print("\nESG DEPLOYMENT VERIFICATION: SUCCESS")
            sys.exit(0)
        else:
            print("\nESG DEPLOYMENT VERIFICATION: FAILED")
            sys.exit(1)
    else:
        print("\nESG DEPLOYMENT VERIFICATION: FAILED (Login)")
        sys.exit(1)
