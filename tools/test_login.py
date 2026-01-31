#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOGIN SİSTEMİ TEST
- Yeni güvenlik sistemi ile admin girişini test et
"""

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3

from security.core.secure_password import lockout_check, verify_password
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def test_login(username: str, password: str, db_path: str = DB_PATH) -> None:
    """Login sistemini test et"""
    
    logging.info(f" Login Test: {username}")
    logging.info("="*60)
    
    # 1. Kilit kontrolü
    logging.info("\n1️⃣ Brute-force kilit kontrolü...")
    can_login, wait_seconds = lockout_check(db_path, username)
    if not can_login:
        logging.info(f"    Hesap kilitli! {wait_seconds} saniye bekleyin.")
        return False
    logging.info("    Hesap kilitli değil")
    
    # 2. Kullanıcı bilgilerini al
    logging.info("\n2️⃣ Kullanıcı bilgileri alınıyor...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, username, password_hash, role, is_active, must_change_password, pw_hash_version
        FROM users
        WHERE LOWER(username) = LOWER(?)
    """, (username,))
    
    row = cur.fetchone()
    conn.close()
    
    if not row:
        logging.info("    Kullanıcı bulunamadı!")
        return False
    
    user_id, db_username, password_hash, role, is_active, must_change, hash_version = row
    
    logging.info("    Kullanıcı bulundu")
    logging.info(f"      ID: {user_id}")
    logging.info(f"      Username: {db_username}")
    logging.info(f"      Role: {role}")
    logging.info(f"      Active: {is_active}")
    logging.info(f"      Must Change: {must_change}")
    logging.info(f"      Hash Version: {hash_version}")
    logging.info(f"      Hash: {password_hash[:50]}...")
    
    # 3. Aktif mi?
    if not is_active:
        logging.info("\n    Hesap pasif!")
        return False
    logging.info("    Hesap aktif")
    
    # 4. Şifre doğrula
    logging.info("\n3️⃣ Şifre doğrulanıyor...")
    try:
        is_valid, needs_rehash = verify_password(password_hash, password)
        
        if not is_valid:
            logging.info("    Şifre yanlış!")
            return False
        
        logging.info("    Şifre doğru!")
        logging.info(f"   Rehash gerekli: {needs_rehash}")
        
    except Exception as e:
        logging.error(f"    Doğrulama hatası: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Zorunlu şifre değişimi?
    logging.info("\n4️⃣ Zorunlu şifre değişimi kontrolü...")
    if must_change:
        logging.info("   ️ İlk girişte şifre değiştirilmeli!")
    else:
        logging.info("    Şifre değişimi gerekli değil")
    
    logging.info("\n" + "="*60)
    logging.info(" LOGIN BAŞARILI!")
    logging.info("="*60)
    
    return True


if __name__ == "__main__":
    logging.info("\n")
    
    # Admin ile test
    result1 = test_login("admin", "admin123")
    
    logging.info("\n\n" + "="*80 + "\n")
    
    # Yanlış şifre ile test
    logging.info(" Yanlış şifre testi:\n")
    result2 = test_login("admin", "yanlis_sifre")
    
    logging.info("\n")
    if result1:
        logging.info(" Admin girişi BAŞARILI!")
    else:
        logging.info("️ Admin girişi başarısız - lütfen kontrol edin")

