
import paramiko
import logging

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        logging.info("Attempting to start gunicorn manually to capture error...")
        # Try to run gunicorn directly to see the error
        cmd = "cd /var/www/sustainage && source venv/bin/activate && gunicorn --bind 0.0.0.0:5000 web_app:app"
        stdin, stdout, stderr = client.exec_command(cmd)
        
        # Read a bit of output
        out = stdout.read().decode()
        err = stderr.read().decode()
        
        logging.info("STDOUT:")
        logging.info(out)
        logging.info("STDERR:")
        logging.info(err)
        
    except Exception as e:
        logging.error(f"Connection failed: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    main()
