import requests
import sys

BASE_URL = "http://127.0.0.1:5000"

MODULES = [
    '/sdg',
    '/gri',
    '/carbon',
    '/energy',
    '/water',
    '/waste',
    '/biodiversity',
    '/social',
    '/governance',
    '/supply_chain',
    '/economic',
    '/esg',
    '/cbam',
    '/csrd',
    '/taxonomy',
    '/issb',
    '/iirc',
    '/esrs',
    '/tcfd',
    '/tnfd',
    '/cdp'
]

def check_routes():
    print(f"Checking routes on {BASE_URL}...")
    
    results = {'ok': [], 'missing': [], 'error': []}
    
    # Check root
    try:
        r = requests.get(BASE_URL, allow_redirects=False)
        print(f"/ -> {r.status_code}")
    except Exception as e:
        print(f"Failed to connect to root: {e}")
        return

    for mod in MODULES:
        url = f"{BASE_URL}{mod}"
        try:
            # We expect a redirect to login (302) or success (200) if public (unlikely)
            # If 404, it's missing.
            r = requests.get(url, allow_redirects=False)
            status = r.status_code
            
            if status == 404:
                results['missing'].append(mod)
                print(f"[MISSING] {mod} -> 404")
            elif status == 500:
                results['error'].append(mod)
                print(f"[ERROR] {mod} -> 500")
            elif status in [200, 302]:
                results['ok'].append(mod)
                print(f"[OK] {mod} -> {status}")
            else:
                print(f"[?] {mod} -> {status}")
                results['ok'].append(mod) # Assume other codes are handled routes
                
        except Exception as e:
            print(f"[EXCEPTION] {mod} -> {e}")
            results['error'].append(mod)

    print("\nSummary:")
    print(f"OK: {len(results['ok'])}")
    print(f"Missing: {len(results['missing'])}")
    print(f"Error: {len(results['error'])}")
    
    if results['missing']:
        print("\nMissing Modules:")
        for m in results['missing']:
            print(m)
            
    if results['error']:
        print("\nErrored Modules:")
        for m in results['error']:
            print(m)

if __name__ == "__main__":
    check_routes()
