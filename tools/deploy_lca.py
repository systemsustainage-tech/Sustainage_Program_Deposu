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
            '/var/www/sustainage/backend/modules/lca',
            '/var/www/sustainage/templates' # Should exist but good to be safe
        ]
        for d in dirs:
            try:
                sftp.mkdir(d)
                print(f"Created {d}")
            except OSError:
                print(f"Directory {d} already exists")
                
        # 2. Upload files
        files = [
            ('c:\\SUSTAINAGESERVER\\backend\\modules\\lca\\__init__.py', '/var/www/sustainage/backend/modules/lca/__init__.py'),
            ('c:\\SUSTAINAGESERVER\\backend\\modules\\lca\\lca_manager.py', '/var/www/sustainage/backend/modules/lca/lca_manager.py'),
            ('c:\\SUSTAINAGESERVER\\tools\\migrate_db_lca.py', '/var/www/sustainage/tools/migrate_db_lca.py'),
            ('c:\\SUSTAINAGESERVER\\web_app.py', '/var/www/sustainage/web_app.py'),
            ('c:\\SUSTAINAGESERVER\\templates\\lca.html', '/var/www/sustainage/templates/lca.html'),
            ('c:\\SUSTAINAGESERVER\\templates\\lca_product.html', '/var/www/sustainage/templates/lca_product.html'),
            ('c:\\SUSTAINAGESERVER\\templates\\lca_assessment.html', '/var/www/sustainage/templates/lca_assessment.html')
        ]
        
        for local, remote in files:
            print(f"Uploading {local} -> {remote}")
            try:
                sftp.put(local, remote)
            except Exception as e:
                print(f"Error uploading {local}: {e}")
        
        sftp.close()
        
        # 3. Run migration
        print("Running migration script...")
        stdin, stdout, stderr = ssh.exec_command('python3 /var/www/sustainage/tools/migrate_db_lca.py')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        # 4. Restart service
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
