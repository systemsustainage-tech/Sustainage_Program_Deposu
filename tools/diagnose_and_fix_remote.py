import paramiko
import os

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_diagnostics():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        print("Connected.")
        
        # 1. Fix Permissions for Images
        print("\n--- Fixing Permissions for Static Images ---")
        cmd_perm = "chmod -R 755 /var/www/sustainage/static/images"
        stdin, stdout, stderr = ssh.exec_command(cmd_perm)
        print("Permissions updated.")
        
        # 2. Upload reset script
        print("\n--- Uploading reset_super_remote.py ---")
        sftp = ssh.open_sftp()
        local_path = r'c:\SUSTAINAGESERVER\tools\reset_super_remote.py'
        remote_path = '/var/www/sustainage/tools/reset_super_remote.py'
        sftp.put(local_path, remote_path)
        sftp.close()
        print("Uploaded.")
        
        # 3. Run reset script
        print("\n--- Running reset_super_remote.py ---")
        stdin, stdout, stderr = ssh.exec_command(f"python3 {remote_path}")
        print("Output:")
        print(stdout.read().decode())
        print("Errors:")
        print(stderr.read().decode())

        # 4. Check if images are accessible via Nginx check (simulate ls)
        # Nginx config usually maps /static to /var/www/sustainage/static
        # If user says "broken", it might be missing images too.
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    run_diagnostics()
