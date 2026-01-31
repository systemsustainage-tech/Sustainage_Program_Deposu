
import requests
import sys

HOST = '72.62.150.207'
BASE_URL = f"http://{HOST}"
LOGIN_URL = f"{BASE_URL}/login"

MODULES = [
    'carbon', 'energy', 'waste', 'water', 'biodiversity',
    'social', 'governance', 'supply_chain', 'economic',
    'esg', 'cbam', 'csrd', 'taxonomy', 'gri', 'sdg',
    'ifrs', 'tcfd', 'tnfd', 'cdp'
]

ADMIN_MODULES = ['users', 'companies', 'reports', 'data']

def test_login(username, password):
    session = requests.Session()
    print(f"\nTesting login for {username}...")
    r = session.get(LOGIN_URL)
    payload = {'username': username, 'password': password}
    r = session.post(LOGIN_URL, data=payload)
    
    if r.url == f"{BASE_URL}/dashboard":
        print("Login SUCCESS.")
        return session
    else:
        print(f"Login FAILED. URL: {r.url}")
        return None

def check_modules(session, username):
    print(f"Checking modules for {username}...")
    for mod in MODULES:
        url = f"{BASE_URL}/{mod}"
        r = session.get(url)
        if r.status_code == 200:
            print(f"[OK] {mod}")
        else:
            print(f"[FAIL] {mod} - Status: {r.status_code}")

    print(f"Checking admin modules for {username}...")
    for mod in ADMIN_MODULES:
        url = f"{BASE_URL}/{mod}"
        r = session.get(url)
        if r.status_code == 200:
            print(f"[OK] {mod}")
        else:
            print(f"[FAIL] {mod} - Status: {r.status_code}")

if __name__ == '__main__':
    # Test test_user
    session_user = test_login('test_user', 'test12345')
    if session_user:
        check_modules(session_user, 'test_user')
    
    # Test __super__
    session_super = test_login('__super__', 'super123')
    if session_super:
        check_modules(session_super, '__super__')
