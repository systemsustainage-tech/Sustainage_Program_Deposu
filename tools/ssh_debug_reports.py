
import paramiko

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check_server():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        # Check service status
        print("--- Service Status ---")
        stdin, stdout, stderr = client.exec_command('systemctl status sustainage')
        print(stdout.read().decode())
        
        # Check logs (last 50 lines)
        print("\n--- Journal Logs ---")
        stdin, stdout, stderr = client.exec_command('journalctl -u sustainage -n 50 --no-pager')
        print(stdout.read().decode())
        
        # Check reports.html existence
        print("\n--- Checking reports.html ---")
        stdin, stdout, stderr = client.exec_command('ls -l /var/www/sustainage/templates/reports.html')
        out = stdout.read().decode()
        err = stderr.read().decode()
        if out:
            print(f"Found: {out}")
        else:
            print(f"Not Found: {err}")
            
        client.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_server()
