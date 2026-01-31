import paramiko

def read_data_header():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("Reading first 50 lines of /var/www/sustainage/templates/data.html...")
        stdin, stdout, stderr = client.exec_command("head -n 50 /var/www/sustainage/templates/data.html")
        content = stdout.read().decode()
        print(content)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    read_data_header()
