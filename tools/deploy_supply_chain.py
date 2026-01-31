
import paramiko
import os
import time

HOSTNAME = '72.62.150.207'
USERNAME = 'root'
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy():
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {HOSTNAME}...")
        ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
        
        sftp = ssh.open_sftp()
        
        # 1. Create remote directories
        print("Creating remote directories...")
        dirs = [
            '/var/www/sustainage/backend/modules/supply_chain',
            '/var/www/sustainage/templates'
        ]
        for d in dirs:
            try:
                sftp.mkdir(d)
                print(f"Created {d}")
            except OSError:
                print(f"Directory {d} already exists")
                
        # 2. Upload files
        files = [
            ('c:\\SUSTAINAGESERVER\\backend\\modules\\supply_chain\\__init__.py', '/var/www/sustainage/backend/modules/supply_chain/__init__.py'),
            ('c:\\SUSTAINAGESERVER\\backend\\modules\\supply_chain\\supply_chain_manager.py', '/var/www/sustainage/backend/modules/supply_chain/supply_chain_manager.py'),
            ('c:\\SUSTAINAGESERVER\\tools\\migrate_db_supply_chain.py', '/var/www/sustainage/tools/migrate_db_supply_chain.py'),
            ('c:\\SUSTAINAGESERVER\\web_app.py', '/var/www/sustainage/web_app.py'),
            ('c:\\SUSTAINAGESERVER\\templates\\supply_chain.html', '/var/www/sustainage/templates/supply_chain.html'),
            ('c:\\SUSTAINAGESERVER\\templates\\supply_chain_profile.html', '/var/www/sustainage/templates/supply_chain_profile.html')
        ]
        
        for local, remote in files:
            print(f"Uploading {local} -> {remote}")
            try:
                sftp.put(local, remote)
            except Exception as e:
                print(f"Error uploading {local}: {e}")
        
        sftp.close()
        
        # 3. Fix permissions (Important for new files)
        print("Fixing permissions...")
        ssh.exec_command('chown -R www-data:www-data /var/www/sustainage')
        
        # 4. Run migration
        print("Running migration script...")
        stdin, stdout, stderr = ssh.exec_command('python3 /var/www/sustainage/tools/migrate_db_supply_chain.py')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # 5. Restart service
        print("Restarting service...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart sustainage.service')
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            print("Service restarted successfully.")
        else:
            print("Error restarting service.")
            print(stderr.read().decode())
            
        ssh.close()
        print("Deployment complete.")
        
    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
