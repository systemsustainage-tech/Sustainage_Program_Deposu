import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = 'http://72.62.150.207'
LOGIN_URL = f'{BASE_URL}/login'
DASHBOARD_URL = f'{BASE_URL}/dashboard'

USERNAME = '__super__'
PASSWORD = 'super123'

def test_login():
    session = requests.Session()
    
    # 1. Get Login Page (CSRF check if needed, but we don't use CSRF token in form currently)
    try:
        logging.info(f"Fetching login page: {LOGIN_URL}")
        response = session.get(LOGIN_URL)
        if response.status_code != 200:
            logging.error(f"Failed to get login page. Status: {response.status_code}")
            return False
        logging.info("Login page fetched successfully.")
    except Exception as e:
        logging.error(f"Connection error: {e}")
        return False

    # 2. Post Login
    payload = {
        'username': USERNAME,
        'password': PASSWORD
    }
    
    try:
        logging.info(f"Attempting login with user: {USERNAME}")
        response = session.post(LOGIN_URL, data=payload, allow_redirects=True)
        
        logging.info(f"Login Response Status: {response.status_code}")
        logging.info(f"Final URL: {response.url}")
        
        if response.url == DASHBOARD_URL:
            logging.info("Login SUCCESS! Redirected to dashboard.")
            if "Panel" in response.text or "Dashboard" in response.text:
                 logging.info("Dashboard content verified.")
            else:
                 logging.warning("Dashboard URL reached but content might be wrong.")
                 # print(response.text[:500])
            return True
        elif "/login" in response.url:
            logging.error("Login FAILED. Redirected back to login page.")
            if "Hata" in response.text or "Error" in response.text:
                logging.info("Error message detected on page.")
            return False
        else:
            logging.warning(f"Unexpected redirect: {response.url}")
            return False
            
    except Exception as e:
        logging.error(f"Login request failed: {e}")
        return False

if __name__ == "__main__":
    test_login()
