
import paramiko
import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_user_companies_remote():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # Check user_companies for user_id 1000 (__super__)
        query = "SELECT * FROM user_companies WHERE user_id = 1000;"
        
        cmd = f"sqlite3 {remote_db_path} \"{query}\""
        print(f"Executing: {cmd}")
        
        stdin, stdout, stderr = client.exec_command(cmd)
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if error:
            print(f"Error: {error}")
        
        print("\nResults for user_id 1000:")
        print(output)
        
        if not output.strip():
            print("FAILURE: No company assigned to __super__ (user_id 1000).")
        else:
            print("SUCCESS: Company assigned.")
            
    except Exception as e:
        print(f"Check failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_user_companies_remote()
