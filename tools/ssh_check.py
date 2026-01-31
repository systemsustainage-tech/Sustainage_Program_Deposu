
import paramiko
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

def create_client():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        return client
    except Exception as e:
        logging.error(f"SSH Connection Failed: {e}")
        return None

def run_command(client, command):
    logging.info(f"Running: {command}")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    
    if out:
        logging.info(f"Output:\n{out}")
    if err:
        logging.error(f"Error:\n{err}")
    
    return exit_status, out, err

def main():
    client = create_client()
    if not client:
        return

    # 1. Find the web root for sustainage.cloud
    logging.info("--- Locating Web Root ---")
    run_command(client, "find /var/www/vhosts -name httpdocs -type d | grep sustainage")

    # 2. Check Python version
    logging.info("--- Checking Python Version ---")
    run_command(client, "python3 --version")
    
    # 3. List active directory to confirm contents
    # Assuming standard Plesk path based on previous FTP knowledge, but verification is better
    # We will try to list the likely path found in step 1 manually if step 1 is too broad, 
    # but let's try a direct guess first as well.
    logging.info("--- Listing /var/www/vhosts/sustainage.cloud/httpdocs ---")
    run_command(client, "ls -la /var/www/vhosts/sustainage.cloud/httpdocs")

    # 4. Check Logs
    logging.info("--- Checking Error Logs ---")
    # Common locations for Plesk
    run_command(client, "tail -n 20 /var/www/vhosts/sustainage.cloud/logs/error_log")
    
    client.close()

if __name__ == "__main__":
    main()
