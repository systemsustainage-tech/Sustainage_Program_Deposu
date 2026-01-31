#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Süper admin kullanıcı oluşturma / güncelleme aracı

- Kullanıcı adı: __super__
- Şifre: Kayra_1507 (Argon2 )
- Rol: super_admin
"""

import logging
import os
import sqlite3

from yonetim.security.core.crypto import hash_password as secure_hash_password

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'sdg_desktop.sqlite')

USERNAME = "__super__"
PASSWORD = "Kayra_1507"
DISPLAY_NAME = "Süper Admin"
EMAIL = "super@sustainage.tr"
ROLE = "super_admin"

def ensure_db() -> None:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Veritabanı bulunamadı: {DB_PATH}")

def upsert_super_admin() -> None:
    ensure_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        password_hash = secure_hash_password(PASSWORD)

        # users tablosunda gerekli sütunların varlığını doğrula (minimal kontrol)
        cur.execute("PRAGMA table_info(users)")
        cols = {row[1] for row in cur.fetchall()}
        required = {"username", "display_name", "email", "password_hash", "role", "is_active"}
        if not required.issubset(cols):
            # Bazı ortamlarda farklı şema olabilir; yine de en yakın alanlarla deneriz
            # display_name yoksa username'i display olarak ayarla
            display_col = "display_name" if "display_name" in cols else None
            role_col = "role" if "role" in cols else None

            # Dinamik INSERT hazırla
            fields = ["username", "email", "password_hash", "is_active"]
            values = [USERNAME, EMAIL, password_hash, 1]
            if display_col:
                fields.insert(1, display_col)
                values.insert(1, DISPLAY_NAME)
            if role_col:
                fields.append(role_col)
                values.append(ROLE)

            placeholders = ", ".join(["?" for _ in fields])
            sql = f"INSERT OR REPLACE INTO users ({', '.join(fields)}) VALUES ({placeholders})"
            cur.execute(sql, values)
        else:
            cur.execute(
                """
                INSERT OR REPLACE INTO users (username, display_name, email, password_hash, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (USERNAME, DISPLAY_NAME, EMAIL, password_hash, ROLE, 1),
            )

        conn.commit()
        logging.info("[OK] Süper admin oluşturuldu/güncellendi: __super__")
    except Exception as e:
        conn.rollback()
        logging.info(f"[ERR] Süper admin eklenemedi: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    upsert_super_admin()
