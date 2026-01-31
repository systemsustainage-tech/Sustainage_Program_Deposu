import paramiko

def read_webapp_full():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # Read dashboard and reports routes again
        stdin, stdout, stderr = client.exec_command("grep -n -A 50 'def reports' /var/www/sustainage/web_app.py")
        print("REPORTS ROUTE:")
        print(stdout.read().decode())
        
        stdin, stdout, stderr = client.exec_command("grep -n -A 50 'def dashboard' /var/www/sustainage/web_app.py")
        print("\nDASHBOARD ROUTE:")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    read_webapp_full()
