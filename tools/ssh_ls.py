
import paramiko

HOST = "72.62.150.207"
USER = "root"
KEY = "Z/2m?-JDp5VaX6q+HO(b"

def list_files(path):
    print(f"Connecting to {HOST}...")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USER, password=KEY)
        
        print(f"Listing {path}...")
        stdin, stdout, stderr = ssh.exec_command(f"ls -R {path}")
        print(stdout.read().decode())
        
        ssh.close()
    except Exception as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    list_files("/var/www/sustainage/backend")
