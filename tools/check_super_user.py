#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Super User Kontrolü ve Düzeltme
"""

import logging
import sqlite3
import sys

from security.core.secure_password import hash_password
from config.icons import Icons

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_and_fix_super_user(db_path="sdg.db") -> None:
    """Super user'ı kontrol et ve düzelt"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    logging.info(" Super User Kontrolü")
    logging.info("="*50)
    
    try:
        # Tüm kullanıcıları listele
        cur.execute("SELECT username, password_hash, failed_attempts, locked_until, is_active FROM users")
        users = cur.fetchall()
        
        logging.info(f"\n Toplam {len(users)} kullanıcı:")
        for user in users:
            username, pwd_hash, failed, locked, active = user
            logging.info(f"   {username}")
            logging.info(f"      Hash: {pwd_hash[:50] if pwd_hash else 'YOK'}...")
            logging.error(f"      Failed: {failed}")
            logging.info(f"      Locked: {locked}")
            logging.info(f"      Active: {active}")
            logging.info()
        
        # _super_ kullanıcısını kontrol et
        cur.execute("SELECT * FROM users WHERE username = '_super_'")
        super_user = cur.fetchone()
        
        if super_user:
            logging.info(" _super_ kullanıcısı mevcut")
            super_user[0]
            
            # Şifreyi sabitle: Kayra_1507
            fixed_password = "Kayra_1507"
            new_hash = hash_password(fixed_password)
            
            # Super user'ı güncelle
            cur.execute("""
                UPDATE users 
                SET password_hash = ?,
                    pw_hash_version = 'argon2',
                    failed_attempts = 0,
                    locked_until = NULL,
                    must_change_password = 0,
                    is_active = 1
                WHERE username = '_super_'
            """, (new_hash,))
            
            conn.commit()
            logging.info(f" _super_ şifresi sabitlendi: {fixed_password}")
            
        else:
            logging.info(" _super_ kullanıcısı bulunamadı!")
            logging.info(f"{Icons.NEW} _super_ kullanıcısı oluşturuluyor...")
            
            # Yeni super user oluştur
            fixed_password = "Kayra_1507"
            new_hash = hash_password(fixed_password)
            
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
            
            conn.commit()
            logging.info(f" _super_ kullanıcısı oluşturuldu, şifre: {fixed_password}")
        
        # Admin kullanıcısını da kontrol et
        cur.execute("SELECT * FROM users WHERE username = 'admin'")
        admin_user = cur.fetchone()
        
        if admin_user:
            # Admin şifresini de düzelt
            admin_password = "admin123"
            admin_hash = hash_password(admin_password)
            
            cur.execute("""
                UPDATE users 
                SET password_hash = ?,
                    pw_hash_version = 'argon2',
                    failed_attempts = 0,
                    locked_until = NULL,
                    must_change_password = 0,
                    is_active = 1
                WHERE username = 'admin'
            """, (admin_hash,))
            
            conn.commit()
            logging.info(f" admin şifresi düzeltildi: {admin_password}")
        
        logging.info("\n" + "="*50)
        logging.info(" Super User işlemleri tamamlandı!")
        logging.info(" Giriş bilgileri:")
        logging.info("   _super_ / Kayra_1507")
        logging.info("   admin / admin123")
        
    except Exception as e:
        logging.error(f" Hata: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "sdg.db"
    logging.info(f" Veritabanı: {db_path}\n")
    
    success = check_and_fix_super_user(db_path)
    sys.exit(0 if success else 1)
