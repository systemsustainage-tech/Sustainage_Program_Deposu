
import paramiko
import os

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

FILES_TO_UPLOAD = [
    {'local': 'c:\\SUSTAINAGESERVER\\services\\email_service.py', 'remote': '/var/www/sustainage/services/email_service.py'},
    {'local': 'c:\\SUSTAINAGESERVER\\backend\\config\\smtp_config.json', 'remote': '/var/www/sustainage/backend/config/smtp_config.json'}
]

def deploy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        
        for item in FILES_TO_UPLOAD:
            local_path = item['local']
            remote_path = item['remote']
            print(f"Uploading {local_path} to {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"Error uploading {local_path}: {e}")
        
        sftp.close()
        
        print("Restarting services...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service 'sustainage' restarted successfully.")
        else:
            print("Error restarting service 'sustainage':")
            print(stderr.read().decode())

    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
