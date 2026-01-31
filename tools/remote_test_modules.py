import urllib.request
import urllib.parse
import http.cookiejar
import sys

BASE_URL = "https://sustainage.cloud"

MODULES = [
    "/sdg", "/carbon", "/energy", "/esg", "/cbam", "/csrd", "/taxonomy",
    "/waste", "/water", "/biodiversity", "/economic", "/tcfd", "/tnfd",
    "/supply_chain", "/cdp", "/issb", "/iirc", "/esrs", "/gri", "/social", "/governance"
]

def test_login(opener, username, password):
    print(f"\nTesting login for {username}...")
    login_url = f"{BASE_URL}/login"
    
    # Enable cookie handling
    
    data = urllib.parse.urlencode({
        'username': username,
        'password': password
    }).encode('utf-8')
    
    try:
        response = opener.open(login_url, data=data)
        content = response.read().decode('utf-8')
        
        if "Dashboard" in content or "Hoşgeldiniz" in content or "Çıkış Yap" in content:
            print(f"SUCCESS: Login successful for {username}")
            return True
        elif "Hatalı kullanıcı adı veya şifre" in content:
            print(f"FAILED: Invalid credentials for {username}")
        else:
            # Check redirect URL if possible (urllib handles redirects automatically)
            if "/dashboard" in response.geturl():
                print(f"SUCCESS: Login successful (redirected) for {username}")
                return True
            print(f"WARNING: Login status unclear. URL: {response.geturl()}")
            
    except Exception as e:
        print(f"ERROR login: {e}")
        
    return False

def test_modules(opener):
    print("\nTesting Modules (login session)...")
    success_count = 0
    failed_modules = []
    
    for module in MODULES:
        try:
            url = f"{BASE_URL}{module}"
            response = opener.open(url)
            code = response.getcode()
            
            if code == 200:
                print(f"SUCCESS: {module}")
                success_count += 1
            else:
                print(f"FAILED: {module} ({code})")
                failed_modules.append(module)
                
        except urllib.error.HTTPError as e:
            print(f"FAILED: {module} ({e.code})")
            failed_modules.append(module)
        except Exception as e:
            print(f"ERROR testing {module}: {e}")
            failed_modules.append(module)
            
    print(f"\nSummary (with login): {success_count}/{len(MODULES)} modules accessible.")
    if failed_modules:
        print(f"Failed modules (with login): {', '.join(failed_modules)}")
        return False
    return True


def test_modules_no_login():
    print("\nTesting Modules WITHOUT login (basic availability)...")
    success_count = 0
    failed = []
    for module in MODULES:
        url = f"{BASE_URL}{module}"
        try:
            resp = urllib.request.urlopen(url)
            code = resp.getcode()
            # 200 OK or 3xx redirect are fine here, we only care about 5xx errors
            if 500 <= code < 600:
                print(f"FAILED (server error): {module} ({code})")
                failed.append(module)
            else:
                print(f"OK: {module} ({code}) -> {resp.geturl()}")
                success_count += 1
        except urllib.error.HTTPError as e:
            if 500 <= e.code < 600:
                print(f"FAILED (HTTP {e.code}): {module}")
                failed.append(module)
            else:
                print(f"OK (HTTP {e.code}): {module} (likely auth/redirect)")
                success_count += 1
        except Exception as e:
            print(f"ERROR accessing {module}: {e}")
            failed.append(module)

    print(f"\nSummary (no login): {success_count}/{len(MODULES)} modules reachable without server error.")
    if failed:
        print(f"Modules with errors: {', '.join(failed)}")

if __name__ == "__main__":
    # 1) Basic availability check without login (detect 5xx errors like 502)
    test_modules_no_login()

    # 2) Optional: login-based checks (may fail if credentials or CSRF change)
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    if test_login(opener, "__super__", "super123"):
        test_modules(opener)

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    if test_login(opener, "test_user", "Test1234!"):
        test_modules(opener)
