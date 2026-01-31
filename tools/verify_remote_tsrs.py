import requests
import re

BASE_URL = "http://72.62.150.207"

def verify_tsrs():
    print("Verifying TSRS Module...")
    
    # Login first (if needed, but some pages might be protected)
    # Assuming we need login. I'll use a session.
    session = requests.Session()
    
    # Try to access /tsrs directly. If it redirects to login, we know it's protected.
    try:
        response = session.get(f"{BASE_URL}/tsrs", allow_redirects=True, timeout=10)
        print(f"Initial access status: {response.status_code}")
        
        if "login" in response.url:
            print("Redirected to login. Attempting to login...")
            # Perform login
            login_data = {
                'username': '__super__',
                'password': 'Kayra_1507' # Using known super admin creds
            }
            # Note: The login form might require CSRF token.
            # Let's fetch login page first to get CSRF token if present
            login_page = session.get(f"{BASE_URL}/login", timeout=10)
            
            # Simple check if login is successful with POST
            # Assuming standard Flask-Login without strict CSRF for this test or simple form
            login_response = session.post(f"{BASE_URL}/login", data=login_data, timeout=10)
            
            if login_response.status_code == 200 and ("dashboard" in login_response.url or "dashboard" in login_response.text):
                 print("Login successful.")
            else:
                 print("Login might have failed or redirected elsewhere.")
                 print(f"Login URL: {login_response.url}")
                 # Continue anyway to check /tsrs
            
            # Now access /tsrs again
            response = session.get(f"{BASE_URL}/tsrs", timeout=10)
            
        print(f"/tsrs status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for Mappings Section
            if "TSRS - ESRS Eşleştirmeleri" in content:
                print("[PASS] Mappings section found.")
            else:
                print("[FAIL] Mappings section NOT found.")
                
            # Check for specific mapping data
            if "ESRS 2 GOV-1" in content:
                 print("[PASS] Mapping data 'ESRS 2 GOV-1' found.")
            else:
                 print("[FAIL] Mapping data 'ESRS 2 GOV-1' NOT found.")
                 
            # Check for Indicators
            if "TSRS-1-1" in content:
                 print("[PASS] Indicator 'TSRS-1-1' found.")
            else:
                 print("[FAIL] Indicator 'TSRS-1-1' NOT found.")

        else:
            print(f"Failed to access /tsrs. Status: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_tsrs()
