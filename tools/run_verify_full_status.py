import paramiko
import sys

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def run_remote_verification():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        cmd = "python3 /var/www/sustainage/tools/verify_full_status_remote.py"
        
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print("STDERR:", err)
        
        client.close()

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    run_remote_verification()
