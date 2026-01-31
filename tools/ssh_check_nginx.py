
import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check_nginx():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        print("--- Nginx Config ---")
        stdin, stdout, stderr = client.exec_command('cat /etc/nginx/sites-enabled/default')
        print(stdout.read().decode())
        
        stdin, stdout, stderr = client.exec_command('cat /etc/nginx/nginx.conf')
        # print(stdout.read().decode()) # Might be too long, let's just check sites-enabled first
        
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_nginx()
