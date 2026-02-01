import paramiko

HOST = "72.62.150.207"
USER = "root"
PASS = "Sustainage123!"

def check_ai_manager_head():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        
        stdin, stdout, stderr = client.exec_command("head -n 50 /var/www/sustainage/backend/modules/ai/ai_manager.py")
        print("--- Head of AI Manager ---")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_ai_manager_head()
