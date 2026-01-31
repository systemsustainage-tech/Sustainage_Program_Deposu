
import paramiko
import os

# Server Details
HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def deploy():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        print("Connected to server.")

        sftp = client.open_sftp()

        # 1. Deploy web_app.py
        local_app = os.path.join(BASE_DIR, 'web_app.py')
        remote_app = '/var/www/sustainage/web_app.py'
        print(f"Uploading {local_app} to {remote_app}...")
        sftp.put(local_app, remote_app)

        # 2. Deploy ALL Templates
        local_templates_dir = os.path.join(BASE_DIR, 'templates')
        remote_templates_dir = '/var/www/sustainage/templates'

        print("Deploying templates...")
        for file in os.listdir(local_templates_dir):
            if file.endswith('.html'):
                local_path = os.path.join(local_templates_dir, file)
                remote_path = f"{remote_templates_dir}/{file}"
                print(f"Uploading {file}...")
                sftp.put(local_path, remote_path)

        # 3. Deploy Locales (All of them to be safe)
        local_locales_dir = os.path.join(BASE_DIR, 'locales')
        remote_locales_dir = '/var/www/sustainage/locales'

        # Ensure remote dir exists
        try:
            sftp.listdir(remote_locales_dir)
        except IOError:
            print(f"Creating {remote_locales_dir}...")
            sftp.mkdir(remote_locales_dir)

        for file in os.listdir(local_locales_dir):
            if file.endswith('.json'):
                local_path = os.path.join(local_locales_dir, file)
                remote_path = f"{remote_locales_dir}/{file}"
                print(f"Uploading {file}...")
                sftp.put(local_path, remote_path)

        # 4. Deploy and Run DB Script
        local_script = os.path.join(BASE_DIR, 'tools', 'create_report_registry.py')
        remote_script = '/var/www/sustainage/create_report_registry.py'
        print(f"Uploading {local_script}...")
        sftp.put(local_script, remote_script)

        print("Running DB creation script...")
        stdin, stdout, stderr = client.exec_command(f'python3 {remote_script}')
        print(stdout.read().decode())
        print(stderr.read().decode())

        # Install reportlab
        print("Installing reportlab...")
        stdin, stdout, stderr = client.exec_command('pip install reportlab')
        print(stdout.read().decode())
        print(stderr.read().decode())

        # 5. Restart Gunicorn
        print("Restarting Gunicorn...")
        client.exec_command("pkill -HUP gunicorn")
        print("Done.")

        sftp.close()
        client.close()

    except Exception as e:
        print(f"Deployment failed: {e}")


if __name__ == '__main__':
    deploy()
