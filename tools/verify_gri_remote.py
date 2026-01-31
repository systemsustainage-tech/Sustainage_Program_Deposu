import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://sustainage.cloud"
LOGIN_URL = f"{BASE_URL}/login"
GRI_URL = f"{BASE_URL}/gri"

def verify_gri_remote():
    session = requests.Session()
    
    # 1. Login
    logging.info("Attempting login with __super__...")
    response = session.post(LOGIN_URL, data={'username': '__super__', 'password': 'Kayra_1507'})
    
    if response.status_code != 200:
        logging.error(f"Login failed with status code {response.status_code}")
        # Check if it's a redirect (302) which requests handles automatically usually, 
        # but if it returns 200 on login page it means failure.
    
    if 'dashboard' in response.url or 'Giriş başarılı' in response.text:
         logging.info("Login successful.")
    else:
         logging.warning(f"Login might have failed. Current URL: {response.url}")
         # Try accessing GRI anyway, maybe session is set.
    
    # 2. Access GRI Module
    logging.info("Accessing GRI module...")
    response = session.get(GRI_URL)
    
    if response.status_code != 200:
        logging.error(f"Failed to access GRI module. Status: {response.status_code}")
        return False
        
    content = response.text
    
    # 3. Check for new standards
    expected_strings = [
        "GRI 11", "Oil and Gas",
        "GRI 12", "Coal",
        "GRI 13", "Agriculture",
        "GRI 14", "Mining",
        "GRI 101", "Biodiversity"
    ]
    
    missing = []
    for s in expected_strings:
        if s not in content:
            missing.append(s)
            
    if missing:
        logging.error(f"Missing strings in GRI page: {missing}")
        # Print snippet for debugging
        # print(content[:1000])
        return False
    
    logging.info("All expected GRI standards found in the dropdown/page.")
    return True

if __name__ == "__main__":
    verify_gri_remote()
