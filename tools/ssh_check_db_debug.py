import paramiko
import sys

# Server Details
HOST = "72.62.150.207"
USER = "root"
KEY = "Z/2m?-JDp5VaX6q+HO(b"
DB_PATH = "/var/www/sustainage/data/sdg_desktop.sqlite"

def check_debug():
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=KEY)
        
        # Check sqlite3 version
        print("Checking sqlite3 version:")
        stdin, stdout, stderr = ssh.exec_command("sqlite3 --version")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # Check DB file details
        print(f"Checking {DB_PATH}:")
        stdin, stdout, stderr = ssh.exec_command(f"ls -l {DB_PATH}")
        print(stdout.read().decode())
        
        # Try a simple query
        print("Trying simple query:")
        stdin, stdout, stderr = ssh.exec_command(f"sqlite3 {DB_PATH} 'SELECT 1;'")
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"Check failed: {e}")

if __name__ == "__main__":
    check_debug()
