import requests
import sys
import urllib3
import time

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://72.62.150.207"
LOGIN_URL = f"{BASE_URL}/login"

USERNAME = "__super__"
PASSWORD = "Kayra_1507" # Using the known correct password for super user

def check_modules():
    session = requests.Session()
    
    print(f"Logging in to {BASE_URL} as {USERNAME}...")
    try:
        # 1. Login
        r = session.post(LOGIN_URL, data={'username': USERNAME, 'password': PASSWORD}, verify=False, allow_redirects=True)
        
        # Check if login was successful (redirected to dashboard or returned 200 OK on dashboard)
        if r.status_code == 200 and ('Dashboard' in r.text or 'Gösterge Paneli' in r.text or '/logout' in r.text):
            print("Login Successful.")
        elif r.history and r.history[0].status_code == 302:
             # Redirected
             print(f"Login Successful (Redirected to {r.url})")
        else:
            print(f"Login Failed. Status: {r.status_code}")
            if 'Giriş Yap' in r.text:
                print("Still on login page.")
            return

        modules = [
            '/governance', '/social', '/environmental', '/supply_chain', '/economic',
            '/esg', '/csrd', '/eu_taxonomy', '/issb', '/iirc', '/esrs', '/tcfd', '/tnfd', '/cdp',
            '/gri', '/sasb', '/ungc', '/sdg',
            '/reports', '/users', '/companies', '/prioritization', '/targets'
        ]

        print("\nChecking Modules...")
        failed_modules = []
        for mod in modules:
            url = f"{BASE_URL}{mod}"
            try:
                resp = session.get(url, verify=False, allow_redirects=True)
                if resp.status_code == 200:
                    # Check for "Internal Server Error" text just in case custom error page returns 200
                    if "Internal Server Error" in resp.text:
                         print(f"[FAIL] {mod} : 500 Internal Server Error (Text match)")
                         failed_modules.append(mod)
                    else:
                        print(f"[OK] {mod}")
                else:
                    print(f"[FAIL] {mod} : Status {resp.status_code}")
                    print(f"Response snippet: {resp.text[:200]}")
                    failed_modules.append(mod)
            except Exception as e:
                print(f"[ERROR] {mod} : {e}")
                failed_modules.append(mod)

        if failed_modules:
            print(f"\nFAIL: The following modules failed: {', '.join(failed_modules)}")
            sys.exit(1)
        else:
            print("\nSUCCESS: All modules are accessible.")
            sys.exit(0)

    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_modules()
