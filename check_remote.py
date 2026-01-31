import paramiko
import time

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def check_remote():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOST, username=USER, password=PASS)
        
        print("--- Listing /var/www/sustainage ---")
        stdin, stdout, stderr = client.exec_command("ls -F /var/www/sustainage")
        print(stdout.read().decode())
        
        print("--- Listing /var/www/sustainage/backend/data ---")
        stdin, stdout, stderr = client.exec_command("ls -F /var/www/sustainage/backend/data")
        out = stdout.read().decode()
        err = stderr.read().decode()
        print(out)
        if err: print(f"Error: {err}")

        print("--- Checking Process ---")
        stdin, stdout, stderr = client.exec_command("ps aux | grep web_app.py")
        print(stdout.read().decode())

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_remote()
