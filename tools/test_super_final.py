import requests
import sys

BASE_URL = "https://sustainage.cloud"
LOGIN_URL = f"{BASE_URL}/login"
ADMIN_USERS_URL = f"{BASE_URL}/users"
USERNAME = "__super__"
PASSWORD = "super123"

def test_super_admin():
    session = requests.Session()
    
    # 1. Login
    print(f"Logging in as {USERNAME}...")
    resp = session.post(LOGIN_URL, data={'username': USERNAME, 'password': PASSWORD})
    if resp.status_code != 200:
        print(f"Login failed. Status: {resp.status_code}")
        return False
    
    if "Giris basarili" not in resp.text and "dashboard" not in resp.url:
         if "/dashboard" in resp.url:
             print("Login successful (redirected).")
         else:
             print("Login failed (content check).")
             return False
    else:
        print("Login successful.")

    # 2. Access Admin Panel (Users)
    print("\n--- Testing Admin Panel Access (/users) ---")
    resp = session.get(ADMIN_USERS_URL)
    if resp.status_code == 200:
        if "Kullanıcı Yönetimi" in resp.text or "Kullanıcılar" in resp.text:
            print("SUCCESS: Admin panel accessible.")
        else:
            print("WARNING: 200 OK but 'Kullanıcı Yönetimi' text not found.")
            # print(resp.text[:500])
    else:
        print(f"FAILED: Admin panel access failed. Status: {resp.status_code}")
        return False

    return True

if __name__ == "__main__":
    if test_super_admin():
        print("\nSuper Admin tests passed!")
        sys.exit(0)
    else:
        print("\nSuper Admin tests failed.")
        sys.exit(1)
