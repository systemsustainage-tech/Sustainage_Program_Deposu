#!/bin/bash
# Sustainage Backup Script
# Bu script veritabani ve loglari yedekler.
# Crontab ornegi: 0 3 * * * /var/www/sustainage/tools/sustainage_backup.sh

BASE_DIR="/var/www/sustainage"
BACKUP_DIR="$BASE_DIR/backups"
DATA_DIR="$BASE_DIR/backend/data"
LOG_DIR="$BASE_DIR/logs"
DATE=$(date +%Y%m%d_%H%M%S)

# Klasor olustur
mkdir -p $BACKUP_DIR

echo "[$(date)] Yedekleme basladi..." >> $LOG_DIR/backup.log

# Veritabani Yedegi
if [ -d "$DATA_DIR" ]; then
    echo "Veritabanlari yedekleniyor..."
    # SQLite dosyalarini kopyala (lock sorununu en aza indirmek icin .backup komutu kullanilabilir ama burada basit zip yapiyoruz)
    # En iyisi sqlite3 .backup komutudur ama karmasik olabilir. Kopyalama + Zip yeterli.
    zip -j "$BACKUP_DIR/db_backup_$DATE.zip" "$DATA_DIR"/*.sqlite "$DATA_DIR"/*.db 2>/dev/null
else
    echo "UYARI: Data dizini bulunamadi: $DATA_DIR" >> $LOG_DIR/backup.log
fi

# Log Yedegi
if [ -d "$LOG_DIR" ]; then
    echo "Loglar yedekleniyor..."
    zip -j "$BACKUP_DIR/logs_backup_$DATE.zip" "$LOG_DIR"/*.log 2>/dev/null
    
    # Loglari temizle (opsiyonel - truncate)
    # truncate -s 0 "$LOG_DIR"/*.log
else
    echo "UYARI: Log dizini bulunamadi: $LOG_DIR" >> $LOG_DIR/backup.log
fi

# Eski yedekleri temizle (7 gunden eski)
find "$BACKUP_DIR" -name "db_backup_*.zip" -type f -mtime +7 -delete
find "$BACKUP_DIR" -name "logs_backup_*.zip" -type f -mtime +7 -delete

echo "[$(date)] Yedekleme tamamlandi: $DATE" >> $LOG_DIR/backup.log
