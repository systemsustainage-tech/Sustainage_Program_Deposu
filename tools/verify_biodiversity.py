
import requests
import sys

URL = "http://72.62.150.207:5000/biodiversity"

def verify():
    try:
        # Since we need login, this might redirect to login page (302) or 200 if public (unlikely)
        # But getting a response means the route exists and doesn't 500.
        print(f"Checking {URL}...")
        response = requests.get(URL, allow_redirects=False)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print("Biodiversity route is reachable.")
            # If 302, it's likely redirecting to login, which is expected behavior for protected route.
            if response.status_code == 302:
                print(f"Redirects to: {response.headers.get('Location')}")
        else:
            print(f"Failed to reach biodiversity route. Status: {response.status_code}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error checking URL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
