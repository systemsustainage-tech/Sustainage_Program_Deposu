
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5003"
LOGIN_URL = f"{BASE_URL}/login"
SDG_ADD_URL = f"{BASE_URL}/sdg/add"

def test_sdg():
    session = requests.Session()
    
    # Login
    print("Logging in...")
    resp = session.post(LOGIN_URL, data={'username': 'admin', 'password': 'Admin_2025!'})
    print(f"Login Status: {resp.status_code}")
    print(f"Login History: {resp.history}")
    print(f"Login URL: {resp.url}")
    
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code}")
        # print(resp.text)
        return
    
    # Check if login successful (usually redirects to dashboard or returns 200)
    # Use a more specific check to avoid matching "Giriş Yapıldı" in dashboard activity log
    if '<h3 class="card-title text-center mb-4">Giriş Yap</h3>' in resp.text:
        print("Login failed (Login page title found)")
        return
        
    if 'Dashboard' not in resp.text:
        print("Login failed (Dashboard text not found)")
        return
        
    print("Login successful")

    # Add SDG Data
    print("Adding SDG data...")
    ts = int(time.time())
    action = f"Action-{ts}"
    data = {
        'year': '2024',
        'goal_id': '1', 
        'indicator_id': '1',
        'target': f"Target {ts}",
        'action': action,
        'status': 'Devam Ediyor',
        'progress_pct': '50'
    }
    
    resp = session.post(SDG_ADD_URL, data=data)
    print(f"Add response: {resp.status_code}")
    
    if resp.status_code == 200 or resp.status_code == 302:
        print("SDG Add Request sent successfully")
    else:
        print(f"SDG Add Request failed: {resp.text}")

    # Verify Data Display
    print("Verifying data display on SDG page...")
    resp = session.get(f"{BASE_URL}/sdg")
    if resp.status_code == 200:
        if action in resp.text:
            print(f"SUCCESS: Found action '{action}' in SDG page.")
        else:
            print(f"FAILURE: Action '{action}' NOT found in SDG page.")
            # print(resp.text[:1000]) # Print first 1000 chars to debug
    else:
        print(f"Failed to load SDG page: {resp.status_code}")

if __name__ == "__main__":
    test_sdg()
