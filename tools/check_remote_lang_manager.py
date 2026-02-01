import paramiko
import sys

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"
REMOTE_FILE = "/var/www/sustainage/backend/core/language_manager.py"

def read_remote_file():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        sftp = client.open_sftp()
        try:
            with sftp.open(REMOTE_FILE, 'r') as f:
                print(f"--- Content of {REMOTE_FILE} ---")
                print(f.read().decode())
        except FileNotFoundError:
            print(f"File not found: {REMOTE_FILE}")
        finally:
            sftp.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    read_remote_file()
