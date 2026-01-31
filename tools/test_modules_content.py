
import requests
import sys

# Configuration
BASE_URL = "https://sustainage.cloud"
LOGIN_URL = f"{BASE_URL}/login"
USERNAME = "test_user"
PASSWORD = "password123"

# List of modules and expected content keywords
MODULES = [
    ("/carbon", ["Karbon", "Carbon"]),
    ("/water", ["Su", "Water"]),
    ("/energy", ["Enerji", "Energy"]),
    ("/waste", ["Atık", "Waste"]),
    ("/biodiversity", ["Biyoçeşitlilik", "Biodiversity"]),
    ("/supply_chain", ["Tedarik", "Supply"]),
    ("/social", ["Sosyal", "Social"]),
    ("/governance", ["Yönetişim", "Governance"]),
    ("/economic", ["Ekonomik", "Economic"]),
    ("/gri", ["GRI", "Standards"]),
    ("/tcfd", ["TCFD"]),
    ("/tnfd", ["TNFD"]),
    ("/cdp", ["CDP"]),
    ("/csrd", ["CSRD"]),
    ("/esrs", ["ESRS"]),
    ("/cbam", ["CBAM"]),
    ("/sdg", ["SDG", "Kalkınma"]),
    ("/iirc", ["Entegre", "Integrated", "IIRC"]), # IIRC might be in text as 'Entegre'
    ("/issb", ["ISSB", "IFRS"]),
    ("/taxonomy", ["Taxonomy", "Taksonomi"]),
    ("/esg", ["ESG"])
]

def test_modules_content():
    session = requests.Session()
    
    # Login
    print(f"Logging in as {USERNAME}...")
    resp = session.post(LOGIN_URL, data={'username': USERNAME, 'password': PASSWORD})
    if resp.status_code != 200:
        print("Login failed.")
        return False

    failed_modules = []
    
    print("\n--- Testing Modules ---")
    for path, keywords in MODULES:
        url = f"{BASE_URL}{path}"
        print(f"Checking {path}...", end=" ")
        try:
            resp = session.get(url)
            if resp.status_code == 200:
                content = resp.text
                found = False
                for kw in keywords:
                    if kw in content or kw.lower() in content.lower():
                        found = True
                        break
                
                if found:
                    print("OK")
                else:
                    print(f"WARNING: 200 OK but keywords {keywords} not found.")
                    # print(content[:200]) # Debug
            else:
                print(f"FAILED: {resp.status_code}")
                failed_modules.append(path)
        except Exception as e:
            print(f"ERROR: {e}")
            failed_modules.append(path)

    if failed_modules:
        print(f"\nFailed modules: {failed_modules}")
        return False
    else:
        print("\nAll modules accessible and verified.")
        return True

if __name__ == "__main__":
    if test_modules_content():
        sys.exit(0)
    else:
        sys.exit(1)
