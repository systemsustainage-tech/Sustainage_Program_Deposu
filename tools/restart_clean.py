import paramiko
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def restart_clean():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, username=USERNAME, password=PASS)
    
    print("Stopping service...")
    client.exec_command('systemctl stop sustainage')
    time.sleep(2)
    
    print("Killing any remaining gunicorn processes...")
    client.exec_command('pkill gunicorn')
    time.sleep(1)
    
    print("Cleaning pycache...")
    client.exec_command('find /var/www/sustainage -name "__pycache__" -type d -exec rm -rf {} +')
    
    print("Starting service...")
    client.exec_command('systemctl start sustainage')
    time.sleep(3)
    
    print("Checking status...")
    stdin, stdout, stderr = client.exec_command('systemctl status sustainage')
    print(stdout.read().decode())
    
    client.close()

if __name__ == '__main__':
    restart_clean()
