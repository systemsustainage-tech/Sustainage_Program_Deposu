import paramiko
import time

def restart_service():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        
        # Try to find the service name. It might be 'sustainage' or 'gunicorn' or via systemctl.
        # I'll try standard names or just pkill gunicorn and run the start script if needed.
        # But safer to try systemctl first.
        
        commands = [
            "systemctl restart sustainage",
            "systemctl restart gunicorn",
            "systemctl restart nginx"
        ]
        
        for cmd in commands:
            print(f"Running: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            if out: print(out)
            if err: print(f"Error/Status: {err}")
            
        print("Service restart attempted.")
        
    except Exception as e:
        print(f"Restart failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    restart_service()
