
import requests
import sys

HOST = '72.62.150.207'
LOGIN_URL = f"http://{HOST}/login"
DASHBOARD_URL = f"http://{HOST}/dashboard"
CARBON_URL = f"http://{HOST}/carbon"

USERNAME = 'test_user'
PASSWORD = 'test12345'

def test_user_login():
    session = requests.Session()
    
    # Login
    print("Logging in as test_user...")
    r = session.get(LOGIN_URL)
    payload = {'username': USERNAME, 'password': PASSWORD}
    r = session.post(LOGIN_URL, data=payload)
    
    if r.url == DASHBOARD_URL:
        print("Login SUCCESS. Redirected to dashboard.")
    else:
        print(f"Login FAILED. URL: {r.url}")
        return

    # Check Dashboard content
    if "Hızlı Erişim" in r.text or "Modüller" in r.text:
        print("Dashboard loaded correctly.")
    else:
        print("Dashboard loaded but content suspicious.")

    # Check Module Access
    print("Checking Carbon module access...")
    r = session.get(CARBON_URL)
    if r.status_code == 200:
        print("Carbon module ACCESS GRANTED.")
    else:
        print(f"Carbon module ACCESS DENIED. Status: {r.status_code}")

if __name__ == '__main__':
    test_user_login()
