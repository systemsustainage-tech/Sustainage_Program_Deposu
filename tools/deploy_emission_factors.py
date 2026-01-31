#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emisyon Faktörleri Kütüphanesini Uzak Sunucuya Deploy Etme Aracı
"""

import paramiko
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Credentials
HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

REMOTE_BASE = '/var/www/sustainage'
LOCAL_BASE = os.getcwd()

FILES_TO_DEPLOY = [
    "backend/modules/environmental/emission_factor_data.py",
    "backend/modules/environmental/carbon_manager.py",
    "tools/populate_emission_factors.py"
]

def deploy():
    ssh = None
    try:
        # Establish SSH connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASS)
        logging.info(f"Connected to {HOST}")

        # SFTP for file transfer
        sftp = ssh.open_sftp()
        
        for file_path in FILES_TO_DEPLOY:
            local_path = os.path.join(LOCAL_BASE, file_path)
            remote_path = f"{REMOTE_BASE}/{file_path}"
            
            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_path)
            try:
                sftp.stat(remote_dir)
            except IOError:
                # Directory doesn't exist, try to create it
                logging.info(f"Creating remote directory: {remote_dir}")
                # mkdir -p equivalent via exec_command because sftp.mkdir is shallow
                stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {remote_dir}")
                exit_status = stdout.channel.recv_exit_status()
                if exit_status != 0:
                    logging.error(f"Failed to create directory {remote_dir}: {stderr.read().decode()}")
                    continue

            try:
                sftp.put(local_path, remote_path)
                logging.info(f"Uploaded: {file_path}")
            except Exception as e:
                logging.error(f"Failed to upload {file_path}: {e}")

        sftp.close()
        
        # Run population script
        logging.info("Running population script on remote server...")
        cmd = f"cd {REMOTE_BASE} && python3 tools/populate_emission_factors.py"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        
        # Stream output
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line.strip())
            
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            logging.info("Remote population script finished successfully.")
        else:
            logging.error(f"Remote script failed with exit code {exit_status}")
            print(stderr.read().decode())

        ssh.close()
        logging.info("Deployment and execution complete.")
        
    except Exception as e:
        logging.error(f"Deployment failed: {e}")
        if ssh:
            ssh.close()

if __name__ == "__main__":
    deploy()
