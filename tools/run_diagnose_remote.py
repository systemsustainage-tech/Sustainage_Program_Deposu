import paramiko
import os

hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

local_file = 'c:/SUSTAINAGESERVER/tools/diagnose_remote_db.py'
remote_file = '/var/www/sustainage/tools/diagnose_remote_db.py'

def run():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        print(f"Uploading {local_file} to {remote_file}...")
        sftp.put(local_file, remote_file)
        sftp.close()
        
        print(f"Executing {remote_file}...")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_file}")
        
        out = stdout.read().decode('utf-8')
        err = stderr.read().decode('utf-8')
        
        print("\n--- OUTPUT ---")
        print(out)
        if err:
            print("\n--- ERROR ---")
            print(err)
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run()
