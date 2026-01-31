import paramiko
import time

HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = "Z/2m?-JDp5VaX6q+HO(b)"

def list_files():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        cmds = [
            "ls -F /var/www/sustainage/backend/data",
            "ls -l /var/www/sustainage/backend/data/sdg_desktop.sqlite"
        ]
        
        for cmd in cmds:
            print(f"\nRunning: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(stdout.read().decode())
            err = stderr.read().decode()
            if err:
                print(f"Error: {err}")
            
        ssh.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    list_files()
