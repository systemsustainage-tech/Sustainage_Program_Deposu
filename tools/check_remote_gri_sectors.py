
import paramiko
import sqlite3
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def check_remote_gri_sectors():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    remote_db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    
    print(f"Connecting to {hostname}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # Check if gri_standards has sectors
        query = "SELECT code, sector FROM gri_standards WHERE code IN ('GRI 11', 'GRI 12', 'GRI 13', 'GRI 14', 'GRI 101', 'GRI 103');"
        
        cmd = f"sqlite3 {remote_db_path} \"{query}\""
        print(f"Executing: {cmd}")
        
        stdin, stdout, stderr = client.exec_command(cmd)
        
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if error:
            print(f"Error: {error}")
        
        print("\nResults:")
        print(output)
        
        if "Oil & Gas" in output and "Coal" in output:
            print("SUCCESS: Remote DB has correct sectors.")
        else:
            print("FAILURE: Remote DB missing sectors.")
            
    except Exception as e:
        print(f"Check failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_remote_gri_sectors()
