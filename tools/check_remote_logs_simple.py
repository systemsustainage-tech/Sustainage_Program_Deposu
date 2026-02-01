import paramiko
import sys

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

def check_logs():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        stdin, stdout, stderr = client.exec_command("journalctl -u sustainage.service -n 50 --no-pager")
        print("--- Recent Logs ---")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_logs()
