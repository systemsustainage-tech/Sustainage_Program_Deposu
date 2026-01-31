import paramiko
import logging

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
        
        commands = [
            "ls -F /var/www/sustainage/backend/",
            "ls -F /var/www/sustainage/backend/modules/",
            "ls -F /var/www/sustainage/backend/modules/security/",
            "ls -F /var/www/sustainage/yonetim/"
        ]
        
        for cmd in commands:
            logging.info(f"RUNNING: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            if out: logging.info(f"OUTPUT:\n{out}")
            if err: logging.error(f"ERROR:\n{err}")
            logging.info("-" * 20)
            
    except Exception as e:
        logging.error(f"Failed: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
