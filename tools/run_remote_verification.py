
import paramiko
import os

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy_and_run_verification():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")
        
        sftp = client.open_sftp()
        
        # Upload setup script
        local_setup = r'c:\SDG\tools\setup_test_user.py'
        remote_setup = '/var/www/sustainage/setup_test_user.py'
        print("Uploading setup script...")
        sftp.put(local_setup, remote_setup)
        
        # Upload verification script
        local_verify = r'c:\SDG\tools\verify_remote.py'
        remote_verify = '/var/www/sustainage/verify_remote.py'
        print("Uploading verification script...")
        sftp.put(local_verify, remote_verify)
        
        sftp.close()
        
        # Run setup
        print("\n--- Running Setup ---")
        stdin, stdout, stderr = client.exec_command(f'python3 {remote_setup}')
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err: print(f"Setup Errors: {err}")
        
        # Run verify
        print("\n--- Running Verification ---")
        stdin, stdout, stderr = client.exec_command(f'python3 {remote_verify}')
        out = stdout.read().decode()
        print(out)
        err = stderr.read().decode()
        if err: print(f"Verification Errors: {err}")
        
        client.close()
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    deploy_and_run_verification()
