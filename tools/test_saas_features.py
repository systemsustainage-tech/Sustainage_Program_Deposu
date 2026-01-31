import requests
import time
import subprocess
import sys
import threading

# Config
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
API_DEMO_URL = f"{BASE_URL}/api/saas/demo"
API_STATS_URL = f"{BASE_URL}/api/dashboard/stats"
DASHBOARD_URL = f"{BASE_URL}/dashboard"

def run_server():
    """Starts the Flask server in a separate thread/process for testing."""
    print("Starting server on port 5005...")
    # Using python directly might block, so we use subprocess in a way we can kill later
    # But for this simple test script, we assume the user might have to run the server separately 
    # OR we try to launch it in background.
    # Given the environment, let's try to launch it.
    
    env = os.environ.copy()
    env['FLASK_APP'] = 'c:\\SUSTAINAGESERVER\\remote_web_app.py'
    env['FLASK_RUN_PORT'] = '5005'
    
    # We use remote_web_app.py directly. It has app.run() but usually protected by if main.
    # Let's check if remote_web_app.py runs on 5000 by default. 
    # We'll try to run it and wait a bit.
    
    # NOTE: Since we modified remote_web_app.py, we should be careful.
    # Ideally, we should import app and run it in a thread, but imports might be messy.
    pass

def test_saas_flow():
    session = requests.Session()
    
    print("\n--- Test 1: Access API without Login ---")
    response = session.get(API_DEMO_URL)
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("[PASS] API rejected unauthenticated request.")
    else:
        print(f"[FAIL] API allowed unauthenticated request! Code: {response.status_code}")

    print("\n--- Test 2: Login as 'admin' ---")
    # We need to post to login.
    # Based on code: username, password
    # We'll try admin/admin first (test mode) or check DB.
    # The search result showed: if username=='admin' and password=='admin' ...
    login_data = {'username': 'admin', 'password': 'admin'}
    response = session.post(LOGIN_URL, data=login_data)
    
    if response.status_code == 200 and "dashboard" in response.url:
        print("[PASS] Login successful.")
    else:
        # It might redirect
        if response.history:
            print(f"Redirection history: {[r.status_code for r in response.history]}")
        print(f"Final URL: {response.url}")
        if "dashboard" in response.url:
             print("[PASS] Login successful (redirected).")
        else:
             print("[FAIL] Login failed.")
             return

    print("\n--- Test 3: Access SaaS Demo API ---")
    response = session.get(API_DEMO_URL)
    if response.status_code == 200:
        data = response.json()
        print("API Response:", data)
        if 'company_id' in data and 'company_name' in data:
            print(f"[PASS] API returned company data. Company ID: {data['company_id']}")
        else:
            print("[FAIL] API response missing key fields.")
    else:
        print(f"[FAIL] API request failed. Code: {response.status_code}")

    print("\n--- Test 4: Access Dashboard Stats API ---")
    response = session.get(API_STATS_URL)
    if response.status_code == 200:
        data = response.json()
        print("Stats Response:", data)
        if 'energy_consumption' in data:
            print("[PASS] Dashboard Stats API returned data.")
        else:
            print("[FAIL] Stats API response malformed.")
    else:
        print(f"[FAIL] Stats API request failed. Code: {response.status_code}")
        print("Response Body:", response.text)

    print("\n--- Test 5: Check Dashboard Access (Strict Mode) ---")
    response = session.get(DASHBOARD_URL)
    if response.status_code == 200:
        print("[PASS] Dashboard accessible with context.")
    else:
        print(f"[FAIL] Dashboard access failed. Code: {response.status_code}")
        print("Response Body:", response.text)

if __name__ == "__main__":
    # We assume the server is running externally or we start it here.
    # For this environment, we'll try to connect. If fails, we ask user to start it.
    try:
        requests.get(BASE_URL, timeout=1)
        test_saas_flow()
    except requests.exceptions.ConnectionError:
        print("Server not running on port 5005.")
        print("Please run the server using: python c:\\SUSTAINAGESERVER\\remote_web_app.py")
        # In the agent context, we will launch it now.
