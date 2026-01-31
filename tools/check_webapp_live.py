import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

URLS = [
    'https://sustainage.cloud/test_debug',
    'https://sustainage.cloud/'
]

def check_url(url):
    try:
        logging.info(f"Checking {url}...")
        response = requests.get(url, timeout=10)
        logging.info(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            logging.info("Success!")
            if "test_debug" in url:
                print(response.text.replace('<br>', '\n'))
        else:
            logging.error(f"Failed with status code: {response.status_code}")
            logging.error(response.text[:500])
    except Exception as e:
        logging.error(f"Failed to reach {url}: {e}")

if __name__ == '__main__':
    for url in URLS:
        check_url(url)
