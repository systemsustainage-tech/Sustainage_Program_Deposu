
import requests
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def verify_gri_filter():
    hostname = "72.62.150.207"
    login_url = f"https://{hostname}/login"
    target_url = f"https://{hostname}/gri"
    
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Host': 'sustainage.cloud'
    }
    
    print(f"Logging in to {login_url}...")
    try:
        # Initial GET
        session.get(login_url, verify=False, headers=headers)
        
        # Login
        resp = session.post(login_url, data={
            'username': '__super__',
            'password': 'Kayra_1507'
        }, verify=False, headers=headers, allow_redirects=True)
        
        if resp.status_code != 200 or 'dashboard' not in resp.url:
            print(f"Login failed! Status: {resp.status_code}, URL: {resp.url}")
            return False
            
        print("Login successful.")
        
        # Get GRI page
        print(f"Fetching {target_url}...")
        resp = session.get(target_url, verify=False, headers=headers)
        
        if resp.status_code != 200:
            print(f"Failed to fetch GRI page. Status: {resp.status_code}")
            return False
            
        content = resp.text
        
        # Check for data-sector attribute
        matches = re.findall(r'data-sector="([^"]+)"', content)
        
        if matches:
            print(f"Found {len(matches)} rows with data-sector attribute.")
            print(f"Sectors found: {set(matches)}")
            return True
        else:
            print("No data-sector attributes found in the HTML.")
            # Print a snippet of the table body to debug
            if '<tbody>' in content:
                tbody = content.split('<tbody>')[1].split('</tbody>')[0]
                print(f"Table body snippet:\n{tbody[:500]}")
            return False
            
    except Exception as e:
        print(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    verify_gri_filter()
