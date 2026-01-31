#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV'den ESG politika kayıtlarını içe aktarır.

CSV beklenen sütunlar:
company_id,pillar,policy_name,status,document_url,notes

Kullanım:
  python tools/import_esg_policies_csv.py --db data/sdg_desktop.sqlite --csv data/imports/templates/esg/policies.csv
"""

import logging
import argparse
import csv
import os
import sqlite3
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def import_csv(db_path: str, csv_path: str) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                """
                INSERT INTO esg_policies(company_id, pillar, policy_name, status, document_url, notes)
                VALUES(?,?,?,?,?,?)
                """,
                (
                    int(row.get('company_id') or 1),
                    (row.get('pillar') or 'E').strip(),
                    row.get('policy_name') or '',
                    (row.get('status') or 'Planned').strip(),
                    row.get('document_url'),
                    row.get('notes')
                )
            )
            count += 1
    conn.commit()
    conn.close()
    return count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=DB_PATH)
    ap.add_argument('--csv', required=True)
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        logging.info('CSV dosyası bulunamadı:', args.csv)
        raise SystemExit(1)

    total = import_csv(args.db, args.csv)
    logging.info(f'Toplam içe aktarılan politika: {total}')


if __name__ == '__main__':
    main()
