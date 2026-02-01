import paramiko

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"
REMOTE_FILE = "/var/www/sustainage/backend/modules/ai/ai_manager.py"

def read_remote_ai_manager():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        
        sftp = client.open_sftp()
        with sftp.open(REMOTE_FILE, 'r') as f:
            print(f"--- Content of {REMOTE_FILE} ---")
            print(f.read().decode())
        sftp.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    read_remote_ai_manager()
