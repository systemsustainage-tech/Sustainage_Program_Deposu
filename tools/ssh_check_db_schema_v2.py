import paramiko
import sys

# Server Details
HOST = "72.62.150.207"
USER = "root"
KEY = "Z/2m?-JDp5VaX6q+HO(b"
DB_PATH = "/var/www/sustainage/backend/data/sdg_desktop.sqlite"

def check_schema():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=KEY)
        
        # Check if DB file exists
        stdin, stdout, stderr = ssh.exec_command(f"ls -l {DB_PATH}")
        print(f"DB File: {stdout.read().decode().strip()}")
        
        # Check tables
        print("\nTables:")
        stdin, stdout, stderr = ssh.exec_command(f"sqlite3 {DB_PATH} .tables")
        print(stdout.read().decode())
        
        # Check carbon_emissions columns
        print("\ncarbon_emissions columns:")
        stdin, stdout, stderr = ssh.exec_command(f"sqlite3 {DB_PATH} 'PRAGMA table_info(carbon_emissions);'")
        print(stdout.read().decode())
        
        # Check carbon_targets columns
        print("\ncarbon_targets columns:")
        stdin, stdout, stderr = ssh.exec_command(f"sqlite3 {DB_PATH} 'PRAGMA table_info(carbon_targets);'")
        print(stdout.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"Schema check failed: {e}")

if __name__ == "__main__":
    check_schema()
