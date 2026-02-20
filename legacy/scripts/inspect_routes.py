import paramiko
import re

def inspect_app_routes():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # 1. Get all routes from web_app.py
        print("--- Routes in web_app.py ---")
        stdin, stdout, stderr = client.exec_command("grep '@app.route' /var/www/sustainage/web_app.py")
        print(stdout.read().decode())
        
        # 2. Get function definitions associated with routes (to match endpoint names)
        print("\n--- Route Definitions ---")
        # Grep context to see function names
        stdin, stdout, stderr = client.exec_command("grep -A 1 '@app.route' /var/www/sustainage/web_app.py")
        print(stdout.read().decode())
        
        # 3. Check dashboard.html content to see current hrefs
        print("\n--- Current dashboard.html content (first 200 lines) ---")
        sftp = client.open_sftp()
        with sftp.open("/var/www/sustainage/templates/dashboard.html", "r") as f:
            # Read enough to see the module links
            content = f.read()
            print(content[:2000]) # First 2000 chars should cover the modules section
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    inspect_app_routes()
