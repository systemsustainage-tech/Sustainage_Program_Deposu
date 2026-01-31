
import paramiko
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Check web_app.py timestamp
        stdin, stdout, stderr = client.exec_command("ls -l /var/www/sustainage/web_app.py")
        print("Remote web_app.py:")
        print(stdout.read().decode())
        
        # Check service status
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage | grep Active")
        print("Service Status:")
        print(stdout.read().decode())
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check()
