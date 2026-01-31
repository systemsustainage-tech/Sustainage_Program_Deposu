
import requests
import sys

# Configuration
BASE_URL = "https://sustainage.cloud"
LOGIN_URL = f"{BASE_URL}/login"
DASHBOARD_URL = f"{BASE_URL}/dashboard"
USERS_URL = f"{BASE_URL}/users" # Admin only

USERNAME = "__super__"
PASSWORD = "super123"

def test_super_login():
    session = requests.Session()
    
    # Login
    print(f"Logging in as {USERNAME}...")
    resp = session.post(LOGIN_URL, data={'username': USERNAME, 'password': PASSWORD})
    
    # Check if redirected to dashboard or returned 200 (if JSON API, but here it's template)
    # Usually redirects to dashboard upon success
    print(f"Login Response Status: {resp.status_code}")
    
    if resp.url == LOGIN_URL or "Giriş Yap" in resp.text:
         print("Login failed (still on login page).")
         return False
         
    # Check Dashboard Access
    print(f"Accessing {DASHBOARD_URL}...")
    resp = session.get(DASHBOARD_URL)
    print(f"Dashboard Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print("Failed to access dashboard.")
        return False
        
    # Check Admin Page Access
    print(f"Accessing {USERS_URL}...")
    resp = session.get(USERS_URL)
    print(f"Users Page Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print("Success: Admin panel accessible.")
        return True
    elif resp.status_code == 403:
        print("Failure: Admin panel forbidden (403). Role might be incorrect.")
        return False
    else:
        print(f"Failure: Unexpected status {resp.status_code}")
        return False

if __name__ == "__main__":
    if test_super_login():
        sys.exit(0)
    else:
        sys.exit(1)
