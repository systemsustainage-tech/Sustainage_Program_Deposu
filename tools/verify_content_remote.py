import requests
import urllib3
import sys

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://72.62.150.207"
LOGIN_URL = f"{BASE_URL}/login"
USERNAME = "__super__"
PASSWORD = "Kayra_1507"

def verify_content():
    session = requests.Session()
    print("Logging in...")
    try:
        r = session.post(LOGIN_URL, data={'username': USERNAME, 'password': PASSWORD}, verify=False, allow_redirects=True)
        if r.status_code == 200 and ('Dashboard' in r.text or 'Gösterge Paneli' in r.text or '/logout' in r.text):
            print(f"Login Successful (Redirected to {r.url})")
        else:
            print(f"Login Failed. Status: {r.status_code}")
            return

        # Check /iirc
        print("\nChecking /iirc...")
        r = session.get(f"{BASE_URL}/iirc", verify=False)
        if r.status_code == 200:
            print("[OK] /iirc loaded.")
            if "Entegre Raporlar" in r.text:
                 print("   Content verified: 'Entegre Raporlar' found.")
            else:
                 print("   WARNING: 'Entegre Raporlar' NOT found in content.")
        else:
            print(f"[FAIL] /iirc returned {r.status_code}")

        # Check /targets
        print("\nChecking /targets...")
        r = session.get(f"{BASE_URL}/targets", verify=False)
        if r.status_code == 200:
            print("[OK] /targets loaded.")
            if "Hedef Takibi" in r.text:
                print("   Content verified: 'Hedef Takibi' found.")
            else:
                print("   WARNING: 'Hedef Takibi' NOT found in content.")
        else:
             print(f"[FAIL] /targets returned {r.status_code}")

        # Check /prioritization
        print("\nChecking /prioritization...")
        r = session.get(f"{BASE_URL}/prioritization", verify=False)
        if r.status_code == 200:
             print("[OK] /prioritization loaded.")
        else:
             print(f"[FAIL] /prioritization returned {r.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_content()
