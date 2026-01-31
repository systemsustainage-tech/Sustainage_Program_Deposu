import paramiko
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_command():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        print("Connected.")
        
        cmd = "python3 /var/www/sustainage/tools/apply_sdg_2025_remote.py"
        print(f"Running command: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        # Wait for command to complete
        exit_status = stdout.channel.recv_exit_status()
        
        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()
        
        print("Output:")
        print(out)
        if err:
            print("Errors:")
            print(err)
            
        if exit_status == 0:
            print("Command executed successfully.")
        else:
            print(f"Command failed with exit status {exit_status}")
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    run_remote_command()
