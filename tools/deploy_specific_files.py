import paramiko
import os
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy(files):
    if not files:
        print("No files provided for deployment.")
        return

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    connected = False
    for attempt in range(3):
        try:
            print(f"Connecting to {HOSTNAME} (Attempt {attempt+1}/3)...")
            client.connect(HOSTNAME, username=USERNAME, password=PASSWORD, banner_timeout=30)
            connected = True
            break
        except Exception as e:
            print(f"Connection failed: {e}")
            import time
            time.sleep(2)
            
    if not connected:
        print("Could not connect after 3 attempts.")
        return

    try:
        sftp = client.open_sftp()
        
        for local_path in files:
            # Normalize path for Windows
            local_path = os.path.abspath(local_path)
            
            # Determine remote path
            # Assuming local project root is c:\SUSTAINAGESERVER and remote is /var/www/sustainage
            rel_path = os.path.relpath(local_path, 'c:\\SUSTAINAGESERVER')
            remote_path = '/var/www/sustainage/' + rel_path.replace('\\', '/')
            
            print(f"Uploading {local_path} to {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"Failed to upload {local_path}: {e}")
        
        sftp.close()
        
        print("Restarting services...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Services restarted successfully.")
        else:
            print("Error restarting services:")
            print(stderr.read().decode())
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_specific_files.py <file1> <file2> ...")
        sys.exit(1)
    
    files_to_deploy = sys.argv[1:]
    deploy(files_to_deploy)
