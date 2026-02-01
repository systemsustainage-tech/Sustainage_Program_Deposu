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
        print("Connected. Running web_app.py manually (unbuffered)...")
        
        cmd = "cd /var/www/sustainage && /var/www/sustainage/venv/bin/python -u web_app.py"
        
        stdin, stdout, stderr = client.exec_command(cmd)
        
        # Wait a bit for output
        time.sleep(5)
        
        # Check if it has exited
        if stdout.channel.exit_status_ready():
            print("Process exited with status:", stdout.channel.recv_exit_status())
        else:
            print("Process is still running.")
        
        print("\n--- STDOUT ---")
        # Read available data (loop a bit to get all)
        while stdout.channel.recv_ready():
            print(stdout.channel.recv(1024).decode(), end='')
        
        print("\n\n--- STDERR ---")
        while stderr.channel.recv_ready():
            print(stderr.channel.recv(1024).decode(), end='')
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    debug_manual()
