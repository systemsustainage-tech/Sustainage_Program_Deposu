import requests
import json
from bs4 import BeautifulSoup

BASE_URL = "https://sustainage.cloud"
LOGIN_URL = f"{BASE_URL}/login"

# User Credentials
USERNAME = "test_user"
PASSWORD = "password123"

def test_module_data_entry():
    session = requests.Session()
    
    # 1. Login
    print("Logging in...")
    resp = session.get(LOGIN_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})
    token = csrf_token['value'] if csrf_token else None
    
    login_data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    if token:
        login_data['csrf_token'] = token
        
    resp = session.post(LOGIN_URL, data=login_data)
    if "Giris basarili" not in resp.text and "/dashboard" not in resp.url:
        print("Login failed.")
        print(resp.text)
        return
    print("Login successful.")

    def check_response(resp, module_name, success_msg):
        if resp.status_code == 200 and (success_msg in resp.text or "/data" in resp.url):
            print(f"SUCCESS: {module_name} data added.")
        else:
            print(f"FAILED: {module_name} add. Status: {resp.status_code}, URL: {resp.url}")
            try:
                soup = BeautifulSoup(resp.text, 'html.parser')
                alerts = soup.find_all('div', class_='alert')
                if alerts:
                    for alert in alerts:
                        print(f"Alert: {alert.get_text().strip()}")
                else:
                    print("No alerts found.")
            except Exception as e:
                print(f"Error parsing alerts: {e}")

    # 2. Test Carbon Add
    print("\n--- Testing Carbon Add ---")
    carbon_data = {
        'date': '2025-01',
        'scope': 'Scope 1',
        'category': 'Mobile Combustion',
        'amount': 100,
        'unit': 'liters',
        'co2e': 250,
        'source': 'Vehicle Fleet',
        'fuel_type': 'Diesel'
    }
    resp = session.post(f"{BASE_URL}/carbon/add", data=carbon_data)
    check_response(resp, "Carbon", "Karbon verisi başarıyla eklendi")

    # 3. Test Energy Add
    print("\n--- Testing Energy Add ---")
    energy_data = {
        'date': '2025-01',
        'energy_type': 'Electricity',
        'energy_consumption': 500,
        'energy_unit': 'kWh',
        'cost': 1000
    }
    resp = session.post(f"{BASE_URL}/energy/add", data=energy_data)
    check_response(resp, "Energy", "Enerji verisi başarıyla eklendi")

    # 4. Test Water Add
    print("\n--- Testing Water Add ---")
    water_data = {
        'date': '2025-01',
        'water_type': 'Mains',
        'water_consumption': 50,
        'water_unit': 'm3'
    }
    resp = session.post(f"{BASE_URL}/water/add", data=water_data)
    check_response(resp, "Water", "Su verisi başarıyla eklendi")

    # 5. Test Waste Add
    print("\n--- Testing Waste Add ---")
    waste_data = {
        'date': '2025-01',
        'waste_type': 'Plastic',
        'waste_amount': 20,
        'waste_unit': 'kg',
        'disposal_method': 'Recycling'
    }
    resp = session.post(f"{BASE_URL}/waste/add", data=waste_data)
    check_response(resp, "Waste", "Atık verisi başarıyla eklendi")

    # 6. Test Social Add
    print("\n--- Testing Social Add ---")
    social_data = {
        'date': '2025-06-01',
        'social_category': 'employment',
        'employees_total': 100,
        'employees_female': 45,
        'employees_youth': 30,
        'turnover_rate': 5.2
    }
    resp = session.post(f"{BASE_URL}/social/add", data=social_data)
    check_response(resp, "Social", "Sosyal veri başarıyla eklendi")

    # 7. Test Governance Add
    print("\n--- Testing Governance Add ---")
    governance_data = {
        'date': '2025',
        'governance_category': 'board',
        'board_members': 10,
        'female_members': 4,
        'independent_members': 3
    }
    resp = session.post(f"{BASE_URL}/governance/add", data=governance_data)
    check_response(resp, "Governance", "Yönetişim verisi başarıyla eklendi")

    # 8. Test Economic Add
    print("\n--- Testing Economic Add ---")
    economic_data = {
        'date': '2025',
        'economic_category': 'value',
        'revenue': 1000000,
        'operating_costs': 800000
    }
    resp = session.post(f"{BASE_URL}/economic/add", data=economic_data)
    check_response(resp, "Economic", "Ekonomik veri başarıyla eklendi")

if __name__ == "__main__":
    test_module_data_entry()
