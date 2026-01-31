#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADMIN ŞİFRESİNİ ARGON2 İLE GÜNCELLE
- Mevcut admin kullanıcısının şifresini güvenli Argon2 hash'e dönüştür
- must_change_password = 0 (admin için)
"""

import logging
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from security.core.secure_password import audit_log, hash_password
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def reset_admin_password(db_path: str = DB_PATH, username: str = "admin", new_password: str = "admin123") -> None:
    """Admin şifresini güvenli hash ile güncelle"""
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        # Admin kullanıcısı var mı?
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        
        if not row:
            logging.info(f" '{username}' kullanıcısı bulunamadı!")
            return False
        
        user_id = row[0]
        
        # Yeni hash oluştur
        new_hash = hash_password(new_password)
        hash_version = 'argon2' if new_hash.startswith('argon2$') else 'pbkdf2'
        
        # Şifreyi güncelle
        cur.execute("""
            UPDATE users 
            SET password_hash = ?,
                pw_hash_version = ?,
                must_change_password = 0,
                failed_attempts = 0,
                locked_until = NULL
            WHERE id = ?
        """, (new_hash, hash_version, user_id))
        
        conn.commit()
        
        # Audit log
        audit_log(db_path, "PWD_RESET_ADMIN", user_id=user_id, username=username,
                 success=True, metadata={"reset_by": "system_admin", "hash_version": hash_version})
        
        logging.info(f" '{username}' kullanıcısının şifresi güncellendi!")
        logging.info(f"   Yeni şifre: {new_password}")
    
    except Exception as e:
        conn.rollback()
        logging.error(f"Hata: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    logging.info(" Admin Şifre Güncelleme")
    logging.info("="*60)
    
    # Admin şifresini varsayılan "admin123" ile güncelle
    reset_admin_password(DB_PATH, "admin", "admin123")
    
    # Super admin varsa onu da güncelle
    logging.info("\n" + "-"*60)
    reset_admin_password(DB_PATH, "__super__", "__super__")
    
    logging.info("\n" + "="*60)
    logging.info(" Admin şifreleri Argon2 ile güncellendi!")
    logging.info("\n Giriş Bilgileri:")
    logging.info("   Admin: admin / admin123")
    logging.info("   Super: __super__ / __super__")

