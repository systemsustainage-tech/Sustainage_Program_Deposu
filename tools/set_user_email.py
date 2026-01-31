#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kullanıcı e-mail güncelleme aracı.
Kullanım:
    python tools/set_user_email.py <username> <new_email> [db_path]
Varsayılan DB: data/sdg_desktop.sqlite
"""

import logging
import os
import sqlite3
import sys
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB = os.path.join(BASE_DIR, 'data', 'sdg_desktop.sqlite')


def set_user_email(username: str, new_email: str, db_path: Optional[str] = None) -> bool:
    db = db_path or DEFAULT_DB
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, username, email FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        row = cur.fetchone()
        if not row:
            logging.info(f" Kullanıcı bulunamadı: {username}")
            return False
        user_id = row[0]
        cur.execute("UPDATE users SET email = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_email, user_id))
        conn.commit()
        logging.info(f" E-mail güncellendi: {username} → {new_email}")
        return True
    except Exception as e:
        conn.rollback()
        logging.error(f" Hata: {e}")
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        logging.info("Kullanım: python tools/set_user_email.py <username> <new_email> [db_path]")
        sys.exit(1)
    username = sys.argv[1]
    new_email = sys.argv[2]
    db_path = sys.argv[3] if len(sys.argv) > 3 else None
    set_user_email(username, new_email, db_path)
