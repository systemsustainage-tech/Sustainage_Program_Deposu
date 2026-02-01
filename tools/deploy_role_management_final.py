import paramiko
import os
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

FILES_TO_UPLOAD = [
    {'local': 'c:\\SUSTAINAGESERVER\\backend\\yonetim\\kullanici_yonetimi\\models\\user_manager.py', 'remote': '/var/www/sustainage/backend/yonetim/kullanici_yonetimi/models/user_manager.py'},
    {'local': 'c:\\SUSTAINAGESERVER\\web_app.py', 'remote': '/var/www/sustainage/web_app.py'},
    {'local': 'c:\\SUSTAINAGESERVER\\templates\\roles.html', 'remote': '/var/www/sustainage/templates/roles.html'},
    {'local': 'c:\\SUSTAINAGESERVER\\templates\\role_edit.html', 'remote': '/var/www/sustainage/templates/role_edit.html'},
    {'local': 'c:\\SUSTAINAGESERVER\\backend\\core\\language_manager.py', 'remote': '/var/www/sustainage/backend/core/language_manager.py'},
    {'local': 'c:\\SUSTAINAGESERVER\\tools\\fix_roles_schema_migration.py', 'remote': '/var/www/sustainage/tools/fix_roles_schema_migration.py'}
]

def deploy():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"Connecting to {HOSTNAME}...")
    try:
        client.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = client.open_sftp()
        
        # 1. Upload files
        for item in FILES_TO_UPLOAD:
            local_path = item['local']
            remote_path = item['remote']
            if os.path.exists(local_path):
                print(f"Uploading {local_path} to {remote_path}...")
                try:
                    remote_dir = os.path.dirname(remote_path)
                    client.exec_command(f"mkdir -p {remote_dir}")
                    sftp.put(local_path, remote_path)
                except Exception as e:
                    print(f"Error uploading {local_path}: {e}")
            else:
                print(f"Local file not found: {local_path}")
        
        sftp.close()
        
        # 2. Run schema fix
        print("Running schema fix script...")
        stdin, stdout, stderr = client.exec_command("cd /var/www/sustainage && python3 tools/fix_roles_schema_migration.py")
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(f"Schema Fix Output:\n{output}")
        if error:
            print(f"Schema Fix Error:\n{error}")

        # 3. Restart services
        print("Restarting services...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            print("Service 'sustainage' restarted successfully.")
        else:
            print("Error restarting service 'sustainage':")
            print(stderr.read().decode())
            print("Trying to restart gunicorn directly...")
            stdin, stdout, stderr = client.exec_command("systemctl restart gunicorn")
            print(stdout.read().decode())
            print(stderr.read().decode())
            
        # 4. Check status
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager")
        print(stdout.read().decode())

    except Exception as e:
        print(f"Deployment error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
