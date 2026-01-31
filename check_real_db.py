import paramiko

def check_real_db():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Checking /var/www/sustainage/backend/data/sdg_desktop.sqlite:")
        stdin, stdout, stderr = client.exec_command("ls -l /var/www/sustainage/backend/data/sdg_desktop.sqlite")
        print(stdout.read().decode())
        print(stderr.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_real_db()
