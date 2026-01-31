#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__super__ Kullanıcısını Oluştur
"""

import logging
import sqlite3
import sys

sys.path.insert(0, '.')

from security.core.secure_password import hash_password
from config.icons import Icons

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_super_super_user(db_path="sdg.db") -> None:
    """__super__ kullanıcısını oluştur"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    logging.info(" __super__ Kullanıcısı Oluşturma")
    logging.info("="*50)
    
    try:
        # __super__ kullanıcısını kontrol et
        cur.execute("SELECT * FROM users WHERE username = '__super__'")
        existing = cur.fetchone()
        
        if existing:
            logging.info(" __super__ kullanıcısı zaten mevcut")
            # Şifreyi güncelle
            password = "Kayra_1507"
            new_hash = hash_password(password)
            
            cur.execute("""
                UPDATE users 
                SET password_hash = ?,
                    pw_hash_version = 'argon2',
                    failed_attempts = 0,
                    locked_until = NULL,
                    must_change_password = 0,
                    is_active = 1,
                    role = 'super_admin'
                WHERE username = '__super__'
            """, (new_hash,))
            
            logging.info(f" __super__ şifresi güncellendi: {password}")
            
        else:
            logging.info(f"{Icons.NEW} __super__ kullanıcısı oluşturuluyor...")
            
            password = "Kayra_1507"
            new_hash = hash_password(password)
            
            cur.execute("""
                INSERT INTO users (
                    username, display_name, email, password_hash, pw_hash_version,
                    role, is_active, must_change_password, failed_attempts, locked_until,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                '__super__', 'Super Super Admin', 'super@super.tr',
                new_hash, 'argon2', 'super_admin', 1, 0, 0, None
            ))
            
            logging.info(f" __super__ kullanıcısı oluşturuldu, şifre: {password}")
        
        # _super_ kullanıcısını da kontrol et
        cur.execute("SELECT * FROM users WHERE username = '_super_'")
        underscore_super = cur.fetchone()
        
        if underscore_super:
            logging.info(" _super_ kullanıcısı da mevcut")
        else:
            logging.info(f"{Icons.NEW} _super_ kullanıcısı da oluşturuluyor...")
            
            cur.execute("""
                INSERT INTO users (
                    username, display_name, email, password_hash, pw_hash_version,
                    role, is_active, must_change_password, failed_attempts, locked_until,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                '_super_', 'Super Admin', 'super@sustainage.tr',
                new_hash, 'argon2', 'super_admin', 1, 0, 0, None
            ))
            
            logging.info(f" _super_ kullanıcısı oluşturuldu, şifre: {password}")
        
        conn.commit()
        
        # Koruma sistemini uygula
        from security.core.super_user_protection import \
            enforce_super_user_protection
        enforce_super_user_protection(db_path)
        
        logging.info("\n" + "="*50)
        logging.info(" SUPER USER'LAR HAZIR!")
        logging.info("="*50)
        logging.info(" Giriş bilgileri:")
        logging.info("   __super__ / Kayra_1507")
        logging.info("   _super_ / Kayra_1507")
        logging.info("   admin / admin123")
        
        return True
        
    except Exception as e:
        logging.error(f" Hata: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "sdg.db"
    logging.info(f" Veritabanı: {db_path}\n")
    
    success = create_super_super_user(db_path)
    sys.exit(0 if success else 1)
