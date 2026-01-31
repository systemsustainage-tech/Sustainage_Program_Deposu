#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV'den GRI yanıtlarını içe aktarır.

Beklenen CSV sütunları:
company_id,period,indicator_code,response_value

indicator_code örnekleri: "GRI 301-1", "GRI 302-1" vb.
"""

import logging
import argparse
import csv
import os
import sqlite3
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def import_csv(db_path: str, csv_path: str) -> int:
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company_id = int(row['company_id'])
            period = (row.get('period') or '').strip() or None
            code = (row.get('indicator_code') or '').strip()
            value = row.get('response_value')
            # indicator_id eşleme: gri_indicators.code
            cur.execute("SELECT id FROM gri_indicators WHERE code = ?", (code,))
            r = cur.fetchone()
            if not r:
                logging.info(f'Atlandı: bilinmeyen gösterge kodu {code}')
                continue
            indicator_id = r[0]
            # upsert basit: aynı company/period/indicator için replace
            cur.execute(
                "DELETE FROM gri_responses WHERE company_id=? AND indicator_id=? AND (period IS ? OR period = ?)",
                (company_id, indicator_id, period, period)
            )
            cur.execute(
                "INSERT INTO gri_responses(company_id, indicator_id, period, response_value) VALUES(?,?,?,?)",
                (company_id, indicator_id, period, value)
            )
            count += 1
    con.commit()
    con.close()
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
    logging.info(f'Toplam içe aktarılan GRI yanıtı: {total}')


if __name__ == '__main__':
    main()
