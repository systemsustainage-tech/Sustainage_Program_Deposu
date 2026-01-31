
import paramiko
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

def check_nginx_logs():
    try:
        logging.info(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASS)
        
        logging.info("Checking Nginx error logs...")
        stdin, stdout, stderr = ssh.exec_command('tail -n 20 /var/log/nginx/error.log')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        logging.info("Checking Nginx access logs...")
        stdin, stdout, stderr = ssh.exec_command('tail -n 20 /var/log/nginx/access.log')
        print(stdout.read().decode())
        print(stderr.read().decode())
        
        ssh.close()
    except Exception as e:
        logging.error(f"Failed to check Nginx logs: {e}")

if __name__ == '__main__':
    check_nginx_logs()
