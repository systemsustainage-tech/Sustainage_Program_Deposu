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
        "echo '=== Last 40 lines with /super_admin ==='",
        "grep -n '/super_admin' /var/www/sustainage/logs/error.log | tail -n 40 || echo 'no /super_admin errors'",
        "echo '=== Last 80 lines of error.log ==='",
        "tail -n 80 /var/www/sustainage/logs/error.log"
    ]
    for c in cmds:
        run_command(c)
