
import paramiko
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def fix_permissions():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {HOSTNAME}...")
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        print("Fixing permissions...")
        # Change owner to www-data for the whole directory
        stdin, stdout, stderr = ssh.exec_command('chown -R www-data:www-data /var/www/sustainage')
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Permissions fixed successfully.")
        else:
            print("Error fixing permissions.")
            print(stderr.read().decode())
            
        # Also ensure the database file is writable
        stdin, stdout, stderr = ssh.exec_command('chmod 664 /var/www/sustainage/backend/data/sdg_desktop.sqlite')
        # And directory is writable
        stdin, stdout, stderr = ssh.exec_command('chmod 775 /var/www/sustainage/backend/data')
        
        ssh.close()
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    fix_permissions()
