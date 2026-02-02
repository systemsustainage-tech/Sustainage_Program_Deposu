import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
REMOTE_PATH = "/var/www/sustainage"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def run_remote_optimization():
    print(f"Connecting to {HOST} for post-deploy optimization...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        
        commands = [
            # 1. Install new requirements (Flask-Compress)
            f"cd {REMOTE_PATH} && ./venv/bin/pip install -r requirements.txt",
            
            # 2. Run DB Optimization (WAL Mode)
            f"cd {REMOTE_PATH} && ./venv/bin/python tools/optimize_db.py",
            
            # 3. Restart Service to apply Gunicorn config and code changes
            "systemctl restart sustainage"
        ]
        
        for cmd in commands:
            print(f"Running: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status == 0:
                print("✅ Success")
                # print(stdout.read().decode())
            else:
                print("❌ Failed")
                print(stderr.read().decode())
                
        ssh.close()
        print("Remote optimization finished.")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    run_remote_optimization()
