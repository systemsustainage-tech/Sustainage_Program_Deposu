import requests
import sys
import datetime

BASE_URL = "http://127.0.0.1:5000"

MODULES = [
    "/sdg", "/carbon", "/energy", "/esg", "/cbam", "/csrd", "/taxonomy",
    "/waste", "/water", "/biodiversity", "/economic", "/tcfd", "/tnfd",
    "/supply_chain", "/cdp", "/issb", "/iirc", "/esrs", "/gri", "/social", "/governance"
]

def log(msg):
    print(msg)

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
    print("\n=== TEST USER ===")
    session = test_login("test_user", "Test1234!")
    if session:
        test_modules(session)
    else:
        log("Cannot proceed with module testing due to login failure.")

    print("\n=== SUPER ADMIN ===")
    session_super = test_login("__super__", "super123")
    if session_super:
        log("Super admin login success.")
        # Check Audit Logs
        log("\n--- Checking Audit Logs Visibility ---")
        try:
            resp = session_super.get(f"{BASE_URL}/super_admin/audit_logs")
            if resp.status_code == 200:
                if "TEST_LOG_ENTRY" in resp.text:
                    log("SUCCESS: Found TEST_LOG_ENTRY in audit logs page.")
                else:
                    log("WARNING: TEST_LOG_ENTRY not found in audit logs page.")
                
                if "LOGIN_SUCCESS_WEB" in resp.text:
                    log("SUCCESS: Found LOGIN_SUCCESS_WEB (security log) in audit logs page.")
                else:
                    log("WARNING: LOGIN_SUCCESS_WEB not found in audit logs page.")
            else:
                log(f"FAILED: Fetching audit logs returned {resp.status_code}")
        except Exception as e:
            log(f"ERROR checking audit logs: {e}")
    else:
        log("Super admin login failed.")
