import requests
import sys

# Remote configuration
BASE_URL_IP = "http://72.62.150.207"
BASE_URL_DOMAIN = "https://sustainage.cloud"

def check_url(url):
    try:
        print(f"Checking {url}...")
        response = requests.get(url, timeout=10, verify=False) # verify=False for potential self-signed certs
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Page is accessible.")
            print(f"Content preview: {response.text[:200]}")
            if "Örnek Sürdürülebilirlik Anketi" in response.text or "Sürdürülebilirlik" in response.text:
                print("Content verification: PASSED (Found expected text)")
            else:
                print("Content verification: WARNING (Expected text not found)")
        else:
            print(f"Failed. Content: {response.text[:200]}")
    except Exception as e:
        print(f"Error checking URL: {e}")

if __name__ == "__main__":
    # Check IP based access
    check_url(f"{BASE_URL_IP}/survey/sample_survey")
    
    # Check Domain based access
    check_url(f"{BASE_URL_DOMAIN}/survey/sample_survey")
