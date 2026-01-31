import paramiko
import sys
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def verify_system_health():
    # 1. Upload updated web_app.py with health check
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        print("Uploading updated web_app.py...")
        sftp.put('c:\\SUSTAINAGESERVER\\web_app.py', '/var/www/sustainage/web_app.py')
        sftp.close()
        
        print("Restarting service...")
        client.exec_command("systemctl restart sustainage")
        time.sleep(5) # Wait for restart
        
        # 2. Run local check against remote URL via curl (since we are on remote via ssh)
        # OR run a python script on remote that hits localhost
        
        check_script = """
import requests
import json
try:
    resp = requests.get('http://127.0.0.1:5000/system/health', timeout=10)
    print("Status Code:", resp.status_code)
    print("Body:", resp.text)
except Exception as e:
    print("Error:", e)
"""
        with open('temp_check.py', 'w') as f:
            f.write(check_script)
            
        sftp = client.open_sftp()
        sftp.put('temp_check.py', '/tmp/health_check_remote.py')
        sftp.close()
        os.remove('temp_check.py')
        
        print("Running health check on remote...")
        stdin, stdout, stderr = client.exec_command("python3 /tmp/health_check_remote.py")
        out = stdout.read().decode()
        err = stderr.read().decode()
        print("\n--- Health Check Results ---")
        print(out)
        if err: print("Error:", err)
        
    except Exception as e:
        print(f"Verification failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    verify_system_health()
