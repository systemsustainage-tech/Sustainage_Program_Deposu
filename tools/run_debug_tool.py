import paramiko
import os

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
LOCAL_SCRIPT = 'tools/remote_debug_script.py'
REMOTE_SCRIPT = '/var/www/sustainage/remote_debug_script.py'

def run_debug():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    connected = False
    for attempt in range(3):
        try:
            print(f"Connecting to {HOSTNAME} (Attempt {attempt+1}/3)...")
            client.connect(HOSTNAME, username=USERNAME, password=PASSWORD, banner_timeout=30)
            connected = True
            break
        except Exception as e:
            print(f"Connection failed: {e}")
            import time
            time.sleep(2)
            
    if not connected:
        print("Could not connect after 3 attempts.")
        return

    try:
        # Upload script
        print(f"Uploading {LOCAL_SCRIPT}...")
        sftp = client.open_sftp()
        sftp.put(LOCAL_SCRIPT, REMOTE_SCRIPT)
        sftp.close()
        
        # Run script
        print("Running debug script...")
        cmd = f"cd /var/www/sustainage && source venv/bin/activate && python {REMOTE_SCRIPT}"
        stdin, stdout, stderr = client.exec_command(f"bash -c '{cmd}'")
        
        print("--- STDOUT ---")
        print(stdout.read().decode())
        print("--- STDERR ---")
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Execution failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_debug()
