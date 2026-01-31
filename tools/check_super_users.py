#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Super User Kontrolü
"""

import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_super_users() -> None:
    """Super user'ları kontrol et"""
    conn = sqlite3.connect('sdg.db')
    cur = conn.cursor()
    
    logging.info(" Super User Kontrolü")
    logging.info("="*40)
    
    # Tüm super user'ları bul
    cur.execute("SELECT username, password_hash, failed_attempts, locked_until FROM users WHERE username LIKE '%super%'")
    super_users = cur.fetchall()
    
    logging.info(f" {len(super_users)} super user bulundu:")
    for username, password_hash, failed_attempts, locked_until in super_users:
        logging.info(f"\n {username}:")
        logging.info(f"   Hash: {password_hash[:50] if password_hash else 'YOK'}...")
        logging.error(f"   Failed: {failed_attempts}")
        logging.info(f"   Locked: {locked_until}")
    
    # Tüm kullanıcıları da göster
    logging.info("\n Tüm kullanıcılar:")
    cur.execute("SELECT username, role FROM users")
    all_users = cur.fetchall()
    for username, role in all_users:
        logging.info(f"   {username} ({role})")
    
    conn.close()

if __name__ == "__main__":
    check_super_users()
