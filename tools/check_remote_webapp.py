
import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Sustainage123!'

def check_remote_file():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    print("Checking 'risk_filter' in remote web_app.py...")
    stdin, stdout, stderr = ssh.exec_command("grep -c 'risk_filter' /var/www/sustainage/web_app.py")
    count = stdout.read().decode().strip()
    print(f"Count: {count}")
    
    ssh.close()

if __name__ == "__main__":
    check_remote_file()
