import paramiko
import sys
import os

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def update_config():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        
        sftp = ssh.open_sftp()
        
        local_gunicorn = "c:/SUSTAINAGESERVER/gunicorn_config.py"
        remote_gunicorn = "/var/www/sustainage/gunicorn_config.py"
        print(f"Uploading {local_gunicorn} -> {remote_gunicorn}")
        sftp.put(local_gunicorn, remote_gunicorn)
        
        local_service = "c:/SUSTAINAGESERVER/sustainage.service"
        remote_service = "/etc/systemd/system/sustainage.service"
        print(f"Uploading {local_service} -> {remote_service}")
        sftp.put(local_service, remote_service)
        
        sftp.close()
        
        cmds = [
            "systemctl daemon-reload",
            "systemctl restart sustainage",
            "systemctl status sustainage --no-pager"
        ]
        
        for cmd in cmds:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out = stdout.read().decode()
            err = stderr.read().decode()
            if out: print(out)
            if err: print(f"STDERR: {err}")
            
        ssh.close()
        print("Update complete.")
        
    except Exception as e:
        print(f"Operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_config()
