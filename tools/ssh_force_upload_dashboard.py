
import paramiko
import os

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def force_upload():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    sftp = client.open_sftp()
    
    local_path = r'c:\SDG\server\templates\dashboard.html'
    remote_path = '/var/www/sustainage/templates/dashboard.html'
    
    print(f"Uploading {local_path} to {remote_path}...")
    sftp.put(local_path, remote_path)
    print("Upload complete.")
    
    # Verify
    stdin, stdout, stderr = client.exec_command(f'grep carbon_dashboard {remote_path}')
    res = stdout.read().decode()
    if res:
        print(f"FAIL: Found 'carbon_dashboard' in {remote_path}:")
        print(res)
    else:
        print("SUCCESS: 'carbon_dashboard' NOT found (updated correctly).")
        
    client.close()

if __name__ == "__main__":
    force_upload()
