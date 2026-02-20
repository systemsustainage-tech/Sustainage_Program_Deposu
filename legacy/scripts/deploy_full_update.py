
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
        
        # 2. Deploy ALL Templates
        local_templates_dir = r'C:\SUSTAINAGESERVER\templates'
        remote_templates_dir = '/var/www/sustainage/templates'
        
        print("Deploying templates...")
        for file in os.listdir(local_templates_dir):
            if file.endswith('.html'):
                local_path = os.path.join(local_templates_dir, file)
                remote_path = f"{remote_templates_dir}/{file}"
                print(f"Uploading {file}...")
                sftp.put(local_path, remote_path)
        
        # 2.5 Deploy Locales
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

        # 2.6 Deploy Static
        local_static_dir = r'C:\SUSTAINAGESERVER\static'
        remote_static_dir = '/var/www/sustainage/static'
        try:
             client.exec_command(f'mkdir -p {remote_static_dir}')
        except:
             pass

        print("Deploying static files...")
        # Recursive function for static and backend
        def put_dir_recursive(sftp, local_dir, remote_dir):
            for item in os.listdir(local_dir):
                if item == '__pycache__' or item.startswith('.'):
                    continue
                local_path = os.path.join(local_dir, item)
                remote_path = f"{remote_dir}/{item}"
                if os.path.isdir(local_path):
                    try:
                        sftp.mkdir(remote_path)
                    except IOError:
                        pass # Directory likely exists
                    put_dir_recursive(sftp, local_path, remote_path)
                else:
                    sftp.put(local_path, remote_path)

        put_dir_recursive(sftp, local_static_dir, remote_static_dir)

        # 2.7 Deploy Backend
        local_backend_dir = r'C:\SUSTAINAGESERVER\backend'
        remote_backend_dir = '/var/www/sustainage/backend'
        try:
             client.exec_command(f'mkdir -p {remote_backend_dir}')
        except:
             pass
             
        print("Deploying backend...")
        put_dir_recursive(sftp, local_backend_dir, remote_backend_dir)

        # 3. Deploy and Run Fix DB Schema
        local_fix = r'C:\SUSTAINAGESERVER\tools\fix_db_schema.py'
        remote_fix = '/var/www/sustainage/fix_db_schema.py'
        print(f"Uploading {local_fix}...")
        sftp.put(local_fix, remote_fix)
        
        print("Running Fix DB Schema...")
        stdin, stdout, stderr = client.exec_command(f'python3 {remote_fix}')
        print(stdout.read().decode())
        print(stderr.read().decode())

        # 4. Deploy and Run GRI Update
        local_gri_update = r'C:\SUSTAINAGESERVER\tools\update_gri_2025.py'
        remote_gri_update = '/var/www/sustainage/update_gri_2025.py'
        print(f"Uploading {local_gri_update}...")
        sftp.put(local_gri_update, remote_gri_update)
        
        print("Running GRI Update...")
        stdin, stdout, stderr = client.exec_command(f'python3 {remote_gri_update}')
        print(stdout.read().decode())
        print(stderr.read().decode())

        # 6. Set Permissions (Crucial for uploads and DB)
        print("Setting permissions...")
        client.exec_command("chown -R www-data:www-data /var/www/sustainage")
        client.exec_command("chmod -R 775 /var/www/sustainage")

        # 5. Restart Gunicorn
        print("Restarting Gunicorn...")
        client.exec_command('systemctl restart sustainage')

        print("Done.")

        sftp.close()
        client.close()
        
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == '__main__':
    deploy()
