import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

PATHS = [
    '/',
    '/login',
    '/dashboard',
    '/training',
    '/biodiversity',
    '/economic',
    '/social',
    '/governance',
    '/waste',
    '/water',
    '/carbon',
    '/esg',
    '/benchmark',
    '/regulation',
    '/supply_chain',
    '/human_rights',
    '/labor',
    '/environment',
    '/fair_operating',
    '/consumer',
    '/community'
]

def check_routes():
    print(f"Checking routes on {BASE_URL}...")
    try:
        # Check if server is up first
        requests.get(BASE_URL)
    except Exception as e:
        print(f"CRITICAL: Cannot connect to {BASE_URL}. Is the service running?")
        print(e)
        sys.exit(1)

    passed = 0
    failed = 0
    
    for path in PATHS:
        url = f"{BASE_URL}{path}"
        try:
            r = requests.get(url, allow_redirects=False)
            status = r.status_code
            
            # 200 is OK (public page like login)
            # 302 is OK (redirect to login, means route exists and is protected)
            if status in [200, 302]:
                print(f"[OK] {path} -> {status}")
                passed += 1
            else:
                print(f"[FAIL] {path} -> {status}")
                failed += 1
        except Exception as e:
            print(f"[ERR] {path} -> {e}")
            failed += 1
            
    print("-" * 30)
    print(f"Total: {len(PATHS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    check_routes()
