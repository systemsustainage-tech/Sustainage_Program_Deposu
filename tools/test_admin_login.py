#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin Login Test
"""

import logging
import sqlite3
import sys
import os

# Proje ana dizinini ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.database import DB_PATH
from security.core.secure_password import verify_password

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def test_admin_login() -> None:
    """Admin login test"""
    db_path = DB_PATH
    
    logging.info(f" Admin Login Test (DB: {db_path})")
    logging.info("="*40)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # Admin kullanıcısını bul
        cur.execute("SELECT username, password_hash FROM users WHERE username = 'admin'")
        admin_user = cur.fetchone()
        
        if not admin_user:
            logging.info(" Admin kullanıcısı bulunamadı!")
            return
        
        username, password_hash = admin_user
        logging.info(f" Admin: {username}")
        logging.info(f" Hash: {password_hash[:50]}...")
        
        # Farklı şifrelerle test et
        test_passwords = ["admin123", "admin", "Kayra_1507", "password"]
        
        for test_pwd in test_passwords:
            is_valid, needs_rehash = verify_password(password_hash, test_pwd)
            status = "" if is_valid else ""
            logging.info(f"   {status} Şifre '{test_pwd}': {'Geçerli' if is_valid else 'Geçersiz'}")
        
        # Admin şifresini düzelt
        logging.info("\n Admin şifresini düzeltiliyor...")
        from security.core.secure_password import hash_password
        
        admin_password = "admin123"
        new_hash = hash_password(admin_password)
        
        cur.execute("""
            UPDATE users 
            SET password_hash = ?,
                pw_hash_version = 'argon2',
                failed_attempts = 0,
                locked_until = NULL,
                must_change_password = 0
            WHERE username = 'admin'
        """, (new_hash,))
        
        conn.commit()
        logging.info(f" Admin şifresi düzeltildi: {admin_password}")
        
        # Test et
        is_valid, _ = verify_password(new_hash, admin_password)
        status = "" if is_valid else ""
        logging.info(f"   {status} Yeni şifre testi: {'Başarılı' if is_valid else 'Başarısız'}")
        
    except Exception as e:
        logging.error(f" Hata: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == "__main__":
    test_admin_login()
