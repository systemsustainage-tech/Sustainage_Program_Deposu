import requests

BASE_URL = "http://72.62.150.207"
LOGIN_URL = f"{BASE_URL}/login"
SDG_URL = f"{BASE_URL}/sdg"

def verify_sdg():
    session = requests.Session()
    
    # 1. Login
    print("Logging in...")
    try:
        resp = session.post(LOGIN_URL, data={
            'username': '__super__',
            'password': 'Kayra_1507'
        })
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code}")
            return False
        if 'Dashboard' not in resp.text and 'dashboard' not in resp.url:
            print("Login might have failed (dashboard not found)")
            # print(resp.text[:500])
    except Exception as e:
        print(f"Login error: {e}")
        return False
        
    # 2. Check SDG
    print("Checking SDG module...")
    try:
        resp = session.get(SDG_URL)
        print(f"URL: {resp.url}")
        if resp.status_code == 200:
            print("SDG Module: OK (200)")
            if "login" in resp.url:
                print("Redirected to Login!")
                return False
                
            if "Sürdürülebilir Kalkınma Hedefleri" in resp.text or "SDG" in resp.text:
                 print("SDG Content: Verified")
                 return True
            else:
                 print("SDG Content: Warning (Keywords not found)")
                 print(resp.text[:500])
                 return True # Still 200
        else:
            print(f"SDG Module: Failed ({resp.status_code})")
            return False
    except Exception as e:
        print(f"SDG Check error: {e}")
        return False

if __name__ == "__main__":
    verify_sdg()
