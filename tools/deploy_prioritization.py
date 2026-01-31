#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Double Materiality (Prioritization) Modülünü Uzak Sunucuya Deploy Etme Aracı
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
    "backend/modules/prioritization/prioritization_manager.py",
    "web_app.py",
    "templates/prioritization.html"
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
                # Try to create directory
                try:
                    ssh.exec_command(f"mkdir -p {remote_dir}")
                    logging.info(f"Created remote directory: {remote_dir}")
                except Exception as e:
                    logging.warning(f"Could not create directory {remote_dir}: {e}")
            
            try:
                sftp.put(local_path, remote_path)
                logging.info(f"Uploaded: {file_path} -> {remote_path}")
            except Exception as e:
                logging.error(f"Failed to upload {file_path}: {e}")

        sftp.close()
        
        # Check/Update Database Schema on Remote
        # We need to run a python script on remote to update schema if needed
        # Or we can just restart the app and let the Manager init handle it?
        # The Manager runs CREATE TABLE IF NOT EXISTS and ALTER TABLE on init.
        # But web_app.py initializes managers on import/start.
        # So restarting the service should trigger the schema update.
        
        logging.info("Restarting sustainage service to apply changes...")
        stdin, stdout, stderr = ssh.exec_command("systemctl restart sustainage")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            logging.info("Service restarted successfully.")
        else:
            logging.error(f"Service restart failed: {stderr.read().decode()}")

        ssh.close()
        logging.info("Deployment complete.")

    except Exception as e:
        logging.error(f"Deployment failed: {e}")
        if ssh:
            ssh.close()

if __name__ == "__main__":
    deploy()
