import paramiko

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def fix_permissions():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(HOST, username=USER, password=PASS)
        print("Connected.")
        
        # 1. Identify service user (guess www-data)
        # 2. Fix permissions
        
        commands = [
            "chown -R www-data:www-data /var/www/sustainage",
            "chmod -R 755 /var/www/sustainage",
            "chmod -R 777 /var/www/sustainage/backend/data", # DB needs write
            "chmod 666 /var/www/sustainage/backend/data/*.sqlite",
            "chmod 666 /var/www/sustainage/backend/data/*.db",
            "systemctl restart sustainage"
        ]
        
        for cmd in commands:
            print(f"Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode()
            err = stderr.read().decode()
            if out: print(out)
            if err: print(f"Error: {err}")
            
        # Check status
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_permissions()
