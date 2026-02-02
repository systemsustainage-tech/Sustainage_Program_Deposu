import paramiko
import time

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

def check_service():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {HOST}...")
        ssh.connect(HOST, username=USER, password=PASS)
        
        print("Checking service status...")
        stdin, stdout, stderr = ssh.exec_command("systemctl status sustainage.service")
        
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        
        print("\n--- Service Status ---")
        print(out)
        if err:
            print("\n--- Errors ---")
            print(err)
            
        ssh.close()
        
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    check_service()
