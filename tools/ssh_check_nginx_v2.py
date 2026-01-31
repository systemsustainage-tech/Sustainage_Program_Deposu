
import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check_nginx():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        print("--- LS sites-enabled ---")
        stdin, stdout, stderr = client.exec_command('ls -l /etc/nginx/sites-enabled/')
        print(stdout.read().decode())
        
        print("--- Cat default (if exists) ---")
        stdin, stdout, stderr = client.exec_command('cat /etc/nginx/sites-enabled/default')
        out = stdout.read().decode()
        err = stderr.read().decode()
        print(out)
        if err: print(f"Error: {err}")
        
        print("--- Cat sustainage (if exists) ---")
        stdin, stdout, stderr = client.exec_command('cat /etc/nginx/sites-enabled/sustainage')
        out = stdout.read().decode()
        err = stderr.read().decode()
        print(out)
        if err: print(f"Error: {err}")

        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_nginx()
