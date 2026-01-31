
import paramiko
import sys
import time

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def fix_templates():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOST}...")
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        sftp = client.open_sftp()
        
        # Files to upload
        files_to_upload = [
            (r'c:\SDG\server\templates\base.html', '/var/www/sustainage/templates/base.html'),
            (r'c:\SDG\server\templates\dashboard.html', '/var/www/sustainage/templates/dashboard.html')
        ]
        
        for local_path, remote_path in files_to_upload:
            print(f"Uploading {local_path} -> {remote_path}...")
            sftp.put(local_path, remote_path)
            print("Done.")
            
        sftp.close()
        
        # Verify fix
        print("Verifying 'carbon_dashboard' removal in base.html...")
        stdin, stdout, stderr = client.exec_command("grep 'carbon_dashboard' /var/www/sustainage/templates/base.html")
        result = stdout.read().decode().strip()
        
        if result:
            print(f"WARNING: 'carbon_dashboard' still found in base.html: {result}")
        else:
            print("SUCCESS: 'carbon_dashboard' not found in base.html.")
            
        # Restart service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print(f"Error restarting service: {stderr.read().decode()}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    fix_templates()
