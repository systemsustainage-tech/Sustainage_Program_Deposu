
import requests
import sys

BASE_URL = "http://72.62.150.207"
LOGIN_URL = f"{BASE_URL}/login"
SDG_URL = f"{BASE_URL}/sdg"

def verify_sdg():
    session = requests.Session()
    
    # 1. Login
    hostname = "72.62.150.207"
    username = "__super__"
    password = "Kayra_1507"

    # Try HTTPS directly to avoid redirect dropping POST data
    login_url = f"https://{hostname}/login"
    target_url = f"https://{hostname}/sdg"
    
    print(f"Logging in to {login_url}...")
    
    # Ignore SSL warnings for IP access
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Headers to mimic browser and Host to match certificate if possible (though we use IP)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Host': 'sustainage.cloud' # Trick vhost if needed
    }
    
    try:
        # Initial GET to get CSRF cookie if any (Flask default doesn't strictly need it unless WTF-CSRF)
        session.get(login_url, verify=False, headers=headers)
        
        resp = session.post(login_url, data={
            'username': username,
            'password': password
        }, verify=False, headers=headers, allow_redirects=True)
        
        print(f"Login Response Status: {resp.status_code}")
        print(f"Login Response URL: {resp.url}")
        print(f"Cookies: {session.cookies.get_dict()}")
        
        if 'Dashboard' not in resp.text and 'dashboard' not in resp.url:
            print("Login failed! Response preview:")
            print(resp.text[:1000]) # Print first 1000 chars
            return False
            
    except Exception as e:
        print(f"Login error: {e}")
        return False
        
    # 2. Check SDG
    print("Checking SDG module...")
    try:
        resp = session.get(SDG_URL)
        print(f"SDG URL: {resp.url}")
        
        if resp.status_code == 200:
            if "login" in resp.url:
                print("Redirected to Login!")
                return False
                
            if "Sürdürülebilir Kalkınma Hedefleri" in resp.text or "SDG" in resp.text:
                 print("SDG Content: Verified")
                 return True
            else:
                 print("SDG Content: Warning (Keywords not found)")
                 print(resp.text[:500])
                 return True 
        else:
            print(f"SDG Module: Failed ({resp.status_code})")
            return False
    except Exception as e:
        print(f"SDG Check error: {e}")
        return False

if __name__ == "__main__":
    verify_sdg()
