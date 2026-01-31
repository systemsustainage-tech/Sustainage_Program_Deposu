
import paramiko
import os
import sys

def check_user_status():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        query = "SELECT id, username, is_active, is_verified, locked_until FROM users WHERE username='__super__';"
        cmd = f"sqlite3 {remote_db_path} \"{query}\""
        print(f"Executing: {cmd}")
        
        stdin, stdout, stderr = client.exec_command(cmd)
        
        output = stdout.read().decode().strip()
        error = stderr.read().decode()
        
        if error:
            print(f"Error: {error}")
        
        print(f"Result: {output}")
        # Expected: 1000|__super__|1|1|
        
    except Exception as e:
        print(f"Check failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_user_status()
