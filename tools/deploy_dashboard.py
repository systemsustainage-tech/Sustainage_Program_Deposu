
import paramiko
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

FILES_TO_DEPLOY = [
    (r'C:\SUSTAINAGESERVER\templates\dashboard.html', '/var/www/sustainage/templates/dashboard.html'),
    (r'C:\SUSTAINAGESERVER\locales\tr.json', '/var/www/sustainage/locales/tr.json')
]

def deploy_files():
    try:
        logging.info(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASS)
        
        sftp = ssh.open_sftp()
        
        for local, remote in FILES_TO_DEPLOY:
            if os.path.exists(local):
                logging.info(f"Uploading {local} to {remote}...")
                sftp.put(local, remote)
            else:
                logging.error(f"Local file not found: {local}")
                
        sftp.close()
        
        logging.info("Reloading sustainage.service...")
        ssh.exec_command('systemctl reload sustainage.service') 
        
        ssh.close()
        logging.info("Deployment successful.")
        
    except Exception as e:
        logging.error(f"Deployment failed: {e}")

if __name__ == '__main__':
    deploy_files()
