import sqlite3
import paramiko
import os

# Remote server configuration
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = os.environ.get('REMOTE_SSH_PASS', 'Kayra_1507')

def check_remote_schema():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Check mapping_suggestions table
        cmd = "sqlite3 /var/www/sustainage/backend/data/sdg_desktop.sqlite \".schema mapping_suggestions\""
        print(f"Running: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode()
        error = stderr.read().decode()
        
        if output.strip():
            print("Table 'mapping_suggestions' EXISTS.")
            print(output)
        else:
            print("Table 'mapping_suggestions' DOES NOT EXIST (or empty schema).")
            
        if error:
            print(f"Error: {error}")
            
        # Check standard_mappings count
        cmd = "sqlite3 /var/www/sustainage/backend/data/sdg_desktop.sqlite \"SELECT COUNT(*) FROM standard_mappings;\""
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"Standard mappings count: {stdout.read().decode().strip()}")
        
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_remote_schema()
