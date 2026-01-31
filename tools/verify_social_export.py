import requests
import sys

BASE_URL = 'http://72.62.150.207:5000'
LOGIN_URL = f'{BASE_URL}/login'
EXPORT_URL = f'{BASE_URL}/social/export'

# Use the super user credentials from memory
USERNAME = '__super__'
PASSWORD = 'Kayra_1507'

def check_export():
    session = requests.Session()
    
    # 1. Login
    print(f"Logging in as {USERNAME}...", flush=True)
    try:
        r = session.get(LOGIN_URL, timeout=10)
        
        login_data = {
            'username': USERNAME,
            'password': PASSWORD
        }
        
        r = session.post(LOGIN_URL, data=login_data, timeout=10)
        print(f"Login Response Code: {r.status_code}", flush=True)
        
        # 2. Request Export
        print(f"Requesting {EXPORT_URL}...", flush=True)
        r = session.get(EXPORT_URL, timeout=30)
        
        if r.status_code == 200:
            content_type = r.headers.get('Content-Type', '')
            print(f"Status Code: {r.status_code}", flush=True)
            print(f"Content-Type: {content_type}", flush=True)
            print(f"Content-Length: {r.headers.get('Content-Length')}", flush=True)
            
            if 'spreadsheet' in content_type or 'excel' in content_type:
                print("SUCCESS: Received Excel file.", flush=True)
                return True
            else:
                print("FAILURE: Did not receive Excel file.", flush=True)
                return False
        else:
            print(f"FAILURE: Status Code {r.status_code}", flush=True)
            print(r.text[:200], flush=True)
            return False

    except Exception as e:
        print(f"Error: {e}", flush=True)
        return False

if __name__ == "__main__":
    check_export()
