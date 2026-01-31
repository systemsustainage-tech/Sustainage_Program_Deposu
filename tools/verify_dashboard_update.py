import requests
import sys

# Configuration
BASE_URL = "https://sustainage.cloud"
LOGIN_URL = f"{BASE_URL}/login"
DASHBOARD_URL = f"{BASE_URL}/dashboard"

# User Credentials (using test_user as verified in previous steps)
USERNAME = "test_user"
PASSWORD = "password123"

def verify_dashboard():
    session = requests.Session()
    
    # 1. Login
    try:
        print(f"Attempting login with {USERNAME}...")
        resp = session.post(LOGIN_URL, data={'username': USERNAME, 'password': PASSWORD})
        if resp.status_code != 200:
            print(f"Login failed with status code {resp.status_code}")
            return False
        
        if "dashboard" not in resp.url and "dashboard" not in resp.text.lower():
             # Sometimes login redirects, sometimes it renders dashboard directly
             pass
        
        # 2. Get Dashboard
        print("Fetching dashboard...")
        resp = session.get(DASHBOARD_URL)
        if resp.status_code != 200:
            print(f"Failed to access dashboard. Status: {resp.status_code}")
            return False
            
        content = resp.text
        
        # 3. Check for new section
        target_string = "Sürdürülebilirlik Modülleri"
        if target_string in content:
            print(f"[SUCCESS] Found '{target_string}' on dashboard.")
        else:
            print(f"[FAILURE] '{target_string}' NOT found on dashboard.")
            # Print a snippet to debug
            print("Dashboard content snippet (first 500 chars):")
            print(content[:500])
            return False

        # 4. Check for a few specific modules to ensure cards are rendered
        modules_to_check = [
            "Karbon (Carbon)",
            "Su (Water)",
            "GRI Standartları",
            "SDG (BM Sürdürülebilirlik)"
        ]
        
        all_found = True
        for mod in modules_to_check:
            if mod in content:
                print(f"[OK] Found module card: {mod}")
            else:
                print(f"[MISSING] Module card not found: {mod}")
                all_found = False
                
        return all_found

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if verify_dashboard():
        sys.exit(0)
    else:
        sys.exit(1)
