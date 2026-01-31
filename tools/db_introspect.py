import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Basit veritabanı introspection aracı.
sdg.db ve data/sdg_desktop.sqlite içindeki users ve ilişkili tabloların
kolonlarını ve kayıt sayılarını döker.
"""

import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def introspect(db_path: str) -> None:
    logging.info(f"\n DB: {db_path} | exists={os.path.exists(db_path)}")
    if not os.path.exists(db_path):
        return
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute('PRAGMA table_info(users)')
        cols = [(r[1], r[2]) for r in cur.fetchall()]
        logging.info(f"   users kolonları ({len(cols)}): "+', '.join([f"{n}:{t}" for n,t in cols]))
        try:
            cur.execute('SELECT COUNT(*) FROM users')
            count = cur.fetchone()[0]
            logging.info(f"   kullanıcı sayısı: {count}")
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        # örnek kolon değerleri (olanları)
        sample_cols = [
            'username','email','password_hash','role','display_name',
            'first_name','last_name','is_active','must_change_password',
            'login_attempts','failed_attempts','locked_until','last_login',
            'last_login_at','totp_enabled','totp_secret','backup_codes'
        ]
        for c in sample_cols:
            try:
                cur.execute(f'SELECT {c} FROM users LIMIT 1')
                row = cur.fetchone()
                logging.info(f"    kolonu var: {c} -> örnek: {row[0] if row else None}")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        # ilişkili tablolar
        related = ['roles','user_roles','permissions','role_permissions','user_permissions']
        import re
        for t in related:
            try:
                if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", t or ""):
                    continue
                cur.execute('SELECT COUNT(*) FROM ' + t)
                n = cur.fetchone()[0]
                logging.info(f"   ↪ {t} satır sayısı: {n}")
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        conn.close()
    except Exception as e:
        logging.error(f"    hata: {e}")


def main() -> None:
    base = os.getcwd()
    dbs = [
        os.path.join(base, 'sdg.db'),
        os.path.join(base, 'data', 'sdg_desktop.sqlite'),
    ]
    logging.info('Veritabanı users şema karşılaştırması')
    logging.info('='*70)
    for db in dbs:
        introspect(db)
    logging.info('\nİnceleme bitti.')


if __name__ == '__main__':
    main()
