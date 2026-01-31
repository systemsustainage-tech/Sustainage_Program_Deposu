import requests
import sys
import paramiko
import os

HOSTNAME = '72.62.150.207'
USERNAME_SSH = 'root'
PASSWORD_SSH = os.environ.get('REMOTE_SSH_PASS', 'Kayra_1507')

BASE_URL = 'https://sustainage.cloud'
# Updated to use HTTPS as server enforces it

LOGIN_URL = f'{BASE_URL}/login'
GENERATE_URL = f'{BASE_URL}/mapping/suggestions/generate'
MAPPING_URL = f'{BASE_URL}/mapping'

USERNAME = '__super__'
PASSWORD = 'Kayra_1507'

def verify_suggestions():
    session = requests.Session()
    
    # 1. Login
    print(f"Logging in as {USERNAME}...", flush=True)
    try:
        r = session.get(LOGIN_URL, timeout=10, verify=False)
        login_data = {'username': USERNAME, 'password': PASSWORD}
        r = session.post(LOGIN_URL, data=login_data, timeout=10, verify=False)
        
        if r.status_code != 200:
            print(f"Login failed: {r.status_code}", flush=True)
            return False
            
        # 2. Trigger Generation
        print(f"Triggering suggestion generation...", flush=True)
        r = session.post(GENERATE_URL, timeout=30, allow_redirects=False, verify=False)
        print(f"Generation Status: {r.status_code}", flush=True)
        
        if r.status_code in [301, 302, 307, 308]:
             print(f"Redirected ({r.status_code}) to: {r.headers.get('Location')}", flush=True)
             # Follow redirect manually if needed, but we expect it to redirect AFTER success
             if 'mapping' in r.headers.get('Location', ''):
                 print("Redirect looks correct (back to mapping module).", flush=True)
             else:
                 print("Redirect unexpected.", flush=True)
                 
        elif r.status_code == 200:
             print("Generation request successful (OK).", flush=True)
        else:
             print(f"Generation request failed: {r.status_code}", flush=True)
             print(r.text[:200])
             
        # 3. Check DB for suggestions
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME_SSH, password=PASSWORD_SSH)
        
        cmd = "sqlite3 /var/www/sustainage/backend/data/sdg_desktop.sqlite \"SELECT COUNT(*) FROM mapping_suggestions;\""
        stdin, stdout, stderr = client.exec_command(cmd)
        count = stdout.read().decode().strip()
        print(f"Suggestions in DB: {count}", flush=True)
        
        client.close()
        return True

    except Exception as e:
        print(f"Error: {e}", flush=True)
        return False

if __name__ == "__main__":
    verify_suggestions()
