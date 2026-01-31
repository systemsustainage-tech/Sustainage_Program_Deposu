import paramiko
import sys
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def run_remote_script(remote_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        print(f"Executing {remote_path}...")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_path}")
        
        # Stream output
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end='')
            if stderr.channel.recv_ready():
                print(stderr.channel.recv(1024).decode(), end='')
            time.sleep(0.1)
            
        print(stdout.read().decode(), end='')
        print(stderr.read().decode(), end='')
        
        exit_status = stdout.channel.recv_exit_status()
        print(f"\nExit status: {exit_status}")
        
    except Exception as e:
        print(f"Execution failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_remote_script.py <remote_path_to_script>")
        sys.exit(1)
    
    script_path = sys.argv[1]
    run_remote_script(script_path)
