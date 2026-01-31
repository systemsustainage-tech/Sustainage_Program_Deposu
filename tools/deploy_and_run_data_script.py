import paramiko
import os
import time

HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = os.environ.get("REMOTE_SSH_PASS", "Kayra_1507")

def run_script():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        local_path = 'tools/remote_add_social_data.py'
        remote_path = '/var/www/sustainage/remote_add_social_data.py'
        
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        
        # Also upload get_flask_error.py again just in case (with the logging fix)
        print("Uploading updated get_flask_error.py...")
        sftp.put('tools/get_flask_error.py', '/var/www/sustainage/get_flask_error.py')
        
        sftp.close()
        
        print("Running data insertion script...")
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/remote_add_social_data.py")
        print("--- Output ---")
        print(stdout.read().decode())
        print("--- Errors ---")
        print(stderr.read().decode())
        
        print("\nVerifying with get_flask_error.py...")
        stdin, stdout, stderr = client.exec_command("python3 /var/www/sustainage/get_flask_error.py")
        print("--- Output ---")
        print(stdout.read().decode())
        print("--- Errors ---")
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_script()
