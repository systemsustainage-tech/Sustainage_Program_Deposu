
import requests
import re

SESSION_COOKIE = "session=.eJwlzsEKgzAMgOFXCTl72E49eJmhO4xF2sE6KnsJ3X1X8fbD9_F_S65jX_fSruW4S-mgl_MAI0oYV51Acl5t5d4iF0Y0hKCNJ0y9p0oZWaX4k3Fw3qJjZ0u-z-10_N7-123_47c6Qe9S4JpQY6hWk44d67yCqB612C5GZ_0BwZwuQA.Z5uj0Q.q56rQ29lM7tYf2J6q56rQ29lM7t" # Example cookie, might need real login

def login_and_get_session():
    # Attempt to login as __super__ to get a valid session
    url = "http://72.62.150.207/login"
    payload = {
        "username": "__super__",
        "password": "Kayra_1507"
    }
    s = requests.Session()
    try:
        r = s.post(url, data=payload, allow_redirects=True)
        if r.status_code == 200 and "Dashboard" in r.text:
            print("[OK] Login successful.")
            return s
        else:
            print(f"[FAIL] Login failed. Status: {r.status_code}")
            # print first 500 chars to see what page we are on
            print(r.text[:500])
            return None
    except Exception as e:
        print(f"[ERROR] Login exception: {e}")
        return None

def verify_sdg_routes(session):
    base_url = "http://72.62.150.207"
    
    # Check /sdg
    print("\nChecking /sdg route...")
    r = session.get(f"{base_url}/sdg")
    if r.status_code == 200:
        print(f"[OK] /sdg returned 200.")
        if "Sürdürülebilir Kalkınma Amaçları" in r.text or "SDG" in r.text:
             print("[OK] Found SDG title/content.")
        else:
             print("[WARN] SDG title not found in response.")
        
        # Check for specific goals
        if "Yoksulluğa Son" in r.text:
            print("[OK] Found 'Yoksulluğa Son' goal.")
        else:
            print("[WARN] 'Yoksulluğa Son' not found.")
    else:
        print(f"[FAIL] /sdg returned {r.status_code}")

    # Check /sdg/add (GET) - assuming it renders a form or redirects
    print("\nChecking /sdg/add route...")
    r = session.get(f"{base_url}/sdg/add")
    if r.status_code == 200:
        print(f"[OK] /sdg/add returned 200.")
    elif r.status_code == 302:
        print(f"[INFO] /sdg/add redirected (likely to list if no ID provided).")
    else:
        print(f"[FAIL] /sdg/add returned {r.status_code}")

if __name__ == "__main__":
    s = login_and_get_session()
    if s:
        verify_sdg_routes(s)
