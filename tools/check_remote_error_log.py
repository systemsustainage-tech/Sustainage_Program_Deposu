import paramiko
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

def check_logs():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("--- sustainage.log (Last 50 lines) ---")
        stdin, stdout, stderr = ssh.exec_command("tail -n 50 /var/www/sustainage/sustainage.log")
        print(stdout.read().decode())
        
        print("\n--- Journalctl (Last 20 lines) ---")
        stdin, stdout, stderr = ssh.exec_command("journalctl -u sustainage.service -n 20 --no-pager")
        print(stdout.read().decode())
        
        ssh.close()
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_logs()
