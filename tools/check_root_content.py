import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def check_root_content():
    url = 'https://sustainage.cloud/'
    try:
        logging.info(f"Checking {url}...")
        response = requests.get(url, timeout=10)
        logging.info(f"Status Code: {response.status_code}")
        logging.info("First 500 chars of content:")
        print(response.text[:500])
        
        if "Login" in response.text or "Giriş" in response.text:
            logging.info("Likely the Login Page (Flask App running?)")
        elif "Dashboard" in response.text:
            logging.info("Likely the Dashboard (Static HTML?)")
        else:
            logging.info("Unknown content.")
            
    except Exception as e:
        logging.error(f"Failed to reach {url}: {e}")

if __name__ == '__main__':
    check_root_content()
