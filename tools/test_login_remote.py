import requests
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def test_login():
    url = 'https://sustainage.cloud/login'
    data = {
        'username': 'admin',
        'password': 'admin'
    }
    
    try:
        logging.info(f"Attempting login at {url}...")
        session = requests.Session()
        response = session.post(url, data=data, timeout=15)
        
        logging.info(f"Status Code: {response.status_code}")

        if "DEPLOYMENT VERSION: 2026-01-01 V2" in response.text:
            logging.info("SUCCESS: Verified new template version (V2).")
        else:
            logging.warning("WARNING: New template version NOT found. Old cache?")
        
        if "UserManager kullanilamiyor" in response.text:
            logging.error("FAILURE: UserManager is NOT available.")
            # Extract the error detail
            match = re.search(r"Sistem hatasi: UserManager kullanilamiyor\. Detay: (.*?)</div>", response.text)
            if match:
                logging.error(f"ERROR DETAIL: {match.group(1)}")
            else:
                logging.error("Could not extract error detail. Dumping surrounding text:")
                idx = response.text.find("UserManager kullanilamiyor")
                print(response.text[idx-100:idx+300])
                
        elif "Kullanici adi veya parola hatali" in response.text:
            logging.info("SUCCESS: UserManager is available (Auth failed, but Manager is working).")
        elif "dashboard" in response.url or "Giris basarili" in response.text:
             logging.info("SUCCESS: Login successful!")
        else:
             logging.warning("Unknown response state.")
             
    except Exception as e:
        logging.error(f"Login request failed: {e}")

if __name__ == '__main__':
    test_login()
