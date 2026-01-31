import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def debug():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    print("--- Checking Permissions ---")
    stdin, stdout, stderr = client.exec_command('ls -ld /var/www/sustainage/uploads')
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    stdin, stdout, stderr = client.exec_command('ls -ld /var/www/sustainage/uploads/reports')
    print(stdout.read().decode())

    print("--- Checking Logs (web_app.log) ---")
    stdin, stdout, stderr = client.exec_command('tail -n 50 /var/www/sustainage/logs/web_app.log')
    print(stdout.read().decode())
    
    print("--- Checking Journalctl (last 50 lines) ---")
    stdin, stdout, stderr = client.exec_command('journalctl -u sustainage -n 50 --no-pager')
    print(stdout.read().decode())

    client.close()

if __name__ == '__main__':
    debug()