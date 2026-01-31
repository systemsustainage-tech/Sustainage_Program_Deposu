
import requests
import sys

HOST = '72.62.150.207'
LOGIN_URL = f"http://{HOST}/login"
DATA_ADD_URL = f"http://{HOST}/data/add"
REPORT_CREATE_URL = f"http://{HOST}/reports/create"
BASE_URL = f"http://{HOST}"

USERNAME = '__super__'
PASSWORD = 'super123'

def test_functionality():
    session = requests.Session()
    
    # Login
    print("Logging in...")
    r = session.get(LOGIN_URL)
    payload = {'username': USERNAME, 'password': PASSWORD}
    r = session.post(LOGIN_URL, data=payload)
    if r.url != f"{BASE_URL}/dashboard":
        print("Login Failed.")
        return

    print("Login Success.")

    # 1. Test Data Entry (Carbon)
    print("Testing Data Entry (Carbon)...")
    data_payload = {
        'data_type': 'carbon',
        'date': '2025-01-01',
        'scope': 'Scope 1',
        'category': 'Stationary Combustion',
        'amount': '100',
        'unit': 'liters',
        'co2e': '250.5'
    }
    r = session.post(DATA_ADD_URL, data=data_payload, allow_redirects=True)
    if r.status_code == 200 and "Veri başarıyla eklendi" in r.text:
        print("Data Entry SUCCESS.")
    else:
        print(f"Data Entry FAIL. Status: {r.status_code}")
        # Print flash messages
        if "alert-danger" in r.text:
            print("Error Alert Found!")
            start = r.text.find("alert-danger")
            print(r.text[start:start+200])
        elif "alert-success" in r.text:
            print("Success Alert Found (but text match failed?)")
            start = r.text.find("alert-success")
            print(r.text[start:start+200])
        else:
             print("No alert found. Page title/header:")
             print(r.text[:500])

    # 2. Test Report Creation (GHG Inventory)
    print("Testing Report Creation (GHG Inventory)...")
    # Need company_id, likely 1
    report_payload = {
        'company_id': '1',
        'report_type': 'ghg_inventory',
        'period': '2024'
    }
    r = session.post(REPORT_CREATE_URL, data=report_payload, allow_redirects=True)
    if r.status_code == 200 and "başarıyla oluşturuldu" in r.text:
        print("Report Creation SUCCESS.")
    else:
        print(f"Report Creation FAIL. Status: {r.status_code}")
        # Check if company 1 exists
        if "Şirket bulunamadı" in r.text:
             print("Reason: Company 1 not found.")

if __name__ == '__main__':
    test_functionality()
