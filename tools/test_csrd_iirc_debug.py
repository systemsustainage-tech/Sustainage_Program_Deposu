
import requests
import json
import time

BASE_URL = "http://127.0.0.1:5003"
LOGIN_URL = f"{BASE_URL}/login"
CSRD_URL = f"{BASE_URL}/csrd"
CSRD_ADD_URL = f"{BASE_URL}/csrd/materiality"
IIRC_URL = f"{BASE_URL}/iirc"
IIRC_ADD_URL = f"{BASE_URL}/iirc/add"

def test_csrd_iirc():
    session = requests.Session()
    
    # Login
    print("Logging in...")
    resp = session.post(LOGIN_URL, data={'username': 'admin', 'password': 'Admin_2025!'})
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code}")
        return
    print("Login successful")

    # CSRD Test
    print("\n--- Testing CSRD ---")
    print("Fetching CSRD page...")
    resp = session.get(CSRD_URL)
    if resp.status_code == 200:
        print("CSRD page loaded successfully")
        # Add CSRD data (Double Materiality)
        data = {
            'topic': 'Climate Change',
            'impact_materiality': 'High',
            'financial_materiality': 'Medium',
            'justification': 'Test Justification',
            'save_materiality': '1'
        }
        print("Adding CSRD Double Materiality data...")
        resp = session.post(CSRD_ADD_URL, data=data)
        if resp.status_code == 200 or resp.status_code == 302:
            print("CSRD data posted successfully")
            # Verify display
            resp = session.get(CSRD_URL)
            if 'Test Justification' in resp.text:
                print("SUCCESS: Found CSRD data in response")
            else:
                print("FAILURE: CSRD data NOT found in response")
        else:
            print(f"CSRD post failed: {resp.status_code}")
    else:
        print(f"Failed to load CSRD page: {resp.status_code}")

    # IIRC Test
    print("\n--- Testing IIRC ---")
    print("Fetching IIRC page...")
    resp = session.get(IIRC_URL)
    if resp.status_code == 200:
        print("IIRC page loaded successfully")
        # Add IIRC data (Integrated Report)
        data = {
            'year': '2024',
            'report_name': 'Test Report',
            'financial_capital': 'Test Financial',
            'human_capital': 'Test Human',
            'save_report': '1'
        }
        print("Adding IIRC Integrated Report data...")
        resp = session.post(IIRC_ADD_URL, data=data)
        if resp.status_code == 200 or resp.status_code == 302:
            print("IIRC data posted successfully")
            # Verify display
            resp = session.get(IIRC_URL)
            if 'Test Report' in resp.text:
                print("SUCCESS: Found IIRC data in response")
            else:
                print("FAILURE: IIRC data NOT found in response")
        else:
            print(f"IIRC post failed: {resp.status_code}")
    else:
        print(f"Failed to load IIRC page: {resp.status_code}")

if __name__ == "__main__":
    test_csrd_iirc()
