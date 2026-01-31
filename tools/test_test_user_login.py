import requests
import sys

BASE_URL = "https://sustainage.cloud"

def test_login(username, password):
    print(f"Testing login for {username}...")
    session = requests.Session()
    try:
        login_data = {
            'username': username,
            'password': password
        }
        
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
        print(f"Status Code: {response.status_code}")
        print(f"URL: {response.url}")
        
        if response.status_code == 200:
            if "Dashboard" in response.text or "Hoşgeldiniz" in response.text or "Çıkış Yap" in response.text:
                print(f"SUCCESS: Login successful for {username}")
                return session
            elif "Hatalı kullanıcı adı veya şifre" in response.text:
                print(f"FAILED: Invalid credentials for {username}")
            else:
                if "/dashboard" in response.url:
                     print(f"SUCCESS: Login successful (redirected to dashboard) for {username}")
                else:
                    print(f"WARNING: Login status unclear.")
                    print(f"Page Title: {response.text.split('<title>')[1].split('</title>')[0] if '<title>' in response.text else 'No Title'}")
        else:
            print(f"FAILED: HTTP {response.status_code}")
            print(response.text[:200])
        
    except Exception as e:
        print(f"ERROR: {e}")
    
    return None

if __name__ == "__main__":
    test_login('test_user', 'password123')
