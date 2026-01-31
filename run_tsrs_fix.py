import paramiko
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_fix():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username, password=password)
        
        print("Executing reinit_tsrs_remote.py on remote server...")
        # We need to set PYTHONPATH so it can find backend modules if needed, 
        # though the script might handle imports relative to project root if run from there.
        # Let's run it from /var/www/sustainage
        command = "cd /var/www/sustainage && python3 tools/reinit_tsrs_remote.py"
        
        stdin, stdout, stderr = ssh.exec_command(command)
        
        # Stream output
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode(), end='')
            if stderr.channel.recv_ready():
                print(stderr.channel.recv(1024).decode(), end='')
            time.sleep(0.1)
            
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("TSRS Fix Script finished successfully.")
        else:
            print(f"TSRS Fix Script failed with exit code {exit_status}")
            
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == '__main__':
    run_fix()
