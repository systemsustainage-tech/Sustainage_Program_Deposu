
import paramiko
import sys
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_schema_check():
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, username=username, password=password)
        
        # Upload check script
        sftp = client.open_sftp()
        local_path = r'c:\SUSTAINAGESERVER\tools\check_remote_schema.py'
        remote_path = '/var/www/sustainage/tools/check_remote_schema.py'
        print(f"Uploading {local_path} to {remote_path}...")
        try:
            sftp.mkdir('/var/www/sustainage/tools')
        except IOError:
            pass # Directory might exist
        sftp.put(local_path, remote_path)
        sftp.close()

        print("Running check_remote_schema.py on remote...")
        stdin, stdout, stderr = client.exec_command('python3 /var/www/sustainage/tools/check_remote_schema.py')
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        print("Output:")
        print(output)
        if error:
            print("Error:")
            print(error)
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_schema_check()
