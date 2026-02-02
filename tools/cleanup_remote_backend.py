import paramiko
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

DIRS_TO_REMOVE = [
    "/var/www/sustainage/backend/modules/supplier_portal"
]

def cleanup_remote_backend():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("Cleaning up unused backend modules on remote...")
        for dir_path in DIRS_TO_REMOVE:
            cmd = f"rm -rf {dir_path}"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()
            if exit_status == 0:
                print(f"Removed directory: {dir_path}")
            else:
                print(f"Failed to remove directory {dir_path}: {stderr.read().decode()}")
        
        ssh.close()
        print("Remote backend cleanup complete.")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    cleanup_remote_backend()
