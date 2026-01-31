
import paramiko

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'
REMOTE_FILE = '/var/www/sustainage/web_app.py'

def read_reports_route():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        stdin, stdout, stderr = client.exec_command(f'grep -A 20 "@app.route(\'/reports\')" {REMOTE_FILE}')
        print(stdout.read().decode())
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_reports_route()
