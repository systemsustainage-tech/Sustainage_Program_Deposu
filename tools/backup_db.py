import shutil
import os
import datetime
import glob
import logging

# Configuration
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
DATA_DIR = os.path.join(BACKEND_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'sdg_desktop.sqlite')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
MAX_BACKUPS = 30

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        logging.info(f"Created backup directory: {BACKUP_DIR}")

    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"sdg_desktop_backup_{timestamp}.sqlite"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)

    try:
        shutil.copy2(DB_PATH, backup_path)
        logging.info(f"Backup created successfully: {backup_path}")
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        return

    rotate_backups()

def rotate_backups():
    # List all backups
    backups = glob.glob(os.path.join(BACKUP_DIR, "sdg_desktop_backup_*.sqlite"))
    backups.sort(key=os.path.getmtime)

    if len(backups) > MAX_BACKUPS:
        to_delete = backups[:-MAX_BACKUPS]
        for f in to_delete:
            try:
                os.remove(f)
                logging.info(f"Deleted old backup: {f}")
            except Exception as e:
                logging.error(f"Failed to delete old backup {f}: {e}")

if __name__ == "__main__":
    create_backup()
