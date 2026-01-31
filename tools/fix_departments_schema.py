#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Departmanlar şemasını düzelt
Eksik sütunları ekler
"""

import logging
import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fix_departments_schema() -> None:
    """Departmanlar şemasını düzelt"""
    
    # Veritabanı yolu
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sdg_desktop.sqlite')
    
    if not os.path.exists(db_path):
        logging.info(f"Veritabanı bulunamadı: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        logging.info("Departmanlar şeması düzeltiliyor...")
        
        # Departments tablosuna eksik sütunları ekle
        try:
            cursor.execute("ALTER TABLE departments ADD COLUMN updated_at TEXT")
            logging.info("[OK] departments.updated_at sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] departments.updated_at sütunu zaten mevcut")
        
        # Permissions tablosuna is_active sütunu ekle
        try:
            cursor.execute("ALTER TABLE permissions ADD COLUMN is_active INTEGER DEFAULT 1")
            logging.info("[OK] permissions.is_active sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] permissions.is_active sütunu zaten mevcut")
        
        # Departments tablosuna created_by sütunu ekle
        try:
            cursor.execute("ALTER TABLE departments ADD COLUMN created_by INTEGER")
            logging.info("[OK] departments.created_by sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] departments.created_by sütunu zaten mevcut")
        
        # Departments tablosuna updated_by sütunu ekle
        try:
            cursor.execute("ALTER TABLE departments ADD COLUMN updated_by INTEGER")
            logging.info("[OK] departments.updated_by sütunu eklendi")
        except sqlite3.OperationalError:
            logging.info("[INFO] departments.updated_by sütunu zaten mevcut")
        
        conn.commit()
        logging.info("[SUCCESS] Departmanlar şeması başarıyla düzeltildi!")
        return True
        
    except Exception as e:
        logging.error(f"[ERROR] Şema düzeltilirken hata: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_departments_schema()
