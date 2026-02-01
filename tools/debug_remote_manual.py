import paramiko
import time

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def debug_manual():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, password=PASS)
        print("Connected. Running web_app.py manually...")
        
        # Run python web_app.py and capture output. 
        # We use timeout because if it works it runs forever.
        # So we expect it to fail quickly if there is an error.
        
        cmd = "cd /var/www/sustainage && /var/www/sustainage/venv/bin/python web_app.py"
        
        # Execute command
        # We can't use exec_command easily for long running process if we want to see output and kill it.
        # But if it crashes, it will exit.
        
        stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
        
        print("\n--- STDOUT ---")
        print(stdout.read().decode())
        
        print("\n--- STDERR ---")
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    debug_manual()
