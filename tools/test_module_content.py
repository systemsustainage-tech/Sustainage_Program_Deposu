import requests
import sys

BASE_URL = "https://sustainage.cloud"

MODULES = {
    "/sdg": "SDG",
    "/carbon": "Carbon",
    "/energy": "Energy",
    "/esg": "ESG",
    "/cbam": "CBAM",
    "/csrd": "CSRD",
    "/taxonomy": "Taxonomy",
    "/waste": "Waste",
    "/water": "Water",
    "/biodiversity": "Biodiversity",
    "/economic": "Economic",
    "/tcfd": "TCFD",
    "/tnfd": "TNFD",
    "/supply_chain": "Supply Chain",
    "/cdp": "CDP",
    "/issb": "ISSB",
    "/iirc": "IIRC",
    "/esrs": "ESRS",
    "/gri": "GRI",
    "/social": "Social",
    "/governance": "Governance"
}

def test_modules_content():
    print("Logging in as test_user...")
    session = requests.Session()
    try:
        login_resp = session.post(f"{BASE_URL}/login", data={'username': 'test_user', 'password': 'password123'})
        if login_resp.status_code != 200 or "Dashboard" not in login_resp.text:
             # Check if redirected to dashboard
             if "/dashboard" not in login_resp.url:
                 print("Login failed or not redirected to dashboard.")
                 print(f"Status: {login_resp.status_code}, URL: {login_resp.url}")
                 return

        print("Login successful. Checking modules...")
        
        success_count = 0
        for url_path, keyword in MODULES.items():
            full_url = f"{BASE_URL}{url_path}"
            resp = session.get(full_url)
            
            if resp.status_code == 200:
                # Case insensitive check
                if keyword.lower() in resp.text.lower():
                    print(f"[OK] {url_path} (Contains '{keyword}')")
                    success_count += 1
                else:
                    print(f"[WARN] {url_path} (200 OK but keyword '{keyword}' not found)")
                    # Print snippet
                    print(f"    Snippet: {resp.text[:100].replace(chr(10), ' ')}...")
                    success_count += 1 # Counting as success for access, but warn on content
            else:
                print(f"[FAIL] {url_path} (Status: {resp.status_code})")
                
        print(f"\nTotal Accessible: {success_count}/{len(MODULES)}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_modules_content()
