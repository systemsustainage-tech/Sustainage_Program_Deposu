
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
        
        logging.info("Moving DB to correct location...")
        # 1. Ensure /var/www/sustainage/data exists
        client.exec_command("mkdir -p /var/www/sustainage/data")
        
        # 2. Move DB if it exists in backend/data
        # We check if backend/data/sdg_desktop.sqlite exists
        # And move it to /var/www/sustainage/data/sdg_desktop.sqlite
        
        cmds = [
            "mv /var/www/sustainage/backend/data/sdg_desktop.sqlite /var/www/sustainage/data/sdg_desktop.sqlite",
            "chown -R www-data:www-data /var/www/sustainage/data",
            "chmod -R 775 /var/www/sustainage/data",
            # Also keep a copy in backend/data just in case something else references it?
            # Or symlink?
            "ln -s /var/www/sustainage/data/sdg_desktop.sqlite /var/www/sustainage/backend/data/sdg_desktop.sqlite"
        ]
        
        for cmd in cmds:
            logging.info(f"Running: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            err = stderr.read().decode()
            if err and "No such file" not in err: # Ignore if file missing (already moved)
                logging.warning(f"Warning: {err}")
                
        logging.info("DB Move Complete.")
        
        # Verify
        stdin, stdout, stderr = client.exec_command("ls -l /var/www/sustainage/data/sdg_desktop.sqlite")
        print(stdout.read().decode())
        
        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == "__main__":
    main()
