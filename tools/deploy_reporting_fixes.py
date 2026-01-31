
import paramiko
import os
import time

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES_TO_DEPLOY = [
    # Report Logic
    {'local': 'backend/modules/reporting/unified_report_docx.py', 'remote': '/var/www/sustainage/backend/modules/reporting/unified_report_docx.py'},
    # {'local': 'tools/render_report.py', 'remote': '/var/www/sustainage/tools/render_report.py'},
    
    # Login & Email Fixes (Already Deployed)
    # {'local': 'backend/yonetim/kullanici_yonetimi/models/user_manager.py', 'remote': '/var/www/sustainage/backend/yonetim/kullanici_yonetimi/models/user_manager.py'},
    # {'local': 'backend/services/email_service.py', 'remote': '/var/www/sustainage/backend/services/email_service.py'},
    # {'local': 'config/smtp_config.json', 'remote': '/var/www/sustainage/config/smtp_config.json'},
    
    # Tools (optional but useful)
    # {'local': 'tools/fix_admin_password.py', 'remote': '/var/www/sustainage/tools/fix_admin_password.py'},
    # {'local': 'tools/verify_user_login.py', 'remote': '/var/www/sustainage/tools/verify_user_login.py'},
    # {'local': 'tools/populate_tsrs_mappings.py', 'remote': '/var/www/sustainage/tools/populate_tsrs_mappings.py'},
]

def deploy():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {HOSTNAME}...")
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected.")

        sftp = client.open_sftp()

        for file_info in FILES_TO_DEPLOY:
            local_path = os.path.join(BASE_DIR, file_info['local'])
            remote_path = file_info['remote']
            
            if not os.path.exists(local_path):
                print(f"Skipping missing local file: {local_path}")
                continue

            print(f"Uploading {local_path} to {remote_path}...")
            try:
                # Ensure remote directory exists
                remote_dir = os.path.dirname(remote_path)
                try:
                    sftp.stat(remote_dir)
                except IOError:
                    # Create directory if missing (simple 1-level check)
                    print(f"Creating remote directory: {remote_dir}")
                    try:
                        sftp.mkdir(remote_dir)
                    except:
                        pass # Might fail if parent missing, but usually ok for existing structure
                
                sftp.put(local_path, remote_path)
                
                # Set permissions
                if remote_path.endswith('.py') or remote_path.endswith('.sh'):
                    sftp.chmod(remote_path, 0o755)
            except Exception as e:
                print(f"Error uploading {local_path}: {e}")

        # Run Population Script
        # print("Running TSRS mapping population script on remote...")
        # stdin, stdout, stderr = client.exec_command("export PYTHONPATH=/var/www/sustainage && python3 /var/www/sustainage/tools/populate_tsrs_mappings.py")
        # exit_code = stdout.channel.recv_exit_status()
        # if exit_code == 0:
        #     print("Mapping population successful.")
        #     print(stdout.read().decode())
        # else:
        #     print(f"Mapping population failed: {stderr.read().decode()}")

        # Restart Service
        print("Restarting sustainage service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_code = stdout.channel.recv_exit_status()
        if exit_code == 0:
            print("Service restarted successfully.")
        else:
            print(f"Service restart failed: {stderr.read().decode()}")

        sftp.close()
        client.close()

    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == '__main__':
    deploy()
