import paramiko

def read_base():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Reading /var/www/sustainage/templates/base.html...")
        stdin, stdout, stderr = client.exec_command("cat /var/www/sustainage/templates/base.html")
        content = stdout.read().decode()
        print(content)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    read_base()
