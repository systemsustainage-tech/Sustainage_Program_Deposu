import paramiko
import os
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def run_verify(local_script_path):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        remote_script_path = '/var/www/sustainage/' + os.path.basename(local_script_path)
        
        print(f"Uploading {local_script_path} to {remote_script_path}...")
        sftp.put(local_script_path, remote_script_path)
        sftp.close()
        
        print(f"Running {remote_script_path}...")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_script_path}")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        print("--- Output ---")
        print(out)
        if err:
            print("--- Errors ---")
            print(err)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_remote_verify.py <local_script>")
    else:
        run_verify(sys.argv[1])
