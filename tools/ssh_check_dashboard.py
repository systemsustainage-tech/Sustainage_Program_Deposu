
import paramiko
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

HOST = '72.62.150.207'
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'
PORT = 22

def check_remote_dashboard():
    try:
        logging.info(f"Connecting to {HOST}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, port=PORT, username=USER, password=PASS)
        
        logging.info("Reading remote dashboard.html...")
        stdin, stdout, stderr = ssh.exec_command('cat /var/www/sustainage/templates/dashboard.html')
        content = stdout.read().decode()
        
        if "Hızlı Veri Girişi" in content:
            print("FOUND 'Hızlı Veri Girişi' in remote dashboard.html!")
            # Print context
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "Hızlı Veri Girişi" in line:
                    print(f"Line {i+1}: {line}")
        else:
            print("'Hızlı Veri Girişi' NOT found in remote dashboard.html")
            
        if "Özet İstatistikler" in content:
             print("FOUND 'Özet İstatistikler' in remote dashboard.html")
             # Check if commented out
             # This is harder with regex, but let's just print a snippet
             idx = content.find("Özet İstatistikler")
             print(f"Context: {content[idx:idx+100]}")
        
        ssh.close()
    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    check_remote_dashboard()
