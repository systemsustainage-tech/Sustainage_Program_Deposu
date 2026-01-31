
import paramiko
import os

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES_TO_DEPLOY = [
    # Web App
    {'local': 'web_app.py', 'remote': '/var/www/sustainage/web_app.py'},
    
    # Templates
    {'local': 'templates/social.html', 'remote': '/var/www/sustainage/templates/social.html'},
    {'local': 'templates/governance.html', 'remote': '/var/www/sustainage/templates/governance.html'},
    {'local': 'templates/sdg.html', 'remote': '/var/www/sustainage/templates/sdg.html'},
    
    # Backend Managers
    {'local': 'backend/modules/social/social_manager.py', 'remote': '/var/www/sustainage/backend/modules/social/social_manager.py'},
    {'local': 'backend/modules/economic/economic_value_manager.py', 'remote': '/var/www/sustainage/backend/modules/economic/economic_value_manager.py'},
    {'local': 'backend/modules/governance/corporate_governance.py', 'remote': '/var/www/sustainage/backend/modules/governance/corporate_governance.py'},
    {'local': 'backend/modules/sdg/sdg_manager.py', 'remote': '/var/www/sustainage/backend/modules/sdg/sdg_manager.py'},
    {'local': 'backend/modules/cbam/cbam_manager.py', 'remote': '/var/www/sustainage/backend/modules/cbam/cbam_manager.py'},
    {'local': 'backend/modules/csrd/csrd_compliance_manager.py', 'remote': '/var/www/sustainage/backend/modules/csrd/csrd_compliance_manager.py'},
    {'local': 'templates/cbam.html', 'remote': '/var/www/sustainage/templates/cbam.html'},
]

def deploy():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        sftp = client.open_sftp()

        for file_info in FILES_TO_DEPLOY:
            local_path = os.path.join(BASE_DIR, file_info['local'])
            remote_path = file_info['remote']
            print(f"Uploading {local_path} to {remote_path}...")
            try:
                sftp.put(local_path, remote_path)
            except Exception as e:
                print(f"Error uploading {local_path}: {e}")

        # Restart Gunicorn
        print("Restarting Gunicorn...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        print(stderr.read().decode())
        print("Done.")

        sftp.close()
        client.close()

    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == '__main__':
    deploy()
