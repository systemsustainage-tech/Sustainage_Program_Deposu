import paramiko
import os
import sys

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")
REMOTE_BASE = "/var/www/sustainage"

FILES_TO_UPLOAD = [
    "tools/reset_remote_admin.py"
]

def upload_files():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        sftp = ssh.open_sftp()
        
        print(f"Connected to {HOST}...")
        
        for file_rel_path in FILES_TO_UPLOAD:
            local_path = os.path.join("c:\\SUSTAINAGESERVER", file_rel_path)
            remote_path = f"{REMOTE_BASE}/{file_rel_path.replace(os.sep, '/')}"
            
            if os.path.exists(local_path):
                print(f"Uploading {file_rel_path} to {remote_path}...")
                sftp.put(local_path, remote_path)
            else:
                print(f"Warning: Local file not found: {local_path}")
                
        print("All files uploaded.")
        
        # Run the reset script
        print("Running reset script on remote server...")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {REMOTE_BASE}/tools/reset_remote_admin.py")
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        print("Output:", output)
        if error:
            print("Error:", error)
            
        exit_status = stdout.channel.recv_exit_status()
        
        sftp.close()
        ssh.close()
        
        return exit_status == 0
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

if __name__ == "__main__":
    if upload_files():
        sys.exit(0)
    else:
        sys.exit(1)
