import paramiko
import sys
import os

HOST = "72.62.150.207"
USER = "root"
KEY_FILE = os.path.expanduser("~/.ssh/id_rsa")

def run_command(cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, key_filename=KEY_FILE if os.path.exists(KEY_FILE) else None)
        
        print(f"--- Running: {cmd} ---")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"STDERR: {err}")
            
        ssh.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    cmds = [
        "head -n 60 /var/www/sustainage/templates/dashboard.html",
        "cat /var/www/sustainage/gunicorn_config.py",
        "cat /etc/systemd/system/sustainage.service",
        "netstat -tulpn | grep 5000 || ss -tulpn | grep 5000 || echo 'no listener on 5000'",
        "ps aux | grep sustainage | head -n 10"
    ]
    for c in cmds:
        run_command(c)
