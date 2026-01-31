import paramiko

def read_dashboard_rest():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        with sftp.open("/var/www/sustainage/templates/dashboard.html", "r") as f:
            content = f.read()
            # Skip first 2000 chars and print next 5000 to see module section
            print(content[2000:7000].decode())
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    read_dashboard_rest()
