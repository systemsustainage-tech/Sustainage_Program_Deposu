#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanı tablolarında company_id sütunu kontrolü yapan script.
Multi-tenant mimari gereği tüm tenant'a özel tablolarda company_id bulunmalıdır.
Global tablolar hariç tutulur.
"""

import os
import sys
import sqlite3
import logging

# Backend modüllerine erişim için yolu ayarla
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.config.database import DB_PATH
    from backend.core.database import GLOBAL_TABLES
except ImportError as e:
    print(f"Hata: Modüller import edilemedi. Lütfen backend klasörünün bir üst dizininde olduğunuzdan emin olun. Detay: {e}")
    sys.exit(1)

# Loglama yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_company_id_column():
    """
    Tüm tabloları tarar ve GLOBAL_TABLES hariç diğerlerinde company_id olup olmadığını kontrol eder.
    """
    print(f"Veritabanı yolu: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("Hata: Veritabanı dosyası bulunamadı.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tüm tabloları al
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        missing_company_id = []
        checked_tables = 0
        skipped_tables = 0
        
        print("\n--- Kontrol Başlıyor ---\n")
        
        for table in tables:
            # Global ve sistem tablolarını atla
            if table in GLOBAL_TABLES or table.startswith('sqlite_'):
                # logging.info(f"Atlandı (Global/Sistem): {table}")
                skipped_tables += 1
                continue
                
            checked_tables += 1
            
            # Tablo sütunlarını al
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'company_id' not in columns:
                missing_company_id.append(table)
                logging.warning(f"EKSİK: {table} tablosunda company_id bulunamadı!")
            else:
                # logging.info(f"OK: {table}")
                pass
                
        print("\n--- Sonuçlar ---\n")
        print(f"Toplam Tablo Sayısı: {len(tables)}")
        print(f"Kontrol Edilen: {checked_tables}")
        print(f"Atlanan (Global): {skipped_tables}")
        
        if missing_company_id:
            print(f"\n[DİKKAT] Aşağıdaki {len(missing_company_id)} tabloda 'company_id' sütunu EKSİK:")
            for t in missing_company_id:
                print(f" - {t}")
            print("\nLütfen bu tabloları inceleyin ve gerekirse migrasyon ekleyin veya GLOBAL_TABLES listesine dahil edin.")
            sys.exit(1) # Hata kodu ile çık
        else:
            print("\n[BAŞARILI] Kontrol edilen tüm tablolarda company_id mevcut.")
            sys.exit(0)

    except Exception as e:
        logging.error(f"Beklenmeyen hata: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_company_id_column()
