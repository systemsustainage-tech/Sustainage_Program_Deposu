
import paramiko

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def check_users():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        cmd = 'sqlite3 /var/www/sustainage/data/sdg_desktop.sqlite "SELECT username FROM users;"'
        stdin, stdout, stderr = client.exec_command(cmd)
        
        users = stdout.read().decode().strip()
        errors = stderr.read().decode().strip()
        
        if users:
            print(f"Users found:\n{users}")
        else:
            print("No users found in database.")
            
        if errors:
            print(f"Errors:\n{errors}")
            
        client.close()
    except Exception as e:
        print(f"Failed to check users: {e}")

if __name__ == '__main__':
    check_users()
