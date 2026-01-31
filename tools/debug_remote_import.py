import paramiko
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def debug_import():
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
        print("Running debug import...")
        # Command to run python inside venv and attempt import
        cmd = "cd /var/www/sustainage && source venv/bin/activate && python3 -c \"import sys; sys.path.append('/var/www/sustainage'); import logging; logging.basicConfig(level=logging.DEBUG); from web_app import app; print('IMPORT_SUCCESS')\""
        
        # We need to use invoke_shell or exec_command with bash to support source
        stdin, stdout, stderr = client.exec_command(f"bash -c '{cmd}'")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("STDOUT:", out)
        print("STDERR:", err)
            
    except Exception as e:
        print(f"Execution failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    debug_import()
