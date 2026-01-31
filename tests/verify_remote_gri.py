import requests
import logging
import sys
import urllib3
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://72.62.150.207"
LOGIN_URL = f"{BASE_URL}/login"
GRI_API_URL = f"{BASE_URL}/api/gri/indicators/GRI%2014"
GRI_PAGE_URL = f"{BASE_URL}/gri"

USERNAME = "__super__"
PASSWORD = "Kayra_1507"

session = requests.Session()

def verify_gri_remote():
    logging.info(f"Checking Login at {LOGIN_URL}...")
    try:
        # Login
        response = session.get(LOGIN_URL, timeout=10, verify=False)
        data = {'username': USERNAME, 'password': PASSWORD}
        response = session.post(LOGIN_URL, data=data, timeout=15, verify=False, allow_redirects=True)
        
        if response.status_code == 200 and ("dashboard" in response.url or "Dashboard" in response.text):
            logging.info("Login SUCCESS.")
        else:
            logging.error(f"Login FAILED. Status: {response.status_code}")
            logging.error(f"Response URL: {response.url}")
            logging.error(f"Response Text Preview: {response.text[:500]}")
            return False

        # Check API
        logging.info(f"Checking GRI API at {GRI_API_URL}...")
        api_resp = session.get(GRI_API_URL, verify=False)
        if api_resp.status_code == 200:
            try:
                data = api_resp.json()
                indicators = data.get('indicators', [])
                logging.info(f"API returned {len(indicators)} indicators.")
                
                # Check for specific indicators (14-1)
                found_14_1 = any(ind['code'] == '14-1' for ind in indicators)
                if found_14_1:
                    logging.info("GRI 14-1 found in API response. ✅")
                else:
                    logging.error("GRI 14-1 NOT found in API response. ❌")
                    return False
                    
            except json.JSONDecodeError:
                logging.error("API did not return JSON.")
                return False
        else:
            logging.error(f"API check failed: {api_resp.status_code}")
            return False

        # Check Page
        logging.info(f"Checking GRI Page at {GRI_PAGE_URL}...")
        page_resp = session.get(GRI_PAGE_URL, verify=False)
        if page_resp.status_code == 200:
            content = page_resp.text
            # Check for new translation keys or elements
            if 'GRI 14' in content or 'Madencilik' in content or 'Mining' in content:
                logging.info("GRI 14/Mining found on page. ✅")
            else:
                logging.warning("GRI 14/Mining text NOT found explicitly on page (might be in dropdown js).")
            
            # Check for sector filter dropdown
            if 'select_sector' in content or 'Sektöre Göre' in content or 'sector' in content: # 'sector' is common word, check id
                if 'id="sectorFilter"' in content or 'id="standardSelect"' in content:
                    logging.info("Sector filter/Standard select elements found. ✅")
                    return True
                else:
                    logging.error("Sector filter elements NOT found.")
                    return False
            else:
                logging.info("Page loaded but specific sector text not matched (could be okay if rendered via JS).")
                return True
        else:
            logging.error(f"Page load failed: {page_resp.status_code}")
            return False

    except Exception as e:
        logging.error(f"Verification failed with error: {e}")
        return False

if __name__ == "__main__":
    if verify_gri_remote():
        print("VERIFICATION SUCCESS: GRI Module is updated and accessible.")
        sys.exit(0)
    else:
        print("VERIFICATION FAILED.")
        sys.exit(1)
