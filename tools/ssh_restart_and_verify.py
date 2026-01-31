
import paramiko
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        # 1. Clear Log
        logging.info("Clearing error log...")
        client.exec_command("truncate -s 0 /var/www/sustainage/logs/error.log")
        
        # 2. Restart Service
        logging.info("Restarting service...")
        stdin, stdout, stderr = client.exec_command("systemctl restart sustainage")
        exit_code = stdout.channel.recv_exit_status()
        
        if exit_code != 0:
            logging.error(f"Restart failed: {stderr.read().decode()}")
            return
            
        logging.info("Restart command sent. Waiting 5 seconds...")
        time.sleep(5)
        
        # 3. Check Status
        logging.info("Checking status...")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
        print(stdout.read().decode())
        
        # 4. Check New Logs
        logging.info("Checking new logs...")
        stdin, stdout, stderr = client.exec_command("cat /var/www/sustainage/logs/error.log")
        print(stdout.read().decode())
        
    except Exception as e:
        logging.error(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
