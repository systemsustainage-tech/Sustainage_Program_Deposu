import paramiko
import sys

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_cmd(command):
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        print("Connected.")
        
        print(f"Executing: {command}")
        
        stdin, stdout, stderr = client.exec_command(command)
        
        # Stream output
        print("--- Output ---")
        for line in stdout:
            print(line.strip())
            
        print("--- Errors ---")
        for line in stderr:
            print(f"{line.strip()}", file=sys.stderr)
            
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Command executed successfully.")
        else:
            print(f"Command failed with exit status {exit_status}")
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        run_remote_cmd(cmd)
    else:
        print("Usage: python run_remote_cmd.py <command>")
