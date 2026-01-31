import requests
import sys
import datetime

BASE_URL = "http://72.62.150.207:5000"
LOG_FILE = "test_report.txt"

MODULES = [
    "/sdg", "/carbon", "/energy", "/esg", "/cbam", "/csrd", "/taxonomy",
    "/waste", "/water", "/biodiversity", "/economic", "/tcfd", "/tnfd",
    "/supply_chain", "/cdp", "/issb", "/iirc", "/esrs", "/gri", "/social", "/governance"
]

def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def test_login(username, password):
    log(f"\n--- Testing login for {username} ---")
    session = requests.Session()
    try:
        login_data = {'username': username, 'password': password}
        response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
        
        if response.status_code == 200:
            if "Dashboard" in response.text or "Hoşgeldiniz" in response.text or "Çıkış Yap" in response.text:
                log(f"SUCCESS: Login successful for {username}")
                return session
            elif "Hatalı kullanıcı adı veya şifre" in response.text:
                log(f"FAILED: Invalid credentials for {username}")
            else:
                if "/dashboard" in response.url:
                    log(f"SUCCESS: Login successful (redirected) for {username}")
                    return session
                log(f"WARNING: Login status unclear. URL: {response.url}")
        else:
            log(f"FAILED: HTTP {response.status_code}")
            
    except Exception as e:
        log(f"ERROR: {e}")
    
    return None

def test_modules(session):
    log("\n--- Testing Modules ---")
    success_count = 0
    failed_modules = []
    
    for module in MODULES:
        try:
            url = f"{BASE_URL}{module}"
            response = session.get(url)
            
            if response.status_code == 200:
                log(f"SUCCESS: {module}")
                success_count += 1
            elif response.status_code == 302:
                 # Redirect might mean login required or something else
                 log(f"REDIRECT: {module} -> {response.headers.get('Location')}")
                 failed_modules.append(module)
            elif response.status_code == 403:
                log(f"FAILED: {module} (403 Forbidden)")
                failed_modules.append(module)
            elif response.status_code == 404:
                log(f"FAILED: {module} (404 Not Found)")
                failed_modules.append(module)
            elif response.status_code == 500:
                log(f"FAILED: {module} (500 Server Error)")
                failed_modules.append(module)
            else:
                log(f"FAILED: {module} ({response.status_code})")
                failed_modules.append(module)
                
        except Exception as e:
            log(f"ERROR testing {module}: {e}")
            failed_modules.append(module)
            
    log(f"\nSummary: {success_count}/{len(MODULES)} modules accessible.")
    if failed_modules:
        log(f"Failed modules: {', '.join(failed_modules)}")
        return False
    return True

if __name__ == "__main__":
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"Test Run at {datetime.datetime.now()}\n")
        
    session = test_login("test_user", "Test1234!")
    if session:
        test_modules(session)
    else:
        log("Cannot proceed with module testing due to login failure.")
