
import paramiko
import sys
import time

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def run_init_tables():
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, username=username, password=password)
        
        # Upload script
        sftp = client.open_sftp()
        local_path = r'c:\SUSTAINAGESERVER\tools\init_missing_tables_remote.py'
        remote_path = '/var/www/sustainage/tools/init_missing_tables_remote.py'
        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        sftp.close()

        print("Running init_missing_tables_remote.py on remote...")
        stdin, stdout, stderr = client.exec_command('export PYTHONPATH=/var/www/sustainage && python3 /var/www/sustainage/tools/init_missing_tables_remote.py')
        
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
    run_init_tables()
