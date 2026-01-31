
import paramiko
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

LOCAL_FILE = r'C:\SUSTAINAGESERVER\tools\check_remote_db_logs.py'
REMOTE_FILE = '/var/www/sustainage/tools/check_remote_db_logs.py'

def run_remote_check():
    try:
        logging.info(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASS)
        
        sftp = ssh.open_sftp()
        try:
            sftp.stat('/var/www/sustainage/tools')
        except FileNotFoundError:
            ssh.exec_command('mkdir -p /var/www/sustainage/tools')
            
        logging.info(f"Uploading {LOCAL_FILE}...")
        sftp.put(LOCAL_FILE, REMOTE_FILE)
        sftp.close()
        
        logging.info("Running check script...")
        stdin, stdout, stderr = ssh.exec_command(f'python3 {REMOTE_FILE}')
        print("STDOUT:", stdout.read().decode())
        print("STDERR:", stderr.read().decode())
        
        ssh.close()
    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    run_remote_check()
