import requests
import re

BASE_URL = 'http://72.62.150.207'
LOGIN_URL = f'{BASE_URL}/login'
REPORT_URL = f'{BASE_URL}/reports'
COMPANY_GRI_URL = f'{BASE_URL}/companies/gri/1' # Assuming company 1 exists (Test Company)

def verify():
    session = requests.Session()
    
    # 1. Login
    print("Logging in...")
    resp = session.get(LOGIN_URL)
    # Extract CSRF token if present (not using WTF-CSRF here based on code, just simple form)
    
    login_data = {
        'username': 'admin',
        'password': 'password123'
    }
    resp = session.post(LOGIN_URL, data=login_data)
    
    if 'Giriş başarılı' in resp.text or 'Dashboard' in resp.text or resp.url == f'{BASE_URL}/':
        print("Login Successful.")
    else:
        print("Login Failed.")
        # Try to print why
        # print(resp.text[:500])
        
    # 2. Check GRI Page
    print(f"Checking {COMPANY_GRI_URL}...")
    resp = session.get(COMPANY_GRI_URL)
    if resp.status_code == 200 and 'Firma Bilgileri (GRI Uyumlu)' in resp.text:
        print("GRI Page OK.")
    else:
        print(f"GRI Page Failed: {resp.status_code}")
        
    # 3. Create Report (Simulate)
    # We need to post to /reports/add
    # But wait, create_report route in company_detail.html points to 'create_report' which I don't see in web_app.py
    # Let me check web_app.py again. I saw report_add but company_detail.html had `action="{{ url_for('create_report') }}"`.
    # Ah, I might have missed checking `create_report` route in web_app.py.
    # If it's missing, report creation from company detail page will fail.
    
    # 4. Check Delete Report logic
    # We used report_delete in company_detail.html which maps to /reports/delete/<id>.
    
    return session

if __name__ == '__main__':
    verify()