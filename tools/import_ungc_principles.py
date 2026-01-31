#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNGC Ten Principles CSV → SQLite import

Beklenen CSV başlıkları:
company_id,principle_no,principle_area,commitment_level,status,last_update,
evidence_url,mapping_gri_indicator_code,mapping_sdg_goal,mapping_tsrs_code,notes

Kullanım:
  python tools/import_ungc_principles.py --db data/sdg_desktop.sqlite --csv data/imports/templates/ungc/principles.csv

Tablo yoksa oluşturur: ungc_principles
"""

import logging
import argparse
import csv
import os
import sqlite3
import sys
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ungc_principles (
    id INTEGER PRIMARY KEY,
    company_id TEXT,
    principle_no INTEGER,
    principle_area TEXT,
    commitment_level TEXT,
    status TEXT,
    last_update TEXT,
    evidence_url TEXT,
    mapping_gri_indicator_code TEXT,
    mapping_sdg_goal TEXT,
    mapping_tsrs_code TEXT,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_SQL = """
INSERT INTO ungc_principles (
 company_id, principle_no, principle_area, commitment_level, status, last_update,
 evidence_url, mapping_gri_indicator_code, mapping_sdg_goal, mapping_tsrs_code, notes
) VALUES (?,?,?,?,?,?,?,?,?,?,?)
"""

EXPECTED_HEADERS = [
    'company_id','principle_no','principle_area','commitment_level','status','last_update',
    'evidence_url','mapping_gri_indicator_code','mapping_sdg_goal','mapping_tsrs_code','notes'
]

def ensure_table(conn: sqlite3.Connection) -> None:
    conn.executescript(TABLE_SQL)
    conn.commit()

def _to_int(val) -> None:
    if val is None or val == '':
        return None
    try:
        return int(val)
    except Exception:
        return None

def import_csv(db_path: str, csv_path: str) -> int:
    conn = sqlite3.connect(db_path)
    ensure_table(conn)
    cur = conn.cursor()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        missing = [h for h in EXPECTED_HEADERS if h not in reader.fieldnames]
        if missing:
            conn.close()
            raise RuntimeError(f"Eksik başlık(lar): {missing}")
        count = 0
        for row in reader:
            vals = [
                row.get('company_id'),
                _to_int(row.get('principle_no')),
                row.get('principle_area'),
                row.get('commitment_level'),
                row.get('status'),
                row.get('last_update'),
                row.get('evidence_url'),
                row.get('mapping_gri_indicator_code'),
                row.get('mapping_sdg_goal'),
                row.get('mapping_tsrs_code'),
                row.get('notes'),
            ]
            cur.execute(INSERT_SQL, vals)
            count += 1
        conn.commit()
    conn.close()
    return count

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=DB_PATH)
    ap.add_argument('--csv', required=True)
    args = ap.parse_args()

    db_path = os.path.abspath(args.db)
    csv_path = os.path.abspath(args.csv)
    if not os.path.exists(csv_path):
        sys.exit(f"CSV bulunamadı: {csv_path}")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    n = import_csv(db_path, csv_path)
    logging.info(f"Import tamam: {n} satır → {db_path} (ungc_principles)")

if __name__ == '__main__':
    main()
