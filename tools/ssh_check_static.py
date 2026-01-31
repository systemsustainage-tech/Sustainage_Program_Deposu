import paramiko
import logging

logging.basicConfig(level=logging.INFO)

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS)
    
    logging.info("Checking static file via HTTP...")
    stdin, stdout, stderr = client.exec_command("curl -I http://127.0.0.1/static/css/style.css")
    print(stdout.read().decode())
    
    logging.info("Checking Nginx config for static alias...")
    stdin, stdout, stderr = client.exec_command("grep 'static' /etc/nginx/sites-enabled/sustainage.conf")
    print(stdout.read().decode())
    
    client.close()

if __name__ == "__main__":
    main()
