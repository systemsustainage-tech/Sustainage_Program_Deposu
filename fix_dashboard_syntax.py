import paramiko
import re

def fix_dashboard_syntax():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        remote_path = '/var/www/sustainage/templates/dashboard.html'
        
        print(f"Reading {remote_path}...")
        with sftp.open(remote_path, 'r') as f:
            content = f.read().decode()
        
        # Remove backslashes before quotes in Jinja2 expressions
        # Specifically targeting the ones I likely introduced: \'
        
        new_content = content.replace("\\'", "'")
        
        if new_content != content:
            print("Found and fixing syntax errors...")
            with sftp.open(remote_path, 'w') as f:
                f.write(new_content)
            print("Upload complete.")
        else:
            print("No syntax errors found (or pattern didn't match).")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_dashboard_syntax()
