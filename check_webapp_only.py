import paramiko

def check_webapp():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        print("--- Checking web_app.py for help_module ---")
        stdin, stdout, stderr = client.exec_command("grep -C 5 'def help_module' /var/www/sustainage/web_app.py")
        print(stdout.read().decode())
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_webapp()
