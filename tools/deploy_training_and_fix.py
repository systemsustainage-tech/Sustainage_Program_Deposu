import paramiko
import os
import sys
import time
from scp import SCPClient

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"
REMOTE_PATH = "/var/www/sustainage"

FILES_TO_DEPLOY = [
    ("backend/modules/training/training_manager.py", "backend/modules/training/training_manager.py"),
    ("tools/fix_remote_schema_others.py", "tools/fix_remote_schema_others.py"),
]

def create_ssh_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, username=USER, password=PASS)
        return client
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

def deploy():
    print(f"Connecting to {HOST}...")
    ssh = create_ssh_client()
    
    print("Uploading files...")
    with SCPClient(ssh.get_transport()) as scp:
        for local, remote in FILES_TO_DEPLOY:
            local_path = os.path.join("c:/SUSTAINAGESERVER", local)
            remote_full_path = f"{REMOTE_PATH}/{remote}"
            print(f"Uploading {local} -> {remote_full_path}")
            scp.put(local_path, remote_full_path)
    
    print("Running schema fix script...")
    stdin, stdout, stderr = ssh.exec_command(f"python3 {REMOTE_PATH}/tools/fix_remote_schema_others.py")
    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(f"Schema fix errors: {err}")

    print("Restarting service...")
    stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage.service")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print("Service restarted successfully.")
    else:
        print(f"Error restarting service: {stderr.read().decode()}")

    ssh.close()
    print("Deployment completed.")

if __name__ == "__main__":
    deploy()
