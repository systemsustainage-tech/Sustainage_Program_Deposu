import paramiko
import time
import sys
import os

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_DIR = '/var/www/sustainage'

def run_command(command):
    print(f"Preparing to run: {command}")
    
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
        stdin, stdout, stderr = client.exec_command(f"cd {REMOTE_DIR} && {command}")
        
        # Wait for command to finish
        exit_status = stdout.channel.recv_exit_status()
        
        print("--- STDOUT ---")
        print(stdout.read().decode())
        print("--- STDERR ---")
        print(stderr.read().decode())
        
        if exit_status == 0:
            print("Command executed successfully.")
            return True
        else:
            print(f"Command failed with exit status {exit_status}")
            return False
            
    except Exception as e:
        print(f"Error executing command: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
    else:
        cmd = "python3 tools/patch_remote_db.py"
        
    run_command(cmd)
