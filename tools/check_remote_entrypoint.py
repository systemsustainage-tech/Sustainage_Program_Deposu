import paramiko

def check_remote_entrypoint():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("--- /etc/systemd/system/sustainage.service ---")
        stdin, stdout, stderr = client.exec_command("cat /etc/systemd/system/sustainage.service")
        print(stdout.read().decode())
        
        print("--- File Listing ---")
        stdin, stdout, stderr = client.exec_command("ls -la /var/www/sustainage/*.py")
        print(stdout.read().decode())
        
        print("--- wsgi.py content (if exists) ---")
        stdin, stdout, stderr = client.exec_command("cat /var/www/sustainage/wsgi.py")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_remote_entrypoint()
