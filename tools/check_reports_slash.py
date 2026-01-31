
import requests

BASE_URL = "https://sustainage.cloud"
URLS = [
    f"{BASE_URL}/reports",
    f"{BASE_URL}/reports/"
]
USERNAME = "test_user"
PASSWORD = "password123"

def check():
    s = requests.Session()
    s.post(f"{BASE_URL}/login", data={'username': USERNAME, 'password': PASSWORD})
    
    for url in URLS:
        print(f"Checking {url}...")
        resp = s.get(url)
        print(f"Status: {resp.status_code}")

if __name__ == "__main__":
    check()
