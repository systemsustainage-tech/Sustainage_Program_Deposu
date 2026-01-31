import paramiko
import os

def check_remote_tables():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # Upload the script
        local_path = os.path.join(os.path.dirname(__file__), 'list_remote_tables_script.py')
        remote_path = '/var/www/sustainage/tools/list_remote_tables_script.py'
        
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        
        # Run it
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_path}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_remote_tables()
