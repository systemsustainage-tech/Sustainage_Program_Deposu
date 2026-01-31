import paramiko
import sys

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_debug():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        
        # Run the test script
        cmd = "python3 /var/www/sustainage/tools/test_module_data_flow.py"
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        # Print output
        print("\n--- STDOUT ---")
        print(stdout.read().decode('utf-8'))
        
        print("\n--- STDERR ---")
        print(stderr.read().decode('utf-8'))
        
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    run_debug()
