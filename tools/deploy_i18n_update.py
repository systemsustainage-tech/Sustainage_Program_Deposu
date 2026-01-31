import paramiko
import os
import time

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        sftp = client.open_sftp()
        
        # 1. Deploy web_app.py
        local_app = r'C:\SUSTAINAGESERVER\web_app.py'
        remote_app = '/var/www/sustainage/web_app.py'
        print(f"Uploading {local_app} to {remote_app}...")
        sftp.put(local_app, remote_app)
        
        # 2. Deploy backend/core/language_manager.py
        local_lm = r'C:\SUSTAINAGESERVER\backend\core\language_manager.py'
        remote_lm_dir = '/var/www/sustainage/backend/core'
        remote_lm = '/var/www/sustainage/backend/core/language_manager.py'
        
        print(f"Ensuring remote directory {remote_lm_dir}...")
        client.exec_command(f'mkdir -p {remote_lm_dir}')
        
        print(f"Uploading {local_lm}...")
        sftp.put(local_lm, remote_lm)

        # 3. Deploy ALL Templates
        local_templates_dir = r'C:\SUSTAINAGESERVER\templates'
        remote_templates_dir = '/var/www/sustainage/templates'
        
        print("Deploying templates...")
        for file in os.listdir(local_templates_dir):
            if file.endswith('.html'):
                local_path = os.path.join(local_templates_dir, file)
                remote_path = f"{remote_templates_dir}/{file}"
                print(f"Uploading {file}...")
                sftp.put(local_path, remote_path)
        
        # 4. Deploy Locales
        local_locales_dir = r'C:\SUSTAINAGESERVER\locales'
        remote_locales_dir = '/var/www/sustainage/locales'
        try:
             client.exec_command(f'mkdir -p {remote_locales_dir}')
        except:
             pass

        print("Deploying locales...")
        for file in os.listdir(local_locales_dir):
            if file.endswith('.json'):
                local_path = os.path.join(local_locales_dir, file)
                remote_path = f"{remote_locales_dir}/{file}"
                print(f"Uploading {file}...")
                sftp.put(local_path, remote_path)

        # 5. Set Permissions
        print("Setting permissions...")
        client.exec_command("chown -R www-data:www-data /var/www/sustainage")
        client.exec_command("chmod -R 775 /var/www/sustainage")
        
        # 6. Restart Gunicorn
        print("Restarting Gunicorn...")
        client.exec_command("pkill -HUP gunicorn")
        print("Done.")

        sftp.close()
        client.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    deploy()
