import paramiko
import requests
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = '321'

def verify():
    print(f"Connecting to {HOSTNAME}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # 1. Check Service Status
        print("Checking service status...")
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active sustainage.service")
        status = stdout.read().decode().strip()
        print(f"Service status: {status}")
        
        if status != 'active':
            print("ERROR: Service is not active.")
            # Check logs
            stdin, stdout, stderr = ssh.exec_command("journalctl -u sustainage.service -n 20 --no-pager")
            print("Logs:")
            print(stdout.read().decode())
        
        # 2. Check Key Files
        print("Checking key files...")
        files_to_check = [
            '/var/www/sustainage/web_app.py',
            '/var/www/sustainage/backend/modules/reporting/target_manager.py',
            '/var/www/sustainage/templates/targets.html',
            '/var/www/sustainage/templates/biodiversity.html',
            '/var/www/sustainage/templates/supply_chain.html',
            '/var/www/sustainage/templates/social.html'
        ]
        
        for f in files_to_check:
            stdin, stdout, stderr = ssh.exec_command(f"ls -l {f}")
            out = stdout.read().decode().strip()
            if not out:
                print(f"ERROR: File missing: {f}")
            else:
                print(f"OK: {f}")

        # 3. Check Port 5000
        print("Checking port 5000...")
        stdin, stdout, stderr = ssh.exec_command("netstat -tulpn | grep :5000")
        out = stdout.read().decode().strip()
        print(f"Port 5000 status: {out}")
        
    except Exception as e:
        print(f"SSH Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    verify()
