
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
            "ls -F /var/www/",
            "ls -F /home/",
            "find / -name httpdocs -type d 2>/dev/null | head -n 5",
            "find / -name sustainage -type d 2>/dev/null | head -n 5",
            "ps aux | grep -E 'apache|httpd|nginx|python'",
            "cat /etc/os-release"
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
