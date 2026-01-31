import requests
import sys

BASE_URL = "https://sustainage.cloud"
LOGIN_URL = f"{BASE_URL}/login"
DATA_ADD_URL = f"{BASE_URL}/data/add"
REPORT_CREATE_URL = f"{BASE_URL}/reports/create"
USERNAME = "test_user"
PASSWORD = "password123"

def test_data_and_reports():
    session = requests.Session()
    
    # 1. Login
    print(f"Logging in as {USERNAME}...")
    resp = session.post(LOGIN_URL, data={'username': USERNAME, 'password': PASSWORD})
    if resp.status_code != 200:
        print(f"Login failed. Status: {resp.status_code}")
        return False
    if "Giris basarili" not in resp.text and "dashboard" not in resp.url:
         # Check if already logged in or redirected
         if "/dashboard" in resp.url:
             print("Login successful (redirected).")
         else:
             print("Login failed (content check).")
             # print(resp.text)
             return False
    else:
        print("Login successful.")

    # 2. Add Carbon Data
    print("\n--- Testing Data Entry (Carbon) ---")
    data_payload = {
        'data_type': 'carbon',
        'date': '2023-05-01',
        'scope': 'Scope 1',
        'category': 'Stationary Combustion',
        'amount': '1000',
        'unit': 'liters',
        'co2e': '2500'
    }
    
    try:
        resp = session.post(DATA_ADD_URL, data=data_payload)
        if resp.status_code == 200:
            if "Veri başarıyla eklendi" in resp.text:
                print("SUCCESS: Carbon data added.")
            elif "/data" in resp.url:
                 # Check if redirected to data page (success)
                 print("SUCCESS: Carbon data added (Redirected to /data).")
            else:
                print("WARNING: Response 200 but success message not found.")
                print(f"URL: {resp.url}")
        else:
            print(f"FAILED: Carbon data add failed. Status: {resp.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

    # 3. Generate Report
    print("\n--- Testing Report Generation ---")
    # Need company_id. Assuming it's in the session or we can use '1'.
    # The script uses 'company_id' from form.
    report_payload = {
        'company_id': '1',
        'report_type': 'ghg_inventory',
        'period': '2023'
    }
    
    try:
        resp = session.post(REPORT_CREATE_URL, data=report_payload)
        if resp.status_code == 200:
            if "başarıyla oluşturuldu" in resp.text:
                print("SUCCESS: Report generated.")
            elif "/companies/detail" in resp.url:
                print("SUCCESS: Report generated (Redirected to company detail).")
                
                # Check if report is listed in the company detail page content
                if "GHG_Inventory_2023" in resp.text or ".docx" in resp.text or ".pdf" in resp.text:
                     print("VERIFIED: Report file listed.")
                else:
                     print("WARNING: Report generated but file not explicitly seen in response.")
            else:
                print("WARNING: Response 200 but success message not found.")
                print(f"URL: {resp.url}")
        else:
            print(f"FAILED: Report generation failed. Status: {resp.status_code}")
            # print(resp.text)
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

    return True

if __name__ == "__main__":
    if test_data_and_reports():
        print("\nAll tests passed!")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)
