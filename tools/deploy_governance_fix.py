
import paramiko
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

LOCAL_FILE = r'C:\SUSTAINAGESERVER\backend\modules\governance\corporate_governance.py'
REMOTE_FILE = '/var/www/sustainage/backend/modules/governance/corporate_governance.py'

def deploy_file():
    try:
        logging.info(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASS)
        
        sftp = ssh.open_sftp()
        logging.info(f"Uploading {LOCAL_FILE} to {REMOTE_FILE}...")
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        sftp.close()
        logging.info("File uploaded successfully.")
        
        logging.info("Restarting sustainage.service...")
        stdin, stdout, stderr = ssh.exec_command('systemctl restart sustainage.service')
        exit_status = stdout.channel.recv_exit_status()
        
        if exit_status == 0:
            logging.info("Service restarted successfully.")
        else:
            logging.error(f"Service restart failed: {stderr.read().decode()}")
            
        ssh.close()
        return True
    except Exception as e:
        logging.error(f"Deployment failed: {e}")
        return False

if __name__ == '__main__':
    deploy_file()
