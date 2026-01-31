
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
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        logging.info("Checking local HTTP response...")
        # Try to access localhost using curl to see if Apache/CGI is serving
        stdin, stdout, stderr = client.exec_command("curl -I http://localhost/login")
        
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        logging.info(f"Output:\n{out}")
        if "200 OK" in out or "302 Found" in out:
            logging.info("App seems to be running!")
        else:
            logging.warning("App might not be responding correctly. Check logs.")
            # Check error log again
            stdin, stdout, stderr = client.exec_command("tail -n 20 /var/log/apache2/error.log")
            logging.info(f"Apache Error Log:\n{stdout.read().decode()}")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == "__main__":
    main()
