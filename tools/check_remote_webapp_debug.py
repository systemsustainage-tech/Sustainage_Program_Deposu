import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

URLS = [
    'https://sustainage.cloud/test_cgi.py',
    'https://sustainage.cloud/test_import_debug.py'
]

def check_url(url):
    try:
        logging.info(f"Checking {url}...")
        response = requests.get(url, timeout=10)
        logging.info(f"Status Code: {response.status_code}")
        logging.info("Response Content:")
        print(response.text)
        print("-" * 50)
    except Exception as e:
        logging.error(f"Failed to reach {url}: {e}")

if __name__ == '__main__':
    for url in URLS:
        check_url(url)
