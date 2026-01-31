import paramiko
import sys
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def execute_remote_fix():
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
        print("Could not connect.")
        return

    try:
        command = "python3 /var/www/sustainage/tools/fix_remote_schema_all.py"
        print(f"Executing: {command}")
        stdin, stdout, stderr = client.exec_command(command)
        
        exit_status = stdout.channel.recv_exit_status()
        print(f"Exit status: {exit_status}")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        if out: print(f"Output:\n{out}")
        if err: print(f"Error:\n{err}")
        
        # Restart service after fix
        print("Restarting sustainage service...")
        client.exec_command("systemctl restart sustainage")
        print("Service restart command sent.")
        
    except Exception as e:
        print(f"Execution failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    execute_remote_fix()
