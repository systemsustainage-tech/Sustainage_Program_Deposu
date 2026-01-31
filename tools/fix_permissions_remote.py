import paramiko
import sys

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def fix_permissions():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")

        print("Fixing permissions...")
        client.exec_command("chown -R www-data:www-data /var/www/sustainage")
        client.exec_command("chmod -R 775 /var/www/sustainage")
        
        # Also restart service to be sure
        print("Restarting service...")
        client.exec_command("systemctl restart sustainage")
        
        client.close()
        print("Done.")
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == '__main__':
    fix_permissions()
