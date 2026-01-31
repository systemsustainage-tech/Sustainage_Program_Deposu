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

NGINX_CONF = """# SUSTAINAGE SDG - Nginx Configuration
# /etc/nginx/sites-available/sustainage

server {
    listen 443 ssl;
    server_name 72.62.150.207 sustainage.cloud www.sustainage.cloud;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/sustainage.cloud/fullchain.pem; 
    ssl_certificate_key /etc/letsencrypt/live/sustainage.cloud/privkey.pem; 
    include /etc/letsencrypt/options-ssl-nginx.conf; 
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; 

    # Maksimum upload boyutu
    client_max_body_size 100M;

    # Ana uygulama
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout ayarları
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Static dosyalar (UPDATED PATH)
    location /static {
        alias /var/www/sustainage/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Raporlar için özel dizin
    location /reports {
        alias /var/www/sustainage/reports;
        expires 1d;
    }

    # Gzip sıkıştırma
    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;
    gzip_comp_level 6;
}

server {
    listen 80 default_server;
    server_name 72.62.150.207 sustainage.cloud www.sustainage.cloud _;

    # Redirect domains to HTTPS
    if ($host = www.sustainage.cloud) {
        return 301 https://$host$request_uri;
    }
    if ($host = sustainage.cloud) {
        return 301 https://$host$request_uri;
    }

    # For IP address access (HTTP), proxy to app
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files for HTTP as well
    location /static {
        alias /var/www/sustainage/static;
    }
}
"""

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        logging.info(f"Connecting to {HOST}...")
        client.connect(HOST, port=PORT, username=USER, password=PASS)
        
        logging.info("Updating Nginx config...")
        sftp = client.open_sftp()
        with sftp.file('/etc/nginx/sites-available/sustainage.conf', 'w') as f:
            f.write(NGINX_CONF)
        sftp.close()
        
        logging.info("Testing Nginx config...")
        stdin, stdout, stderr = client.exec_command("nginx -t")
        out = stdout.read().decode()
        err = stderr.read().decode()
        print(f"Test Output:\n{out}\n{err}")
        
        if "successful" in err or "successful" in out:
            logging.info("Reloading Nginx...")
            client.exec_command("systemctl reload nginx")
            logging.info("Nginx Reloaded.")
            
            logging.info("Checking HTTP response again...")
            time.sleep(2)
            stdin, stdout, stderr = client.exec_command("curl -I http://localhost/login")
            print(f"Response:\n{stdout.read().decode()}")
        else:
            logging.error("Nginx config test failed!")

        client.close()

    except Exception as e:
        logging.error(f"Failed: {e}")

if __name__ == '__main__':
    main()
