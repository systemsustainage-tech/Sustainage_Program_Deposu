import paramiko
import time
import sys

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def run_assignment():
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
            time.sleep(2)
            
    if not connected:
        print("Could not connect after 3 attempts.")
        return False
        
    try:
        cmd = "python3 /var/www/sustainage/tools/assign_company_to_super.py"
        print(f"Executing: {cmd}")
        
        stdin, stdout, stderr = client.exec_command(cmd)
        
        # Wait for command to finish
        exit_status = stdout.channel.recv_exit_status()
        
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        
        print("Output:")
        print(out)
        
        if err:
            print("Errors:")
            print(err)
            
        if exit_status == 0:
            print("Assignment script executed successfully.")
        else:
            print(f"Assignment script failed with exit code {exit_status}")
            
        return exit_status == 0
        
    except Exception as e:
        print(f"Execution failed: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = run_assignment()
    if not success:
        sys.exit(1)
