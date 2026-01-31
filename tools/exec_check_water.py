
import paramiko
import os

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_remote_check():
    try:
        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # SFTP client to upload script
        sftp = client.open_sftp()
        local_script = r'c:\SUSTAINAGESERVER\tools\check_water_schema.py'
        remote_script = '/var/www/sustainage/tools/check_water_schema.py'
        
        # Ensure tools directory exists
        try:
            sftp.stat('/var/www/sustainage/tools')
        except FileNotFoundError:
            sftp.mkdir('/var/www/sustainage/tools')
            
        print(f"Uploading {local_script} to {remote_script}...")
        sftp.put(local_script, remote_script)
        sftp.close()
        
        # Run the script
        print("Running remote check script...")
        stdin, stdout, stderr = client.exec_command(f'python3 {remote_script}')
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        print("Output:")
        print(output)
        
        if error:
            print("Error:")
            print(error)
            
        client.close()
        
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    run_remote_check()
