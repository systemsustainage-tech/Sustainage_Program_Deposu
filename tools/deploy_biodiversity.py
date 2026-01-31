
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
        
        # 2. Deploy biodiversity.html
        local_template = r'C:\SUSTAINAGESERVER\templates\biodiversity.html'
        remote_template = '/var/www/sustainage/templates/biodiversity.html'
        print(f"Uploading {local_template} to {remote_template}...")
        sftp.put(local_template, remote_template)
        
        # 3. Deploy locales/tr.json
        local_locale = r'C:\SUSTAINAGESERVER\locales\tr.json'
        remote_locale = '/var/www/sustainage/locales/tr.json'
        print(f"Uploading {local_locale} to {remote_locale}...")
        sftp.put(local_locale, remote_locale)

        # 4. Deploy BiodiversityManager
        local_manager = r'C:\SUSTAINAGESERVER\backend\modules\environmental\biodiversity_manager.py'
        remote_manager_dir = '/var/www/sustainage/backend/modules/environmental'
        remote_manager = f'{remote_manager_dir}/biodiversity_manager.py'
        
        print(f"Ensuring directory {remote_manager_dir} exists...")
        client.exec_command(f'mkdir -p {remote_manager_dir}')
        
        print(f"Uploading {local_manager} to {remote_manager}...")
        sftp.put(local_manager, remote_manager)

        # 5. Set Permissions
        print("Setting permissions...")
        client.exec_command("chown -R www-data:www-data /var/www/sustainage")
        client.exec_command("chmod -R 775 /var/www/sustainage")
        
        # 6. Restart Service
        print("Restarting Sustainage Service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print(f"Service restart error/warning: {err}")
        else:
            print("Service restarted successfully.")

        # 7. Verify Deployment (Simple Check)
        print("Verifying deployment...")
        time.sleep(5) # Wait for restart
        stdin, stdout, stderr = client.exec_command("curl -I http://localhost:5000/data/add")
        output = stdout.read().decode()
        print("Health check output:", output)
        
        if "200 OK" in output or "302 FOUND" in output: # 302 if redirect to login
            print("Deployment Verified: Web App is responding.")
        else:
            print("Deployment Verification Warning: Web App might not be responding correctly.")

        sftp.close()
        client.close()
        print("Deployment sequence completed.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == '__main__':
    deploy()
