
import paramiko
import os
import sys

def list_companies_remote():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        query = "SELECT id, name FROM companies;"
        cmd = f"sqlite3 {remote_db_path} \"{query}\""
        print(f"Executing: {cmd}")
        
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    list_companies_remote()
