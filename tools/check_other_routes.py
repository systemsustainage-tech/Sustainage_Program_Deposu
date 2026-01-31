
import requests

BASE_URL = "https://sustainage.cloud"
USERNAME = "test_user"
PASSWORD = "password123"

def check_other_routes():
    s = requests.Session()
    resp = s.post(f"{BASE_URL}/login", data={'username': USERNAME, 'password': PASSWORD})
    print(f"Login Status: {resp.status_code}")
    
    urls = [
        f"{BASE_URL}/reports/add",
        f"{BASE_URL}/companies",
        f"{BASE_URL}/dashboard"
    ]
    
    for url in urls:
        print(f"Checking {url}...")
        resp = s.get(url)
        print(f"Status: {resp.status_code}")

if __name__ == "__main__":
    check_other_routes()
