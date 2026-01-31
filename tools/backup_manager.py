import os
import shutil
import datetime
import glob
import zipfile
import logging

# Konfigürasyon
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, 'sustainage.db')
BACKUP_DIR = os.path.join(PROJECT_ROOT, 'backups')
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, 'backups', 'logs_archive')

# Loglama ayarları
logging.basicConfig(
    filename=os.path.join(PROJECT_ROOT, 'logs', 'backup_manager.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_directories():
    """Gerekli klasörleri oluşturur."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

def backup_database():
    """Veritabanını tarih damgasıyla yedekler."""
    try:
        if not os.path.exists(DB_PATH):
            logging.error(f"Veritabanı dosyası bulunamadı: {DB_PATH}")
            print(f"Hata: Veritabanı dosyası bulunamadı: {DB_PATH}")
            return

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"sustainage_backup_{timestamp}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)

        shutil.copy2(DB_PATH, backup_path)
        logging.info(f"Veritabanı yedeklendi: {backup_path}")
        print(f"Veritabanı yedeklendi: {backup_path}")

        # Eski yedekleri temizle (Son 30 yedeği tut)
        cleanup_old_backups()

    except Exception as e:
        logging.error(f"Veritabanı yedekleme hatası: {str(e)}")
        print(f"Hata: {str(e)}")

def cleanup_old_backups(keep_count=30):
    """Eski veritabanı yedeklerini temizler."""
    try:
        backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "sustainage_backup_*.db")), key=os.path.getmtime)
        if len(backups) > keep_count:
            files_to_delete = backups[:-keep_count]
            for f in files_to_delete:
                os.remove(f)
                logging.info(f"Eski yedek silindi: {f}")
    except Exception as e:
        logging.error(f"Eski yedek temizleme hatası: {str(e)}")

def archive_logs():
    """Log dosyalarını arşivler (sıkıştırır)."""
    try:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        log_files = glob.glob(os.path.join(LOG_DIR, "*.log"))
        
        # Sadece backup_manager.log hariç diğerlerini arşivle veya temizle
        files_to_archive = [f for f in log_files if "backup_manager.log" not in f]

        if not files_to_archive:
            return

        archive_filename = f"logs_archive_{timestamp}.zip"
        archive_path = os.path.join(ARCHIVE_DIR, archive_filename)

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files_to_archive:
                zipf.write(file, os.path.basename(file))
                # Arşivlendikten sonra orijinal dosyayı temizle (içeriğini sil)
                with open(file, 'w') as f:
                    f.write('') # Dosyayı boşalt
        
        logging.info(f"Loglar arşivlendi: {archive_path}")
        print(f"Loglar arşivlendi: {archive_path}")

    except Exception as e:
        logging.error(f"Log arşivleme hatası: {str(e)}")
        print(f"Log hatası: {str(e)}")

if __name__ == "__main__":
    print("Yedekleme işlemi başlatılıyor...")
    create_directories()
    backup_database()
    archive_logs()
    print("İşlem tamamlandı.")
