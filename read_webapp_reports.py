import paramiko

def read_webapp_reports():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        print("--- web_app.py reports section ---")
        with sftp.open('/var/www/sustainage/web_app.py', 'r') as f:
            content = f.read().decode()
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if 590 <= i <= 650:
                    print(f"{i+1}: {line}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    read_webapp_reports()
