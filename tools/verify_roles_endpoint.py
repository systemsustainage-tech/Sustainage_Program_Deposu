
import requests

URL = "http://72.62.150.207:5000/roles"

try:
    print(f"Checking {URL}...")
    response = requests.get(URL, allow_redirects=False, timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code in [200, 302]:
        print("Success! Endpoint is reachable.")
        if response.status_code == 302:
            print(f"Redirected to: {response.headers.get('Location')}")
    else:
        print(f"Failed! Status Code: {response.status_code}")
        print(response.text[:500])
except Exception as e:
    print(f"Error: {e}")
