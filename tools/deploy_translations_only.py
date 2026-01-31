import paramiko
import os

HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = os.environ.get("REMOTE_SSH_PASS", "Kayra_1507")

def deploy_translations():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        print("Uploading locales/tr.json...")
        sftp.put('locales/tr.json', '/var/www/sustainage/locales/tr.json')
        sftp.close()
        
        print("Restarting services...")
        client.exec_command("systemctl restart sustainage")
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy_translations()
