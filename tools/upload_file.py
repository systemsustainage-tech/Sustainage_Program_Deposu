import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def upload_file(local_path, remote_path):
    print(f"Uploading {local_path} to {HOST}:{remote_path}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        
        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        ssh.close()
        print("Upload successful.")
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python upload_file.py <local_path> <remote_path>")
    else:
        upload_file(sys.argv[1], sys.argv[2])
