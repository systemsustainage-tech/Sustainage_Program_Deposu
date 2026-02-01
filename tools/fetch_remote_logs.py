import paramiko
import sys
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

def fetch_logs():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, username=USER, password=PASS)
        
        # Get last 100 lines of service logs
        stdin, stdout, stderr = client.exec_command('journalctl -u sustainage.service -n 100 --no-pager')
        logs = stdout.read().decode('utf-8')
        error_logs = stderr.read().decode('utf-8')
        
        print("--- SERVICE LOGS (LAST 100 LINES) ---")
        print(logs)
        if error_logs:
            print("--- STDERR ---")
            print(error_logs)
            
        client.close()
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_logs()
