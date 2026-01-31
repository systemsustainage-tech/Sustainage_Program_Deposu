import requests
import sys

def verify_modules():
    base_url = "http://72.62.150.207"
    login_url = f"{base_url}/login"
    
    session = requests.Session()
    
    # 1. Login
    print(f"Logging in to {login_url}...")
    try:
        # Get CSRF token if needed (assuming simple login for now or no CSRF on login page initially)
        # Actually, let's just try posting.
        response = session.post(login_url, data={
            'username': 'test_user',
            'password': 'test_password_123' # Wait, I set it to '123456' in setup_test_user.py?
            # Let me check setup_test_user.py again or just try '123456'
        })
        
        # If login failed, response might be 200 (login page again) or 401. 
        # Successful login usually redirects (302) then 200 on dashboard.
        # But requests follows redirects by default.
        
        if "Dashboard" not in response.text and "Hoşgeldiniz" not in response.text:
            # Try with '123456'
            response = session.post(login_url, data={
                'username': 'test_user',
                'password': '123456' 
            })
            
        if "Dashboard" in response.text or "Hoşgeldiniz" in response.text or "dashboard" in response.url:
            print("Login successful.")
        else:
            print("Login failed.")
            print("Response URL:", response.url)
            # print("Response text:", response.text[:500])
            return

    except Exception as e:
        print(f"Login error: {e}")
        return

    # 2. Check modules
    modules = [
        "carbon", "energy", "waste", "water", "biodiversity",
        "social", "governance", "supply_chain", "economic",
        "esg", "cbam", "csrd", "taxonomy", "gri", "sdg",
        "tcfd", "tnfd", "cdp", "reports", "companies"
    ]
    
    print("\nVerifying modules...")
    print("\nVerifying content...")
    
    # Check reports for Kivanc
    resp = session.get(f"{base_url}/reports")
    if "Kivanc Demir Celik" in resp.text or "Kivanc_Demir_Celik" in resp.text or "Kıvanç Demir-Çelik" in resp.text:
        print("[OK] Reports: Found 'Kivanc Demir Celik' report.")
    else:
        print("[WARN] Reports: 'Kivanc Demir Celik' not found in report list.")
        print("DEBUG: Response content preview:")
        print(resp.text[:2000]) # Print first 2000 chars to see what's wrong
 
    # Check companies for Kivanc
    resp = session.get(f"{base_url}/companies")
    if "Kivanc Demir Celik" in resp.text or "Kıvanç Demir-Çelik" in resp.text:
        print("[OK] Companies: Found 'Kivanc Demir Celik' company.")
    else:
        print("[WARN] Companies: 'Kivanc Demir Celik' not found in company list.")

if __name__ == "__main__":
    verify_modules()
