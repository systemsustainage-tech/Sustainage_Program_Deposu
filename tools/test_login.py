import requests
import logging
import sys
import re
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://72.62.150.207"
LOGIN_URL = f"{BASE_URL}/login"
USERNAME = "super.admin"
PASSWORD = "SuperPassword123!"

session = requests.Session()

def test_login():
    print(f"Testing login for {USERNAME} at {LOGIN_URL}")
    
    # 1. Get Login Page for CSRF
    response = session.get(LOGIN_URL, verify=False)
    print(f"GET Status: {response.status_code}")
    
    csrf_token = None
    match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
    if match:
        csrf_token = match.group(1)
        print(f"CSRF Token: {csrf_token}")
    else:
        print("CSRF Token NOT found")
        return False
        
    # 2. Post Credentials
    data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrf_token': csrf_token
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': LOGIN_URL
    }
    
    print("Posting login data...")
    response = session.post(LOGIN_URL, data=data, verify=False, headers=headers)
    print(f"POST Status: {response.status_code}")
    print(f"Final URL: {response.url}")
    
    if "dashboard" in response.url or "Hoşgeldiniz" in response.text:
        print("Login SUCCESS!")
        return True
    else:
        print("Login FAILED!")
        if "Kullanıcı adı veya parola hatalı" in response.text:
            print("Reason: Invalid credentials message found.")
        else:
            print("Reason: Unknown.")
            print("Response preview:")
            print(response.text[:500])
        return False

if __name__ == "__main__":
    test_login()
