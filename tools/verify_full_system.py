
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
DASHBOARD_URL = f"{BASE_URL}/dashboard"

USERNAME = "__super__"
PASSWORD = "Kayra_1507"

session = requests.Session()

def check_login():
    logging.info(f"Checking Login at {LOGIN_URL}...")
    try:
        # Get CSRF token if needed
        response = session.get(LOGIN_URL, timeout=10, verify=False)
        if response.status_code != 200:
            logging.error(f"Login Page Load Failed: {response.status_code}")
            return False

        # Extract CSRF token
        csrf_token = None
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        if match:
            csrf_token = match.group(1)
            logging.info("CSRF token found and extracted.")
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
        
        if response.status_code == 200:
            if response.url.endswith('/dashboard') or "dashboard" in response.url or "Hoşgeldiniz" in response.text or "Dashboard" in response.text:
                logging.info("Login SUCCESS.")
                return True
            elif "Giriş" not in response.text and "Login" not in response.text:
                 logging.info("Login SUCCESS (Content suggests authorized).")
                 return True
            else:
                logging.error(f"Login FAILED: Dashboard not reached. URL: {response.url}")
                if "Kullanıcı adı veya parola hatalı" in response.text:
                     logging.error("Reason: Invalid credentials.")
                else:
                     logging.error(f"Response text preview: {response.text[:1000]}")
                     with open('failed_login.html', 'w', encoding='utf-8') as f:
                         f.write(response.text)
                     logging.info("Saved failed login page to failed_login.html")
                return False
        else:
            logging.error(f"Login POST Failed: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Login Exception: {e}")
        return False

def check_dashboard():
    logging.info("Checking Dashboard...")
    try:
        response = session.get(DASHBOARD_URL, timeout=10, verify=False)
        if response.status_code == 200:
            logging.info("Dashboard Load SUCCESS.")
            return True
        else:
            logging.error(f"Dashboard Load Failed: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Dashboard Exception: {e}")
        return False

def check_modules():
    modules = [
        '/governance', '/social', '/environmental', '/supply_chain', '/economic',
        '/esg', '/csrd', '/eu_taxonomy', '/issb', '/iirc', '/esrs', '/tcfd', '/tnfd', '/cdp',
        '/gri', '/sasb', '/ungc', '/sdg',
        '/reports', '/users', '/companies', '/prioritization', '/targets',
        '/surveys', '/cbam', '/lca', '/realtime', '/biodiversity', '/regulation', '/benchmark', '/training',
        '/human_rights', '/labor', '/consumer', '/community'
    ]
    
    failed_modules = []
    
    logging.info(f"Checking {len(modules)} Modules...")
    
    for mod in modules:
        url = urljoin(BASE_URL, mod)
        try:
            response = session.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                # Check for missing translation keys in the page content
                content = response.text
                
                # Check for redirection to login (session lost or auth failed)
                if "Giriş" in content and "password" in content:
                    logging.error(f"{mod}: FAIL (Redirected to Login)")
                    failed_modules.append(mod)
                    continue

                missing_keys = re.findall(r'btn_[a-z_]+|title_[a-z_]+|desc_[a-z_]+', content)
                # Filter out likely false positives (e.g. inside scripts) - simple check
                # We assume if it shows up in text, it's a bug.
                
                # Check if it's a real page or an error page masking as 200
                if "Sistem Hatası" in content or "500 Internal Server Error" in content:
                    logging.error(f"{mod}: FAIL (Error Page Content)")
                    failed_modules.append(mod)
                elif missing_keys:
                     # Check if these are actually visible (crude check)
                     visible_missing = []
                     for k in set(missing_keys):
                         # If key appears outside of quotes or tags, it might be visible text
                         # Simple heuristic: if it appears as >key< it is definitely visible
                         if f'>{k}<' in content:
                             visible_missing.append(k)
                     
                     if visible_missing:
                         logging.warning(f"{mod}: WARN (Visible missing keys: {visible_missing})")
                     else:
                         logging.info(f"{mod}: PASS")
                else:
                    logging.info(f"{mod}: PASS")
            else:
                logging.error(f"{mod}: FAIL ({response.status_code})")
                if response.status_code == 500:
                    logging.error(f"Response Body: {response.text[:1000]}")
                failed_modules.append(mod)
        except Exception as e:
            logging.error(f"{mod}: ERROR ({e})")
            failed_modules.append(mod)
            
    if failed_modules:
        logging.error(f"Failed Modules: {failed_modules}")
        return False
    
    logging.info("All Modules PASSED.")
    return True

def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

if __name__ == '__main__':
    if check_login():
        dash_ok = check_dashboard()
        mods_ok = check_modules()
        
        if dash_ok and mods_ok:
            print("\nSYSTEM VERIFICATION: SUCCESS")
            sys.exit(0)
        else:
            print("\nSYSTEM VERIFICATION: FAILED")
            sys.exit(1)
    else:
        print("\nSYSTEM VERIFICATION: FAILED (Login)")
        sys.exit(1)
