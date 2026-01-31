#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reset_tokens tablosu ve indekslerini doğrulama aracı.

Kullanım:
    python tools/check_reset_tokens.py <db_path>

Örnek:
    python tools/check_reset_tokens.py data/sdg_desktop.sqlite
"""

import logging
import sqlite3
import sys
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    logging.info(f" Veritabanı: {db_path}")

    # Tablo var mı?
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name='reset_tokens'")
    table = cur.fetchone()
    logging.info("\n reset_tokens tablosu mevcut mu? ", bool(table))
    if table:
        logging.info("\n Tablo Şeması:\n", table[1])

    # Indeksler
    cur.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='reset_tokens'")
    indexes = cur.fetchall()
    logging.info("\n Indeksler:", [name for name, _ in indexes])
    for name, sql in indexes:
        logging.info(f"  - {name}: {sql}")

    conn.close()
    return bool(table)


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    exists = check(db_path)
    sys.exit(0 if exists else 1)
