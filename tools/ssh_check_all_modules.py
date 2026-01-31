
import paramiko
import requests
import sys
import time

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
LOGIN_URL = f"http://{HOST}/login"
BASE_URL = f"http://{HOST}"

# Credentials
USERNAME = '__super__'
PASSWORD = 'super123'

MODULES = [
    '/carbon', '/energy', '/waste', '/water', '/biodiversity',
    '/social', '/governance', '/supply_chain', '/economic',
    '/esg', '/cbam', '/csrd', '/taxonomy', '/gri', '/sdg',
    '/ifrs', '/tcfd', '/tnfd', '/cdp'
]

def upload_hardware_lock():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST} via SSH...")
        client.connect(HOST, username=USER, password=PASS)
        
        # Ensure directory exists
        remote_dir = '/var/www/sustainage/backend/modules/security'
        client.exec_command(f'mkdir -p {remote_dir}')
        
        sftp = client.open_sftp()
        local_path = r'c:\SDG\server\backend\modules\security\hardware_lock.py'
        remote_path = f'{remote_dir}/hardware_lock.py'
        
        print(f"Uploading {local_path} -> {remote_path}...")
        sftp.put(local_path, remote_path)
        print("Upload complete.")
        
        sftp.close()
        
        # Restart service
        print("Restarting sustainage service...")
        client.exec_command('systemctl restart sustainage')
        time.sleep(3) # Wait for restart
        
    except Exception as e:
        print(f"SSH Error: {e}")
    finally:
        client.close()

def check_modules():
    print("Checking modules...")
    session = requests.Session()
    
    # Login
    try:
        r = session.get(LOGIN_URL)
        payload = {'username': USERNAME, 'password': PASSWORD}
        r = session.post(LOGIN_URL, data=payload)
        
        if r.url == f"{BASE_URL}/dashboard":
            print("Login Successful.")
        else:
            print("Login Failed. Aborting module check.")
            return
            
        # Check each module
        success_count = 0
        for mod in MODULES:
            url = f"{BASE_URL}{mod}"
            print(f"Checking {mod}...", end=' ')
            r = session.get(url)
            if r.status_code == 200:
                print("OK")
                success_count += 1
            else:
                print(f"FAIL ({r.status_code})")
        
        print(f"Summary: {success_count}/{len(MODULES)} modules active.")
        
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == '__main__':
    upload_hardware_lock()
    # Give service a moment to come up
    time.sleep(5)
    check_modules()
