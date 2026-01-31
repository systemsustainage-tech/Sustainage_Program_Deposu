#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Login Database Debug
"""

import logging
import os
import sqlite3
import sys

sys.path.insert(0, '.')

from security.core.secure_password import lockout_check

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def debug_login_database() -> None:
    """Login veritabanı debug"""
    logging.debug(" Login Database Debug")
    logging.info("="*50)
    
    # 1. Mevcut dizin ve dosyalar
    current_dir = os.getcwd()
    logging.info(f" Mevcut dizin: {current_dir}")
    
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    logging.info(f" DB dosyaları: {db_files}")
    
    # 2. Login screen'deki yol hesaplama
    login_file_path = os.path.join(current_dir, "app", "login_screen.py")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(login_file_path)))
    db_path = os.path.join(base_dir, "sdg.db")
    
    logging.info(f" Login base_dir: {base_dir}")
    logging.info(f" Login db_path: {db_path}")
    logging.info(f" DB dosyası var mı: {os.path.exists(db_path)}")
    
    # 3. Her iki yolu da test et
    test_paths = ["sdg.db", db_path]
    
    for test_path in test_paths:
        logging.info(f"\n Test edilen yol: {test_path}")
        logging.info(f"   Dosya var mı: {os.path.exists(test_path)}")
        
        if os.path.exists(test_path):
            try:
                conn = sqlite3.connect(test_path)
                cur = conn.cursor()
                
                # Tablo yapısını kontrol et
                cur.execute("PRAGMA table_info(users)")
                columns = [row[1] for row in cur.fetchall()]
                logging.info(f"   Users kolonları: {columns}")
                
                has_failed_attempts = 'failed_attempts' in columns
                logging.error(f"   failed_attempts var mı: {has_failed_attempts}")
                
                if has_failed_attempts:
                    # _super_ kullanıcısını kontrol et
                    cur.execute("SELECT username FROM users WHERE username = '_super_'")
                    super_user = cur.fetchone()
                    logging.info(f"   _super_ kullanıcısı var mı: {super_user is not None}")
                    
                    if super_user:
                        # Lockout check test
                        try:
                            can_login, wait_seconds = lockout_check(test_path, "_super_")
                            logging.info(f"   Lockout check başarılı: {can_login}, wait: {wait_seconds}")
                        except Exception as e:
                            logging.error(f"   Lockout check hatası: {e}")
                
                conn.close()
                
            except Exception as e:
                logging.error(f"   Veritabanı hatası: {e}")
    
    # 4. Gerçek login screen test
    logging.info("\n Login Screen Test:")
    try:
        import tkinter as tk

        from app.login_screen import LoginScreen
        
        root = tk.Tk()
        root.withdraw()
        
        login_screen = LoginScreen(root)
        logging.info(f"   Login screen db_path: {login_screen.db_path}")
        logging.info(f"   Login screen db_path var mı: {os.path.exists(login_screen.db_path)}")
        
        root.destroy()
        
    except Exception as e:
        logging.error(f"   Login screen test hatası: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_login_database()
