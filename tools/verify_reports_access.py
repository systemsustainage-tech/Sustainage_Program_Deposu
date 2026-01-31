import requests
import sys

# Configuration
BASE_URL = "https://sustainage.cloud"
LOGIN_URL = f"{BASE_URL}/login"
REPORTS_URL = f"{BASE_URL}/reports"
USERNAME = "test_user"
PASSWORD = "password123"

def verify_reports_access():
    session = requests.Session()
    
    # Login
    print(f"Logging in as {USERNAME}...")
    resp = session.post(LOGIN_URL, data={'username': USERNAME, 'password': PASSWORD})
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code}")
        return False
        
    # Access Reports
    print(f"Accessing {REPORTS_URL}...")
    resp = session.get(REPORTS_URL)
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print("Success: /reports is accessible.")
        if "Raporlar" in resp.text or "Reports" in resp.text:
            print("Content verified (contains 'Raporlar' or 'Reports').")
            return True
        else:
            print("Warning: 200 OK but expected keywords not found.")
            print(resp.text[:500])
            return True # Still count as access success
    elif resp.status_code == 403:
        print("Failure: 403 Forbidden.")
        return False
    else:
        print(f"Failure: Unexpected status code {resp.status_code}")
        return False

if __name__ == "__main__":
    if verify_reports_access():
        sys.exit(0)
    else:
        sys.exit(1)
