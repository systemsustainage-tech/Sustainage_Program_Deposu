#!/bin/bash
# Remote Setup Script for Systemd Service
SERVER_DIR="/var/www/sustainage"

# Dizin yoksa olustur
mkdir -p $SERVER_DIR
cd $SERVER_DIR

echo "1. Paket cikartiliyor (Extracting package)..."
# --overwrite ile dosyalarin uzerine yazilmasini garanti et
tar -xzf deploy_package_v3.tar.gz --overwrite

echo "2. Izinler duzenleniyor (Fixing permissions)..."
# Dosyalarin sahibini ayarla (genelde root veya www-data olur, servise gore root gorunuyor)
chown -R root:root $SERVER_DIR

echo "3. Bagimliliklar kontrol ediliyor (Installing dependencies)..."
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Virtualenv bulunamadi, global pip kullaniliyor..."
    pip3 install -r requirements.txt --break-system-packages
fi

echo "4. Servis yeniden baslatiliyor (Restarting Systemd Service)..."
# Manuel baslatma yerine systemd servisini restart et
systemctl restart sustainage

echo "Deployment Basariyla Tamamlandi!"
systemctl status sustainage --no-pager
