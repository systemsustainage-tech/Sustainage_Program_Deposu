
import paramiko
import time

# SSH Credentials
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_BASE = '/var/www/sustainage'

def run_cmd(ssh, cmd):
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print(f"Error ({exit_status}): {stderr.read().decode()}")
    return exit_status

def fix_permissions_properly():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    
    # 1. Ownership
    run_cmd(ssh, f"chown -R www-data:www-data {REMOTE_BASE}")
    
    # 2. Base permissions (Blocking)
    run_cmd(ssh, f"find {REMOTE_BASE} -type d -exec chmod 755 {{}} +")
    run_cmd(ssh, f"find {REMOTE_BASE} -type f -exec chmod 644 {{}} +")
    
    # 3. Restore executable permissions (Blocking)
    gunicorn_path = "/var/www/sustainage/venv/bin/gunicorn"
    run_cmd(ssh, f"chmod +x {gunicorn_path}")
    run_cmd(ssh, "chmod +x /var/www/sustainage/venv/bin/*")
    
    # 4. Verify
    print("Verifying permissions...")
    stdin, stdout, stderr = ssh.exec_command(f"ls -l {gunicorn_path}")
    print(stdout.read().decode())
    
    # 5. Restart Service
    print("Restarting service...")
    run_cmd(ssh, "systemctl restart sustainage")
    
    ssh.close()

if __name__ == "__main__":
    fix_permissions_properly()
