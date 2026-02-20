import requests
import sys
import re

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGIN_URL = "https://72.62.150.207/login"
DASHBOARD_URL = "https://72.62.150.207/dashboard"

def test_login(username, password):
    print(f"Testing login for {username}...")
    
    session = requests.Session()
    
    # 1. Get Login Page (to get CSRF token if needed, or just check connectivity)
    csrf_token = None
    try:
        r = session.get(LOGIN_URL, verify=False, timeout=10)
        print(f"GET /login: {r.status_code}")
        
        # Extract CSRF Token
        match = re.search(r'<input[^>]*name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']', r.text)
        if match:
            csrf_token = match.group(1)
            print(f"Found CSRF Token: {csrf_token[:10]}...")
        else:
            print("Warning: No CSRF token found in login page.")
            
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # 2. Post Credentials
    headers = {
        'Referer': LOGIN_URL,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    payload = {
        "username": username,
        "password": password,
        "csrf_token": csrf_token
    }
    
    try:
        r = session.post(LOGIN_URL, data=payload, headers=headers, verify=False, allow_redirects=True, timeout=10)
        print(f"POST /login: {r.status_code}")
        print(f"Final URL: {r.url}")
        
        if r.url == DASHBOARD_URL or "/dashboard" in r.url:
            print("SUCCESS: Reached Dashboard!")
        else:
            print("FAILURE: Did not reach Dashboard.")
            if "Hesabınız kilitli" in r.text:
                print("Error: Account Locked.")
            elif "Kullanıcı adı veya parola hatalı" in r.text:
                print("Error: Invalid Credentials.")
            elif "Oturum süreniz doldu" in r.text:
                print("Error: Session Expired / No Company Context.")
            else:
                # Print first 500 chars of response
                print("Response Snippet:", r.text[:500])
                
    except Exception as e:
        print(f"Login request failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        test_login(sys.argv[1], sys.argv[2])
    else:
        test_login("super.admin", "Admin123!")
