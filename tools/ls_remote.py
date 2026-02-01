import paramiko
import sys

# Server details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def ls_remote(path):
    print(f"Listing {path}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD, look_for_keys=False, allow_agent=False)
        stdin, stdout, stderr = ssh.exec_command(f"ls -F {path}")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error: {err}")
        ssh.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    paths = sys.argv[1:] if len(sys.argv) > 1 else ['/var/www/sustainage/']
    for p in paths:
        ls_remote(p)
