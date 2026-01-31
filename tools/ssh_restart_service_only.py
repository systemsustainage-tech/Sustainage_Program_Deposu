import paramiko
import time
import logging

logging.basicConfig(level=logging.INFO)

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    logging.info("Starting service...")
    stdin, stdout, stderr = client.exec_command("systemctl start sustainage")
    out = stdout.read().decode()
    err = stderr.read().decode()
    
    if out: logging.info(f"STDOUT: {out}")
    if err: logging.error(f"STDERR: {err}")
    
    time.sleep(3)
    
    logging.info("Checking status...")
    stdin, stdout, stderr = client.exec_command("systemctl status sustainage")
    print(stdout.read().decode())
    
    client.close()

if __name__ == "__main__":
    main()
