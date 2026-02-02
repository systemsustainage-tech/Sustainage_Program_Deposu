import paramiko
import json
import os
import sys

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

REMOTE_BASE = "/var/www/sustainage"
LOCAL_BASE = "C:\\SUSTAINAGESERVER"

def deploy_cleanup():
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cleanup_report.json')
    if not os.path.exists(report_path):
        print("Report file not found.")
        return

    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        sftp = ssh.open_sftp()

        # 1. Upload updated translation files
        print("Uploading updated translation files...")
        files_to_upload = [
            ('locales/tr.json', 'locales/tr.json'),
            ('locales/en.json', 'locales/en.json')
        ]
        
        for local_rel, remote_rel in files_to_upload:
            local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), local_rel)
            remote_path = f"{REMOTE_BASE}/{remote_rel}"
            if os.path.exists(local_path):
                print(f"Uploading {local_path} to {remote_path}...")
                sftp.put(local_path, remote_path)
            else:
                print(f"Local file not found: {local_path}")

        # 2. Delete unused remote files
        print("Deleting unused remote files...")
        unused_static = report.get('unused_static', [])
        for local_abs_path in unused_static:
            # Convert local absolute path to remote path
            # Expected format: C:\SUSTAINAGESERVER\static\...\file.png
            # Remove LOCAL_BASE and convert slashes
            
            # Normalize paths to handle case insensitivity on Windows but preservation
            # Assume local_abs_path starts with C:\SUSTAINAGESERVER
            
            if local_abs_path.upper().startswith(LOCAL_BASE.upper()):
                rel_path = local_abs_path[len(LOCAL_BASE):]
                if rel_path.startswith('\\'):
                    rel_path = rel_path[1:]
                
                # Convert backslashes to forward slashes
                remote_rel_path = rel_path.replace('\\', '/')
                remote_full_path = f"{REMOTE_BASE}/{remote_rel_path}"
                
                print(f"Deleting remote file: {remote_full_path}")
                cmd = f"rm -f \"{remote_full_path}\""
                stdin, stdout, stderr = ssh.exec_command(cmd)
                exit_status = stdout.channel.recv_exit_status()
                if exit_status != 0:
                     print(f"Failed to delete {remote_full_path}: {stderr.read().decode()}")
            else:
                print(f"Skipping path outside project root: {local_abs_path}")

        # 3. Restart Service
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Failed to restart service: {stderr.read().decode()}")

        sftp.close()
        ssh.close()
        print("Deployment and cleanup complete.")

    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    deploy_cleanup()
