#!/bin/bash

# SustainAge Cron Job Setup Script
# Bu script, gerekli cron gorevlerini kullanicinin crontab dosyasina ekler.

BASE_DIR="/var/www/sustainage"
TOOLS_DIR="$BASE_DIR/tools"

# Scripts executable yap
chmod +x "$TOOLS_DIR/sustainage_backup.sh"
chmod +x "$TOOLS_DIR/log_monitor.py"

# Backup cron entry (Her gun 12:00)
BACKUP_CRON="0 12 * * * $TOOLS_DIR/sustainage_backup.sh >> $BASE_DIR/logs/cron_backup.log 2>&1"

# Monitor cron entry (Her 15 dakikada bir)
# Python3 path'ini garantiye alalim, genellikle /usr/bin/python3
MONITOR_CRON="*/15 * * * * /usr/bin/python3 $TOOLS_DIR/log_monitor.py >> $BASE_DIR/logs/cron_monitor.log 2>&1"

# Clean up old sustainage cron jobs to avoid duplicates
crontab -l 2>/dev/null | grep -v "sustainage_backup.sh" | grep -v "log_monitor.py" | crontab -

# Crontab'a ekle
(crontab -l 2>/dev/null; echo "$BACKUP_CRON") | crontab -
(crontab -l 2>/dev/null; echo "$MONITOR_CRON") | crontab -

echo "SustainAge cron gorevleri eklendi:"
echo "1. Backup: Her gun 12:00"
echo "2. Log Monitor: Her 15 dakikada bir"
echo "Guncel crontab listesi:"
crontab -l
