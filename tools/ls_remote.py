import paramiko
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def ls_remote():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")

        print("Listing backend/security...")
        stdin, stdout, stderr = client.exec_command("find /var/www/sustainage/backend/security -maxdepth 3")
        print(stdout.read().decode())
        
        client.close()
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    ls_remote()
