
import requests
import sys

HOST = "72.62.150.207"
URL = f"http://{HOST}/login"

def check_login():
    print(f"Checking {URL}...")
    try:
        response = requests.get(URL, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Login page is accessible.")
            if "Sustainage" in response.text:
                print("Content verification passed (found 'Sustainage').")
            else:
                print("Warning: 'Sustainage' not found in response text.")
        else:
            print(f"Failed to access login page. Status: {response.status_code}")
    except Exception as e:
        print(f"Error checking login page: {e}")

if __name__ == "__main__":
    check_login()
