#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Companies tablosundaki verileri düzelt ve örnek şirketler ekle
"""

import logging
import os
import sqlite3
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini path'e ekle
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def fix_companies_data() -> None:
    """Companies tablosundaki verileri düzelt ve örnek şirketler ekle"""
    
    # Veritabanı yolu
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sdg_desktop.sqlite')
    
    if not os.path.exists(db_path):
        logging.info(f"Veritabani bulunamadi: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        logging.info("Companies tablosu duzenleniyor...")
        
        # Mevcut şirketleri güncelle
        cursor.execute("UPDATE companies SET name = 'Örnek Şirket A.Ş.' WHERE id = 1")
        cursor.execute("UPDATE companies SET sector = 'Teknoloji', country = 'Türkiye' WHERE id = 1")
        
        # Yeni şirketler ekle
        companies_data = [
            (2, 'Akbank T.A.Ş.', 'Bankacılık', 'Türkiye'),
            (3, 'Arçelik A.Ş.', 'Elektronik', 'Türkiye'),
            (4, 'Borusan Holding A.Ş.', 'Sanayi', 'Türkiye'),
            (7, 'Türk Telekom A.Ş.', 'Telekomünikasyon', 'Türkiye'),
            (8, 'Garanti BBVA', 'Bankacılık', 'Türkiye'),
            (9, 'Koç Holding A.Ş.', 'Holding', 'Türkiye'),
            (10, 'Sabancı Holding A.Ş.', 'Holding', 'Türkiye'),
            (11, 'Türk Hava Yolları A.O.', 'Havacılık', 'Türkiye'),
            (12, 'Vestel Elektronik A.Ş.', 'Elektronik', 'Türkiye'),
            (13, 'Zorlu Enerji A.Ş.', 'Enerji', 'Türkiye')
        ]
        
        for company in companies_data:
            cursor.execute("""
                INSERT OR REPLACE INTO companies (id, name, sector, country, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (*company, datetime.now().isoformat()))
        
        # Mevcut şirketleri de güncelle
        cursor.execute("UPDATE companies SET name = 'Yeni Firma 5', sector = 'Tekstil', country = 'Türkiye' WHERE id = 5")
        cursor.execute("UPDATE companies SET name = 'Yeni Firma 6', sector = 'Gıda', country = 'Türkiye' WHERE id = 6")
        
        # Degisiklikleri kaydet
        conn.commit()
        
        # Sonucu kontrol et
        cursor.execute("SELECT id, name, sector, country FROM companies ORDER BY id")
        companies = cursor.fetchall()
        
        logging.info(f"OK {len(companies)} sirket guncellendi/eklendi")
        logging.info("\nGuncel sirket listesi:")
        for company in companies:
            logging.info(f"ID: {company[0]}, Name: {company[1]}, Sector: {company[2]}, Country: {company[3]}")
        
        return True
        
    except Exception as e:
        logging.error(f"Companies veri duzeltme hatasi: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_companies_data()
    if success:
        logging.info("\nCompanies tablosu basariyla duzeltildi!")
    else:
        logging.error("\nCompanies tablosu duzeltilirken hata olustu!")
        sys.exit(1)
