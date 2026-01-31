import requests
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://72.62.150.207"
SUPPLIER_LOGIN_URL = f"{BASE_URL}/supplier_portal/login"

def check_supplier_portal():
    print(f"Checking Supplier Portal at {SUPPLIER_LOGIN_URL}...")
    try:
        response = requests.get(SUPPLIER_LOGIN_URL, verify=False, timeout=10)
        if response.status_code == 200:
            if "Tedarikçi Portalı Girişi" in response.text:
                print("Supplier Portal Login Page: SUCCESS (Found 'Tedarikçi Portalı Girişi')")
                return True
            else:
                print("Supplier Portal Login Page: WARNING (Status 200 but text not found)")
                print(f"Content preview: {response.text[:200]}")
                return False
        else:
            print(f"Supplier Portal Login Page: FAILED (Status {response.status_code})")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    check_supplier_portal()
