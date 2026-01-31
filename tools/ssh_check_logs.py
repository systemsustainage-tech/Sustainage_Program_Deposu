import paramiko
import sys

# Server Details
HOST = "72.62.150.207"
USER = "root"
KEY = "Z/2m?-JDp5VaX6q+HO(b"

def check_logs():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=KEY)
        
        # Check Flask/Gunicorn logs (assuming journalctl or file)
        # Service is 'sustainage'
        print("Checking service logs (last 50 lines)...")
        stdin, stdout, stderr = ssh.exec_command("journalctl -u sustainage -n 50 --no-pager")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # Also check if there are any specific error files if configured
        # In web_app.py we saw: log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        # /var/www/sustainage/logs
        print("\nChecking application logs in /var/www/sustainage/logs...")
        stdin, stdout, stderr = ssh.exec_command("ls -lt /var/www/sustainage/logs | head -n 5")
        files = stdout.read().decode()
        print(files)
        
        if files:
            # Read the latest log file if exists (assuming standard naming or just cat * if small)
            # Safe bet: just list for now. If there's a recent one, maybe read tail.
            pass
            
        ssh.close()
    except Exception as e:
        print(f"Log check failed: {e}")

if __name__ == "__main__":
    check_logs()
