import paramiko
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_commands():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        
        commands = [
            "python3 /var/www/sustainage/tools/init_missing_tables.py",
            "python3 /var/www/sustainage/tools/debug_remote_issues.py"
        ]
        
        for cmd in commands:
            print(f"\nExecuting: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            
            # Wait for command to finish and get exit status
            exit_status = stdout.channel.recv_exit_status()
            
            out = stdout.read().decode('utf-8')
            err = stderr.read().decode('utf-8')
            
            print("Output:")
            print(out)
            
            if err:
                print("Errors:")
                print(err)
                
            if exit_status != 0:
                print(f"Command failed with exit status {exit_status}")
            else:
                print("Command completed successfully.")
                
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    run_remote_commands()
