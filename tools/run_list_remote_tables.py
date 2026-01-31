import paramiko
import os

def list_remote_tables():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_dir = '/var/www/sustainage'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # Upload check script
        local_path = os.path.join(os.getcwd(), 'tools/list_remote_tables_script.py')
        remote_path = f"{remote_dir}/tools/list_remote_tables_script.py"
        print(f"Uploading check script to {remote_path}...")
        sftp.put(local_path, remote_path)
        
        # Run it
        print("Running check script...")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_path}")
        out = stdout.read().decode()
        err = stderr.read().decode()
        print("--- Output ---")
        print(out)
        print("--- Error ---")
        print(err)
        
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    list_remote_tables()
