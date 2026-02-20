import paramiko
import os
import time

# Configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def fix_gunicorn_config():
    print(f"Connecting to {HOSTNAME}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Check if key file exists
        key_filename = KEY_FILE if os.path.exists(KEY_FILE) else None
        ssh.connect(HOSTNAME, username=USERNAME, key_filename=key_filename)
        
        print("\n--- Updating gunicorn_config.py ---")
        # Use sed to replace the bind address
        cmd = "sed -i 's/bind = \"0.0.0.0:8000\"/bind = \"127.0.0.1:5000\"/' /var/www/sustainage/gunicorn_config.py"
        print(f"Running: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Config updated successfully.")
        else:
            print(f"Error updating config: {stderr.read().decode()}")
            
        print("\n--- Verifying Config ---")
        stdin, stdout, stderr = ssh.exec_command("grep 'bind =' /var/www/sustainage/gunicorn_config.py")
        print(stdout.read().decode())
        
        print("\n--- Restarting Service ---")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")

        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    fix_gunicorn_config()
