
import requests
import json
try:
    resp = requests.get('http://127.0.0.1:5000/system/health', timeout=10)
    print("Status Code:", resp.status_code)
    print("Body:", resp.text)
except Exception as e:
    print("Error:", e)
