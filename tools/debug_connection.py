import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    resp = requests.get('https://72.62.150.207/', verify=False, timeout=10)
    print(f"Status: {resp.status_code}")
    print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")
