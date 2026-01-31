#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mevcut SQLite veritabanında eşleştirme şemasını güvence altına alma
- map_sdg_gri tablosunda relation_type sütunu yoksa ekler
"""

import logging
import argparse
import re
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def column_exists(cur, table: str, column: str) -> bool:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table or ""):
        return False
    cur.execute("PRAGMA table_info(" + table + ")")
    return any(row[1] == column for row in cur.fetchall())


def ensure_mapping_schema(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # map_sdg_gri için relation_type kontrolü
        if not column_exists(cur, 'map_sdg_gri', 'relation_type'):
            cur.execute("ALTER TABLE map_sdg_gri ADD COLUMN relation_type TEXT")
            logging.info("map_sdg_gri: relation_type sütunu eklendi")
        else:
            logging.info("map_sdg_gri: relation_type sütunu zaten mevcut")

        conn.commit()
    finally:
        conn.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True, help='SQLite DB yolu')
    args = ap.parse_args()
    ensure_mapping_schema(args.db)


if __name__ == '__main__':
    main()
