
import paramiko
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'cursorsustainageftp'
PASS = 'Kayra_1507_Sk!'
PORT = 22

def main():
    try:
        logging.info(f"Connecting to {HOST}:{PORT} via SFTP...")
        transport = paramiko.Transport((HOST, PORT))
        transport.connect(username=USER, password=PASS)
        sftp = paramiko.SFTPClient.from_transport(transport)
        logging.info("Connected successfully!")
        
        logging.info("Listing root directory:")
        files = sftp.listdir()
        for f in files:
            print(f)
            
        # Check if httpdocs exists
        if 'httpdocs' in files:
             logging.info("Listing httpdocs:")
             files_http = sftp.listdir('httpdocs')
             for f in files_http:
                 print(f)
        
        sftp.close()
        transport.close()
        
    except Exception as e:
        logging.error(f"SFTP Error: {e}")

if __name__ == "__main__":
    main()
