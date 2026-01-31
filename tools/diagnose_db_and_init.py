import paramiko
import os

def check_remote_schema_and_init():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # Check users schema
        local_path = os.path.join(os.path.dirname(__file__), 'check_users_schema.py')
        remote_path = '/var/www/sustainage/tools/check_users_schema.py'
        
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        
        print("--- Users Schema ---")
        stdin, stdout, stderr = client.exec_command(f"python3 {remote_path}")
        print(stdout.read().decode())
        
        # Check modules init
        print("--- backend/modules Listing ---")
        stdin, stdout, stderr = client.exec_command("ls -la /var/www/sustainage/backend/modules/__init__.py")
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out:
            print(out)
        else:
            print(f"Error/Missing: {err}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_remote_schema_and_init()
