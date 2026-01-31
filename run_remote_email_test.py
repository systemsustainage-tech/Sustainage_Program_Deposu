import paramiko
import os
import time

# Server Details
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

REMOTE_DIR = '/var/www/sustainage'
TEST_SCRIPT = 'send_test_email_remote.py'

def run_test():
    try:
        print(f"Connecting to {HOST}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        # Check/Install python-dotenv
        print("Checking python-dotenv...")
        stdin, stdout, stderr = client.exec_command(f"{REMOTE_DIR}/venv/bin/pip install python-dotenv")
        exit_code = stdout.channel.recv_exit_status()
        if exit_code == 0:
            print("python-dotenv installed/verified.")
        else:
            print(f"Error installing python-dotenv: {stderr.read().decode()}")

        sftp = client.open_sftp()
        
        # Upload test script
        local_path = os.path.join(os.getcwd(), TEST_SCRIPT)
        remote_path = f"{REMOTE_DIR}/{TEST_SCRIPT}"
        print(f"Uploading {TEST_SCRIPT} to {remote_path}...")
        sftp.put(local_path, remote_path)
        
        sftp.close()
        
        # Run test script
        print("Running test script...")
        cmd = f"{REMOTE_DIR}/venv/bin/python {remote_path}"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        print("--- Output ---")
        print(stdout.read().decode())
        print("--- Error ---")
        print(stderr.read().decode())
        
        # Clean up
        # client.exec_command(f"rm {remote_path}")
        
        client.close()
        print("Test complete.")

    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    run_test()
