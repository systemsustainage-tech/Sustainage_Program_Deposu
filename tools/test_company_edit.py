
import requests
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "http://localhost:5000"
USERNAME = "test_user"
PASSWORD = "Test1234!"

def test_company_edit():
    session = requests.Session()
    
    # 1. Login
    logging.info(f"1. Attempting login as {USERNAME}...")
    try:
        login_payload = {'username': USERNAME, 'password': PASSWORD}
        resp = session.post(f"{BASE_URL}/login", data=login_payload)
        
        if resp.status_code == 200 and ("dashboard" in resp.url or "Dashboard" in resp.text or "Hoşgeldiniz" in resp.text):
            logging.info("   Login SUCCESS.")
        else:
            logging.error(f"   Login FAILED. Status: {resp.status_code}, URL: {resp.url}")
            return False
    except Exception as e:
        logging.error(f"   Login ERROR: {e}")
        return False

    # 2. GET company_edit
    logging.info("2. Testing GET /company_edit...")
    try:
        resp = session.get(f"{BASE_URL}/company_edit")
        if resp.status_code == 200:
            logging.info("   GET /company_edit SUCCESS.")
            # Check if key fields are present in form
            if 'name="sirket_adi"' in resp.text:
                 logging.info("   Form fields confirmed (sirket_adi found).")
            else:
                 logging.warning("   Form fields might be missing.")
        else:
            logging.error(f"   GET /company_edit FAILED. Status: {resp.status_code}")
            logging.error(f"   Response snippet: {resp.text[:500]}")
            return False
    except Exception as e:
        logging.error(f"   GET /company_edit ERROR: {e}")
        return False

    # 3. POST company_edit (Update)
    logging.info("3. Testing POST /company_edit...")
    try:
        payload = {
            'sirket_adi': 'Test Şirket A.Ş.',
            'ticari_unvan': 'Test Ticari',
            'sektor': 'Technology',
            'calisan_sayisi': '100',
            'aktif': 'on',
            'il': 'Istanbul',
            'ilce': 'Kadikoy',
            'adres': 'Test Adresi'
        }
        resp = session.post(f"{BASE_URL}/company_edit", data=payload)
        
        # Expect redirect (302) or 200 if it renders template again with success message
        # Requests follows redirects by default, so we check final url or history
        
        if resp.status_code == 200 and "company_edit" in resp.url:
             # Check for success message
             if "başarıyla güncellendi" in resp.text or "updated" in resp.text or "success" in resp.text:
                 logging.info("   POST /company_edit SUCCESS (Data updated).")
             else:
                 logging.warning("   POST /company_edit returned 200 but success message not found. Might be error.")
                 logging.info(f"   Response snippet: {resp.text[:500]}")
        else:
            logging.error(f"   POST /company_edit FAILED. Status: {resp.status_code}")
            return False

    except Exception as e:
        logging.error(f"   POST /company_edit ERROR: {e}")
        return False

    return True

if __name__ == "__main__":
    if test_company_edit():
        print("TEST PASSED")
        sys.exit(0)
    else:
        print("TEST FAILED")
        sys.exit(1)
