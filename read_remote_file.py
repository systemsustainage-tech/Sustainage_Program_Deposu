import paramiko

def read_remote_file(filename):
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        with sftp.open(f"/var/www/sustainage/templates/{filename}", "r") as f:
            print(f.read().decode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    read_remote_file('data_edit.html')
