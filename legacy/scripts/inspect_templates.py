import paramiko
import os

def check_templates():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname, username=username, password=password)
        
        # List templates
        print("--- Templates Directory ---")
        stdin, stdout, stderr = client.exec_command("ls -F /var/www/sustainage/templates/")
        files = stdout.read().decode().split()
        print(files)
        
        # Download base.html and carbon.html for inspection
        sftp = client.open_sftp()
        
        print("\nDownloading base.html...")
        sftp.get("/var/www/sustainage/templates/base.html", "c:\\SUSTAINAGESERVER\\base.html")
        
        # Check if carbon.html exists, if not look for generic
        if "carbon.html" in files:
            print("Downloading carbon.html...")
            sftp.get("/var/www/sustainage/templates/carbon.html", "c:\\SUSTAINAGESERVER\\carbon.html")
        else:
            print("carbon.html not found. Checking for module templates...")
            
        sftp.close()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_templates()
