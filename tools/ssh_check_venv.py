
import paramiko

# SSH Credentials
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def check_venv():
    print(f"Connecting to {HOST}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS)
    
    print("Checking gunicorn...")
    stdin, stdout, stderr = ssh.exec_command("ls -l /var/www/sustainage/venv/bin/gunicorn")
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    print("Checking web_app.py...")
    stdin, stdout, stderr = ssh.exec_command("ls -l /var/www/sustainage/server/web_app.py")
    print(stdout.read().decode())
    print(stderr.read().decode())

    print("Checking /var/www/sustainage/server directory...")
    stdin, stdout, stderr = ssh.exec_command("ls -la /var/www/sustainage/server")
    print(stdout.read().decode())
    
    ssh.close()

if __name__ == "__main__":
    check_venv()
