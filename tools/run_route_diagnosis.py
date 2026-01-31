
import paramiko
import os
import time

# Remote server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_diagnosis():
    print(f"Connecting to {HOSTNAME}...")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        
        # 1. Upload the diagnostic script
        local_path = r'c:\SUSTAINAGESERVER\tools\diagnose_routes_remote.py'
        remote_path = '/var/www/sustainage/tools/diagnose_routes_remote.py'
        
        print(f"Uploading {local_path} to {remote_path}...")
        try:
            sftp.mkdir('/var/www/sustainage/tools')
        except OSError:
            pass # Directory likely exists
            
        sftp.put(local_path, remote_path)
        sftp.close()
        
        # 2. Run the diagnostic script
        print("Running diagnostic script...")
        # We need to set PYTHONPATH so it can find web_app.py
        cmd = "export PYTHONPATH=$PYTHONPATH:/var/www/sustainage && python3 /var/www/sustainage/tools/diagnose_routes_remote.py"
        
        stdin, stdout, stderr = client.exec_command(cmd)
        
        # Wait for command to complete
        exit_status = stdout.channel.recv_exit_status()
        
        print("\n--- STDOUT ---")
        print(stdout.read().decode())
        print("\n--- STDERR ---")
        print(stderr.read().decode())
        
        # 3. Check service status just in case
        print("\n--- Service Status ---")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager | head -n 20")
        print(stdout.read().decode())

        client.close()
        
    except Exception as e:
        print(f"Connection/Execution failed: {e}")

if __name__ == "__main__":
    run_remote_diagnosis()
