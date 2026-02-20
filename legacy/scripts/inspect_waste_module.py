import paramiko

def inspect_waste_module():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        # 1. Read waste.html
        print("--- waste.html ---")
        with sftp.open('/var/www/sustainage/templates/waste.html', 'r') as f:
            content = f.read().decode()
            print(content)

        # 2. Check web_app.py route again (just to be sure of insertion point for data fetching)
        print("\n--- web_app.py waste route ---")
        stdin, stdout, stderr = client.exec_command("grep -A 10 '@app.route(.*waste)' /var/www/sustainage/web_app.py")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_waste_module()
