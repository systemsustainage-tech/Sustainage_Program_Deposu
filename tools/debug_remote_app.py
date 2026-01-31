import paramiko
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def debug_app():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        print("Running web_app.py manually...")
        # Activate venv and run
        cmd = "cd /var/www/sustainage && . venv/bin/activate && python web_app.py"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        # Stream output
        print("--- STDOUT ---")
        print(stdout.read().decode())
        print("--- STDERR ---")
        print(stderr.read().decode())
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    debug_app()
