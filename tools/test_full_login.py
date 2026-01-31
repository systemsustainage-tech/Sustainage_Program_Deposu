#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAM LOGIN TEST - Adım adım debug
"""

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info(" TAM LOGIN FLOW TEST")
logging.info("="*80)

username = "admin"
password = "admin123"
db_path = DB_PATH

try:
    # Adım 1: Import kontrolleri
    logging.info("\n1️⃣ Modülleri import et...")
    from security.core.secure_password import (audit_log, lockout_check,
                                               record_failed_login,
                                               reset_failed_attempts,
                                               verify_password)
    logging.info("    secure_password modülü import edildi")
    
    # Adım 2: Kilit kontrolü
    logging.info("\n2️⃣ Brute-force kilit kontrolü...")
    can_login, wait_seconds = lockout_check(db_path, username)
    if not can_login:
        logging.info(f"    Hesap kilitli: {wait_seconds} saniye")
        sys.exit(1)
    logging.info("    Giriş yapılabilir")
    
    # Adım 3: Kullanıcı sorgula
    logging.info("\n3️⃣ Kullanıcı bilgilerini al...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, username, password_hash, role, is_active, must_change_password,
               display_name, email
        FROM users
        WHERE LOWER(username) = LOWER(?)
    """, (username,))
    
    user_row = cur.fetchone()
    
    if not user_row:
        logging.info("    Kullanıcı bulunamadı!")
        sys.exit(1)
    
    user_id, db_username, password_hash, role, is_active, must_change, display_name, email = user_row
    
    logging.info("    Kullanıcı bulundu:")
    logging.info(f"      ID: {user_id}")
    logging.info(f"      Username: {db_username}")
    logging.info(f"      Role: {role}")
    logging.info(f"      Active: {is_active}")
    logging.info(f"      Must Change: {must_change}")
    logging.info(f"      Display Name: {display_name}")
    logging.info(f"      Email: {email}")
    
    # Adım 4: Aktiflik kontrolü
    logging.info("\n4️⃣ Hesap aktifliği kontrolü...")
    if not is_active:
        logging.info("    Hesap pasif!")
        sys.exit(1)
    logging.info("    Hesap aktif")
    
    # Adım 5: Şifre doğrulama
    logging.info("\n5️⃣ Şifre doğrulama...")
    logging.info(f"   Hash formatı: {password_hash[:50]}...")
    
    is_valid, needs_rehash = verify_password(password_hash, password)
    
    if not is_valid:
        logging.info("    Şifre YANLIŞ!")
        record_failed_login(db_path, username)
        logging.info("    Başarısız deneme kaydedildi")
        sys.exit(1)
    
    logging.info("    Şifre DOĞRU!")
    logging.info(f"   Rehash gerekli: {needs_rehash}")
    
    # Adım 6: Başarılı giriş işlemleri
    logging.info("\n6️⃣ Başarılı giriş işlemleri...")
    reset_failed_attempts(db_path, username)
    logging.info("    Failed attempts sıfırlandı")
    
    # Adım 7: Zorunlu şifre değişimi kontrolü
    logging.info("\n7️⃣ Zorunlu şifre değişimi kontrolü...")
    if must_change:
        logging.info("   ️ Şifre değişikliği GEREKLİ!")
        logging.info("   → İlk giriş şifre değiştirme ekranı açılacak")
    else:
        logging.info("    Şifre değişikliği gerekli değil")
    
    # Adım 8: Audit log
    logging.info("\n8️⃣ Audit log kaydı...")
    audit_log(db_path, "LOGIN_SUCCESS", user_id=user_id, username=username,
             success=True, metadata={"role": role, "test": True})
    logging.info("    Audit log kaydedildi")
    
    # Adım 9: Start main app simülasyonu
    logging.info("\n9️⃣ Ana uygulama başlatma simülasyonu...")
    user_dict = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'display_name': display_name,
        'email': email
    }
    logging.info(f"    User info hazır: {user_dict}")
    
    conn.close()
    
    logging.info("\n" + "="*80)
    logging.info(" TÜM ADIMLAR BAŞARILI!")
    logging.info("="*80)
    logging.info("\n Login sistemi tam çalışıyor!")
    logging.info(f" Giriş Bilgileri: {username} / {password}")
    
except Exception as e:
    logging.error(f"\n HATA OLUŞTU: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

