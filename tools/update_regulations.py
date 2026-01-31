import sys
import os
import sqlite3
import logging
from datetime import datetime, timedelta

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_regulations():
    """
    Regülasyon veritabanını günceller (Simülasyon).
    Gerçek senaryoda bir API'den veri çeker.
    """
    logging.info("Regülasyon güncelleme işlemi başlatıldı...")
    
    # Mock update: Check for existing regulations and update 'updated_at'
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Simüle edilmiş yeni regülasyon kontrolü
        cursor.execute("SELECT COUNT(*) FROM regulations")
        count = cursor.fetchone()[0]
        logging.info(f"Mevcut regülasyon sayısı: {count}")
        
        # 2. Yaklaşan uyum tarihleri kontrolü
        target_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT code, title, compliance_deadline 
            FROM regulations 
            WHERE compliance_deadline BETWEEN ? AND ?
        """, (today, target_date))
        
        upcoming = cursor.fetchall()
        if upcoming:
            logging.warning(f"DİKKAT: {len(upcoming)} regülasyon için uyum tarihi yaklaşıyor (30 gün)!")
            for reg in upcoming:
                logging.warning(f" - {reg[0]}: {reg[1]} (Son Tarih: {reg[2]})")
        else:
            logging.info("Yakın tarihte (30 gün) dolacak uyum zorunluluğu bulunmuyor.")
            
        logging.info("Regülasyon veritabanı güncel.")
        
    except Exception as e:
        logging.error(f"Güncelleme hatası: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_regulations()
