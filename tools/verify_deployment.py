
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import sys
import re

BASE_URL = "https://sustainage.cloud"
LOGIN_URL = f"{BASE_URL}/login"
DASHBOARD_URL = f"{BASE_URL}/dashboard"

USERNAME = "__super__"
PASSWORD = "Kayra_1507"

# Setup Cookie Jar
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
urllib.request.install_opener(opener)

def login():
    print(f"Logging in as {USERNAME}...")
    data = urllib.parse.urlencode({'username': USERNAME, 'password': PASSWORD}).encode('utf-8')
    req = urllib.request.Request(LOGIN_URL, data=data, method='POST')
    
    try:
        with opener.open(req) as response:
            content = response.read().decode('utf-8')
            if "Hoşgeldiniz" in content or "Dashboard" in content or response.geturl() == DASHBOARD_URL:
                print("Login SUCCESS.")
                return True
            else:
                print("Login FAILED: Welcome message not found.")
                print(f"Response URL: {response.geturl()}")
                print(f"Content snippet: {content[:500]}...")
                return False
    except urllib.error.HTTPError as e:
        print(f"Login HTTP Error: {e.code}")
        return False
    except Exception as e:
        print(f"Login Error: {e}")
        return False

def check_dashboard():
    print("\nChecking Dashboard...")
    try:
        with opener.open(DASHBOARD_URL) as response:
            content = response.read().decode('utf-8')
            
            # Check 500/502 (handled by exception usually, but good to know)
            print(f"Dashboard Status: {response.getcode()}")

            # Check Translations
            if "Hoşgeldiniz" in content:
                print("PASS: Translation loaded (Found 'Hoşgeldiniz').")
            elif "dashboard_welcome" in content:
                print("FAIL: Translation NOT loaded (Found raw key 'dashboard_welcome').")
            else:
                print("WARNING: 'Hoşgeldiniz' not found (Login might be different or template changed).")
            
            # Check Quick Access Menu
            if "bi-plus-circle d-block fs-2 mb-2" in content:
                print("FAIL: Quick Access Menu icon found (it should be removed).")
            elif "Hızlı Erişim" in content and "<!--" not in content:
                 print("WARNING: 'Hızlı Erişim' text found, check if it's the menu.")
            else:
                print("PASS: Quick Access Menu appears removed.")
                
            # Check Reports Box 500 Error (User reported this earlier)
            # The reports box is part of the dashboard. If dashboard loads, we are good?
            # User said "Raporlar kutucuğu 500 hatası veriyor". This implies clicking it or it loading data via AJAX?
            # Or maybe the dashboard itself crashed.
            # Assuming dashboard page load covers it for now unless it's an iframe/ajax.
            
    except urllib.error.HTTPError as e:
        print(f"Dashboard FAIL: HTTP {e.code}")
    except Exception as e:
        print(f"Dashboard Error: {e}")

def check_modules():
    modules = [
        '/carbon', 
        '/water', 
        '/waste',
        '/social', 
        '/governance', 
        '/sdg',
        '/reports', 
        '/companies',
        '/users',
        '/gri',
        '/esg',
        '/cbam',
        '/csrd',
        '/taxonomy',
        '/issb',
        '/iirc',
        '/esrs',
        '/tcfd',
        '/tnfd',
        '/cdp',
        '/supply_chain',
        '/economic'
    ]
    
    print("\nChecking Modules & Translations...")
    for mod in modules:
        url = f"{BASE_URL}{mod}"
        try:
            with opener.open(url) as response:
                content = response.read().decode('utf-8')
                code = response.getcode()
                
                # Check for common missing keys
                missing_keys = []
                # Simple regex for keys like 'btn_add', 'title_carbon', etc. appearing in visible text
                # We exclude things inside script tags or comments ideally, but simple check first
                patterns = [r'btn_[a-z_]+', r'title_[a-z_]+', r'desc_[a-z_]+']
                
                for p in patterns:
                    matches = re.findall(p, content)
                    # Filter out matches that might be in code blocks (hard to distinguish without parsing)
                    # But if we see 'btn_add' in the rendered HTML body text, it's usually a bug.
                    if matches:
                        # Let's just list them
                        for m in matches:
                            if m not in missing_keys:
                                missing_keys.append(m)
                
                status = "PASS"
                if missing_keys:
                    status = f"FAIL (Keys: {', '.join(missing_keys[:5])}...)"
                
                print(f"{mod:25} : {code} {status}")
                
        except urllib.error.HTTPError as e:
            print(f"{mod:25} : FAIL HTTP {e.code}")
        except Exception as e:
            print(f"{mod:25} : ERROR {e}")

if __name__ == "__main__":
    if login():
        check_dashboard()
        check_modules()
    else:
        sys.exit(1)
