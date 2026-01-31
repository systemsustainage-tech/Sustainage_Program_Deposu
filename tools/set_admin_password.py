#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sqlite3
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
    username = '__super__'
    new_password = 'Kayra_1507'

    try:
        from security.core.secure_password import hash_password as sp_hash
        from security.core.secure_password import verify_password as sp_verify
    except Exception as e:
        logging.error(f"[ERROR] Güvenlik modülü yüklenemedi: {e}")
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute("SELECT id, username FROM users WHERE LOWER(username)=LOWER(?)", (username,))
        row = cur.fetchone()
        if not row:
            logging.error(f"[ERROR] Kullanıcı bulunamadı: {username}")
            conn.close()
            sys.exit(2)

        new_hash = sp_hash(new_password)
        cur.execute("PRAGMA table_info(users)")
        cols = {c[1] for c in cur.fetchall()}
        set_parts = ["password_hash = ?", "pw_hash_version = 'argon2'", "is_active = 1", "role = 'super_admin'"]
        params = [new_hash]
        if 'failed_attempts' in cols:
            set_parts.append("failed_attempts = 0")
        if 'locked_until' in cols:
            set_parts.append("locked_until = NULL")
        if 'must_change_password' in cols:
            set_parts.append("must_change_password = 0")
        sql = f"UPDATE users SET {', '.join(set_parts)} WHERE LOWER(username) = LOWER(?)"
        params.append(username)
        cur.execute(sql, params)
        conn.commit()

        cur.execute("SELECT password_hash FROM users WHERE LOWER(username)=LOWER(?)", (username,))
        stored = cur.fetchone()[0]
        conn.close()

        ok, needs = sp_verify(stored, new_password)
        logging.info(f"[OK] __super__ şifresi güncellendi. Doğrulama: {ok}, rehash_gerekli={needs}")
        sys.exit(0 if ok else 3)

    except Exception as e:
        logging.error(f"[ERROR] Şifre güncelleme hatası: {e}")
        sys.exit(4)

if __name__ == '__main__':
    main()
