import paramiko
import sys
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_setup():
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Running setup_test_user.py on remote...")
        stdin, stdout, stderr = client.exec_command('python3 /var/www/sustainage/tools/setup_test_user.py')
        
        # Wait for completion
        exit_status = stdout.channel.recv_exit_status()
        print(f"Command finished with exit status: {exit_status}")
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        print("Output:")
        print(output)
        if error:
            print("Error:")
            print(error)
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_remote_setup()
