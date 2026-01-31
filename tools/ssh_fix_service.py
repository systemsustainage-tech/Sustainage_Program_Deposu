import paramiko
import logging
import sys
import time

# Configuration
HOST = '72.62.150.207'
PORT = 22
USER = 'root'
PASS = 'Z/2m?-JDp5VaX6q+HO(b'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

SERVICE_CONTENT = """# SUSTAINAGE SDG - Systemd Service
# /etc/systemd/system/sustainage.service

[Unit]
Description=SUSTAINAGE SDG Web Application
After=network.target

[Service]
Type=notify
User=root
# ONEMLI: Guvenlik icin bu servisi 'www-data' kullanicisi ile calistirmaniz onerilir.
# Eger dosya izinlerini ayarladiysaniz asagidaki satiri aktif edin:
# User=www-data
# Group=www-data

# Calisma dizini: /var/www/sustainage
WorkingDirectory=/var/www/sustainage
Environment="PATH=/var/www/sustainage/venv/bin"
Environment="FLASK_ENV=production"
Environment="PYTHONUNBUFFERED=1"
Environment="PYTHONPATH=/var/www/sustainage"

# Gunicorn ile başlatma
# Entry point: web_app:app (web_app.py icindeki app objesi)
ExecStart=/var/www/sustainage/venv/bin/gunicorn \
    --workers 4 \
    --worker-class gevent \
    --bind 0.0.0.0:5000 \
    --timeout 300 \
    --access-logfile /var/www/sustainage/logs/access.log \
    --error-logfile /var/www/sustainage/logs/error.log \
    --log-level info \
    web_app:app

# Otomatik yeniden başlatma
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        logging.info("Updating service file...")
        sftp = client.open_sftp()
        with sftp.file('/etc/systemd/system/sustainage.service', 'w') as f:
            f.write(SERVICE_CONTENT)
        sftp.close()
        
        logging.info("Reloading daemon and restarting service...")
        client.exec_command("systemctl daemon-reload")
        client.exec_command("systemctl restart sustainage")
        
        logging.info("Waiting for service to stabilize...")
        time.sleep(5)
        
        logging.info("Checking service status...")
        stdin, stdout, stderr = client.exec_command("systemctl status sustainage --no-pager")
        print(stdout.read().decode())
        
        logging.info("Checking error logs...")
        stdin, stdout, stderr = client.exec_command("tail -n 20 /var/www/sustainage/logs/error.log")
        print(stdout.read().decode())

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
