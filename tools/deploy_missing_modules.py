
import paramiko
import os
import time

# Sunucu Bilgileri
HOSTNAME = "72.62.150.207"
USERNAME = "root"
PASSWORD = 'Z/2m?-JDp5VaX6q+HO(b'

def deploy():
    print("Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOSTNAME, username=USERNAME, password=PASSWORD)
    
    sftp = ssh.open_sftp()
    
    files_to_deploy = [
        # Environmental Modules
        (r'C:\SUSTAINAGESERVER\backend\modules\environmental\energy_manager.py', '/var/www/sustainage/backend/modules/environmental/energy_manager.py'),
        (r'C:\SUSTAINAGESERVER\backend\modules\environmental\biodiversity_manager.py', '/var/www/sustainage/backend/modules/environmental/biodiversity_manager.py'),
        (r'C:\SUSTAINAGESERVER\backend\modules\environmental\water_manager.py', '/var/www/sustainage/backend/modules/environmental/water_manager.py'),
        (r'C:\SUSTAINAGESERVER\backend\modules\environmental\waste_manager.py', '/var/www/sustainage/backend/modules/environmental/waste_manager.py'),
        (r'C:\SUSTAINAGESERVER\backend\modules\environmental\carbon_manager.py', '/var/www/sustainage/backend/modules/environmental/carbon_manager.py'),
        
        # Social Module
        (r'C:\SUSTAINAGESERVER\backend\modules\social\social_manager.py', '/var/www/sustainage/backend/modules/social/social_manager.py'),
        
        # Supply Chain Module
        (r'C:\SUSTAINAGESERVER\backend\modules\supply_chain\supply_chain_manager.py', '/var/www/sustainage/backend/modules/supply_chain/supply_chain_manager.py'),
    ]
    
    for local, remote in files_to_deploy:
        if os.path.exists(local):
            print(f"Uploading {local} to {remote}...")
            remote_dir = os.path.dirname(remote).replace('\\', '/')
            try:
                ssh.exec_command(f'mkdir -p {remote_dir}')
            except:
                pass
            sftp.put(local, remote)
        else:
            print(f"Warning: Local file not found: {local}")
            
    print("Setting permissions...")
    ssh.exec_command('chown -R www-data:www-data /var/www/sustainage')
    ssh.exec_command('chmod -R 755 /var/www/sustainage')
    
    print("Restarting Service...")
    stdin, stdout, stderr = ssh.exec_command('systemctl restart sustainage.service')
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print("Service restarted successfully.")
    else:
        print("Error restarting service:")
        print(stderr.read().decode())

    # Check status
    print("Checking service status...")
    stdin, stdout, stderr = ssh.exec_command('systemctl status sustainage.service')
    print(stdout.read().decode())
    
    sftp.close()
    ssh.close()
    print("Deployment of missing modules completed.")

if __name__ == "__main__":
    deploy()
