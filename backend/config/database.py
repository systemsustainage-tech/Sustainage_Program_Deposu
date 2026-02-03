# -*- coding: utf-8 -*-
import os

# Proje kök dizini
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Veritabanı yolu
if os.name == 'nt':
    # Windows (Local Development)
    DB_PATH = os.path.join(ROOT_DIR, 'data', 'sdg_desktop.sqlite')
else:
    # Linux (Remote Server)
    DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

def get_db_path():
    """Veritabanı yolunu döndürür"""
    return DB_PATH

def init_db():
    """Veritabanını başlatır ve tabloları oluşturur (Test için)"""
    import sqlite3
    
    # Şema dosyasını bul
    schema_path = os.path.join(ROOT_DIR, 'target_schema.sql')
    
    if not os.path.exists(schema_path):
        print(f"Uyarı: Şema dosyası bulunamadı: {schema_path}")
        return

    # Veritabanı dizinini oluştur
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.commit()
        print(f"Veritabanı başlatıldı: {DB_PATH}")
    except Exception as e:
        print(f"Veritabanı başlatma hatası: {e}")
