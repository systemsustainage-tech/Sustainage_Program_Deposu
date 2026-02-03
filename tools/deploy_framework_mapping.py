import paramiko
import os

def deploy():
    hostname = '72.62.150.207'
    username = 'root'
    password = '321'
    
    files_to_upload = [
        ('c:\\SUSTAINAGESERVER\\web_app.py', '/var/www/sustainage/web_app.py'),
        ('c:\\SUSTAINAGESERVER\\templates\\framework_mapping.html', '/var/www/sustainage/templates/framework_mapping.html'),
        ('c:\\SUSTAINAGESERVER\\tools\\update_standard_mappings.py', '/var/www/sustainage/tools/update_standard_mappings.py'),
    ]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()
        
        for local, remote in files_to_upload:
            print(f"Uploading {local} -> {remote}...")
            sftp.put(local, remote)
            
        print("Running update_standard_mappings.py on remote...")
        stdin, stdout, stderr = client.exec_command("cd /var/www/sustainage && python3 tools/update_standard_mappings.py")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Error output: {err}")

        print("Restarting service...")
        client.exec_command("systemctl restart sustainage.service")
        
        print("Deployment complete.")
        
    except Exception as e:
        print(f"Deploy failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()