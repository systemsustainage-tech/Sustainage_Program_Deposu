import paramiko

def inspect_server():
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
        
        print("--- Checking access.log for 500 errors ---")
        stdin, stdout, stderr = client.exec_command("tail -n 20 /var/www/sustainage/logs/access.log")
        print(stdout.read().decode())
        
        print("--- Checking error.log (more lines) ---")
        stdin, stdout, stderr = client.exec_command("tail -n 100 /var/www/sustainage/logs/error.log")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_server()
