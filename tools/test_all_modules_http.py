import requests
import sys

# Force stdout flushing
sys.stdout.reconfigure(line_buffering=True)

BASE_URL = "http://72.62.150.207:5000"

MODULES = [
    "/sdg", "/carbon", "/energy", "/esg", "/cbam", "/csrd", "/taxonomy",
    "/waste", "/water", "/biodiversity", "/economic", "/tcfd", "/tnfd",
    "/supply_chain", "/cdp", "/issb", "/iirc", "/esrs", "/gri", "/social", "/governance"
]

def test_login(username, password):
    print(f"\nTesting login for {username}...")
    session = requests.Session()
    try:
        login_data = {
            'username': username,
            'password': password
        }
        
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
        
        if response.status_code == 200:
            if "Dashboard" in response.text or "Hoşgeldiniz" in response.text or "Çıkış Yap" in response.text:
                print(f"SUCCESS: Login successful for {username}")
                return session
            elif "Hatalı kullanıcı adı veya şifre" in response.text:
                print(f"FAILED: Invalid credentials for {username}")
            else:
                # Check for redirect to dashboard
                if "/dashboard" in response.url or "Dashboard" in response.text:
                    print(f"SUCCESS: Login successful (inferred) for {username}")
                    return session
                print(f"WARNING: Login status unclear. Response length: {len(response.text)}")
        else:
            print(f"FAILED: HTTP {response.status_code}")
        
    except Exception as e:
        print(f"ERROR: {e}")
    
    return None

def test_modules(session):
    print("\nTesting Modules...")
    success_count = 0
    failed_modules = []
    
    for module in MODULES:
        try:
            url = f"{BASE_URL}{module}"
            response = session.get(url)
            
            if response.status_code == 200:
                print(f"SUCCESS: {module}")
                success_count += 1
            elif response.status_code == 403:
                print(f"FAILED: {module} (403 Forbidden)")
                failed_modules.append(module)
            elif response.status_code == 404:
                print(f"FAILED: {module} (404 Not Found)")
                failed_modules.append(module)
            elif response.status_code == 500:
                print(f"FAILED: {module} (500 Server Error)")
                failed_modules.append(module)
            else:
                print(f"FAILED: {module} ({response.status_code})")
                failed_modules.append(module)
                
        except Exception as e:
            print(f"ERROR testing {module}: {e}")
            failed_modules.append(module)
            
    print(f"\nSummary: {success_count}/{len(MODULES)} modules accessible.")
    if failed_modules:
        print(f"Failed modules: {', '.join(failed_modules)}")
        return False
    return True

if __name__ == "__main__":
    # Test with __super__
    session = test_login("__super__", "super123")
    if session:
        if test_modules(session):
            print("\nALL MODULES VERIFIED for __super__")
        else:
            print("\nSome modules failed for __super__")
    
    # Test with test_user
    session_user = test_login("test_user", "Test1234!")
    if session_user:
        if test_modules(session_user):
            print("\nALL MODULES VERIFIED for test_user")
        else:
            print("\nSome modules failed for test_user")
