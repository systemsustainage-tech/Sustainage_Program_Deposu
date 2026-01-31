import requests
import sys

# Configuration
BASE_URL = "https://sustainage.cloud"
LOGIN_URL = f"{BASE_URL}/login"
IIRC_URL = f"{BASE_URL}/iirc"
USERNAME = "test_user"
PASSWORD = "password123"

def check_iirc():
    session = requests.Session()
    
    # Login
    resp = session.post(LOGIN_URL, data={'username': USERNAME, 'password': PASSWORD})
    if resp.status_code != 200:
        print("Login failed")
        return False
        
    # Get IIRC page
    resp = session.get(IIRC_URL)
    print(f"Status: {resp.status_code}")
    
    content = resp.text
    print(f"Content length: {len(content)}")
    print("--- Content Snippet (first 1000 chars) ---")
    print(content[:1000])
    print("------------------------------------------")
    
    keywords = ["IIRC", "Entegre", "Integrated"]
    found = []
    for k in keywords:
        if k in content:
            found.append(k)
            
    print(f"Found keywords: {found}")
    
    if not found:
        print("WARNING: No expected keywords found.")
        return False
    return True

if __name__ == "__main__":
    check_iirc()
