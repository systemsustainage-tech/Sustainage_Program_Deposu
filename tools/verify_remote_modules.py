import requests
from bs4 import BeautifulSoup
import time

# Use HTTPS and disable verification to bypass redirect if possible
BASE_URL = "https://72.62.150.207"
LOGIN_URL = f"{BASE_URL}/login"
SDG_URL = f"{BASE_URL}/sdg"
GRI_URL = f"{BASE_URL}/gri"
VERIFY_SSL = False
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def verify_modules():
    session = requests.Session()
    session.verify = VERIFY_SSL
    # Spoof Host header if needed (Nginx might check it)
    # session.headers.update({'Host': 'sustainage.cloud'}) 
    
    # 1. Login
    print(f"Logging in to {BASE_URL}...")
    try:
        # Get login page first to grab CSRF token if needed
        login_page = session.get(LOGIN_URL, verify=VERIFY_SSL)
        csrf_token = None
        if 'name="csrf_token"' in login_page.text:
            # Simple extraction
            import re
            match = re.search(r'name="csrf_token" value="([^"]+)"', login_page.text)
            if match:
                csrf_token = match.group(1)
                print(f"Found CSRF token: {csrf_token[:10]}...")
        
        data = {
            'username': '__super__',
            'password': 'Kayra_1507'
        }
        if csrf_token:
            data['csrf_token'] = csrf_token
            
        resp = session.post(LOGIN_URL, data=data, verify=VERIFY_SSL)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code}")
            return False
        
        # Check if we are really logged in (not redirected back to login)
        print(f"Post-Login URL: {resp.url}")
        if '/login' in resp.url:
             print("Login failed: Redirected back to login page.")
             print("Page content excerpt:")
             print(resp.text[:1000])
             return False
             
        print("Login successful.")
    except Exception as e:
        print(f"Login error: {e}")
        return False
        
    # 2. Check SDG
    print("\nChecking SDG module...")
    try:
        resp = session.get(SDG_URL)
        if resp.status_code == 200:
            if "login" in resp.url:
                print("SDG: Redirected to Login! (Session lost?)")
            elif "Sürdürülebilir Kalkınma Hedefleri" in resp.text or "SDG" in resp.text:
                 print("SDG: OK - Content Verified")
            else:
                 print("SDG: Warning - Page loaded but keywords not found")
        else:
            print(f"SDG: Failed ({resp.status_code})")
    except Exception as e:
        print(f"SDG Check error: {e}")

    # 3. Check GRI
    print("\nChecking GRI module...")
    try:
        resp = session.get(GRI_URL)
        if resp.status_code == 200:
            if "login" in resp.url:
                print("GRI: Redirected to Login! (Session lost?)")
            else:
                content = resp.text
                print("GRI: Page loaded")
                
                # Check for 2026 updates
                checks = [
                    "Petrol ve Gaz", 
                    "GRI 11", 
                    "Sektöre Göre Filtrele",
                    "Madencilik"
                ]
                
                found_all = True
                for check in checks:
                    if check in content:
                        print(f"  [+] Found: {check}")
                    else:
                        print(f"  [-] Missing: {check}")
                        found_all = False
                
                if found_all:
                    print("GRI: OK - All 2026 updates verified")
                else:
                    print("GRI: Warning - Some updates missing")
        else:
            print(f"GRI: Failed ({resp.status_code})")
    except Exception as e:
        print(f"GRI Check error: {e}")

if __name__ == "__main__":
    verify_modules()
