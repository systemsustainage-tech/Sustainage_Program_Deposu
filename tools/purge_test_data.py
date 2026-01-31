#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ana veritabanındaki test/dummy verileri temizler.
- test kullanıcı adları (test%, bulk%, stress_user%)
- example.com ve benzeri test e-postaları
- 'Test Şirketi A.Ş.' şirket kaydı

Kullanım:
    python tools/purge_test_data.py

Not:
- Varsayılan veritabanı: data/sdg_desktop.sqlite
- Güvenlik için sadece açıkça test/dummy kalıplarını hedefler
"""

import logging
import os
import sqlite3
from typing import Tuple
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = os.getenv('SDG_DB_PATH', DB_PATH)

USER_PATTERNS = [
    "test%",
    "bulk%",
    "stress_user%",
]
USER_HARDCODED = [
    "cbam_user",
    "test_user",
    "newuser",
    "authuser",
    "testuser",
    "testuserbyid",
    "statstest",
]
EMAIL_PATTERNS = [
    "%@example.com%",
    "test@%",
    "%@mailinator.com%",
    "%@tempmail.%",
]

COMPANY_NAMES = [
    "Test Şirketi A.Ş.",
    "Test Sirketi A.S.",
]


def table_has_column(cur: sqlite3.Cursor, table: str, column: str) -> bool:
    import re
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table or ""):
        return False
    cur.execute("PRAGMA table_info(" + table + ")")
    return any(row[1] == column for row in cur.fetchall())


def safe_delete(cur: sqlite3.Cursor, sql: str, params: Tuple = ()) -> int:
    try:
        cur.execute(sql, params)
        return cur.rowcount if cur.rowcount is not None else 0
    except Exception as e:
        logging.error(f"[WARN] Silme hatası: {e} | SQL: {sql}")
        return 0


def purge_users(cur: sqlite3.Cursor) -> int:
    total = 0
    # Username pattern'ları
    for pat in USER_PATTERNS:
        total += safe_delete(cur, "DELETE FROM users WHERE username LIKE ?", (pat,))
    # Hardcoded kullanıcı adları
    for uname in USER_HARDCODED:
        total += safe_delete(cur, "DELETE FROM users WHERE username = ?", (uname,))
    # E-posta pattern'ları
    if table_has_column(cur, 'users', 'email'):
        for epat in EMAIL_PATTERNS:
            total += safe_delete(cur, "DELETE FROM users WHERE email LIKE ?", (epat,))
    return total


def purge_companies(cur: sqlite3.Cursor) -> int:
    total = 0
    if table_has_column(cur, 'companies', 'name'):
        for name in COMPANY_NAMES:
            total += safe_delete(cur, "DELETE FROM companies WHERE name = ?", (name,))
    return total


def main() -> None:
    if not os.path.exists(DB_PATH):
        logging.error(f"[HATA] Veritabanı bulunamadı: {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        logging.info(f"[INFO] Test verisi temizliği başlıyor: {DB_PATH}")
        deleted_users = purge_users(cur)
        deleted_companies = purge_companies(cur)
        conn.commit()
        logging.info(f"[OK] Silinen kullanıcı kayıtları: {deleted_users}")
        logging.info(f"[OK] Silinen şirket kayıtları: {deleted_companies}")
        if deleted_users == 0 and deleted_companies == 0:
            logging.info("[INFO] Temizlenecek test verisi bulunamadı.")
    except Exception as e:
        conn.rollback()
        logging.error(f"[HATA] İşlem hatası: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
