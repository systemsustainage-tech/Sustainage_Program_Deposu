import paramiko
import sys

# Remote server details
hostname = '72.62.150.207'
username = 'root'
password = 'Z/2m?-JDp5VaX6q+HO(b)'

def fix_permissions():
    print(f"Connecting to {hostname}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        
        print("Fixing permissions...")
        cmds = [
            "chown -R www-data:www-data /var/www/sustainage/backend/data",
            "chmod -R 775 /var/www/sustainage/backend/data",
            "ls -la /var/www/sustainage/backend/data"
        ]
        
        for cmd in cmds:
            print(f"Running: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            out = stdout.read().decode()
            err = stderr.read().decode()
            if out: print(out)
            if err: print(err)
            
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    fix_permissions()