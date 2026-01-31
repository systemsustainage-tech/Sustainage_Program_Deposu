#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBAM CSV → SQLite import betiği

Beklenen CSV başlıkları:
company_id,reporting_quarter,product_cn_code,country_of_origin,quantity_tonnes,
direct_emissions_tco2e_per_tonne,indirect_emissions_tco2e_per_tonne,
emission_calculation_method,installation_id,production_route,
electricity_emissions_factor,documentation_ref

Kullanım:
  python tools/import_cbam_csv.py --db data/sdg_desktop.sqlite --csv data/imports/templates/eu/cbam/reports.csv

Tablo yoksa oluşturur: cbam_imports
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
CREATE TABLE IF NOT EXISTS cbam_imports (
    id INTEGER PRIMARY KEY,
    company_id TEXT,
    reporting_quarter TEXT,
    product_cn_code TEXT,
    country_of_origin TEXT,
    quantity_tonnes REAL,
    direct_emissions_tco2e_per_tonne REAL,
    indirect_emissions_tco2e_per_tonne REAL,
    emission_calculation_method TEXT,
    installation_id TEXT,
    production_route TEXT,
    electricity_emissions_factor REAL,
    documentation_ref TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_SQL = """
INSERT INTO cbam_imports (
 company_id, reporting_quarter, product_cn_code, country_of_origin,
 quantity_tonnes, direct_emissions_tco2e_per_tonne, indirect_emissions_tco2e_per_tonne,
 emission_calculation_method, installation_id, production_route,
 electricity_emissions_factor, documentation_ref
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
"""

EXPECTED_HEADERS = [
    'company_id', 'reporting_quarter', 'product_cn_code', 'country_of_origin',
    'quantity_tonnes', 'direct_emissions_tco2e_per_tonne', 'indirect_emissions_tco2e_per_tonne',
    'emission_calculation_method', 'installation_id', 'production_route',
    'electricity_emissions_factor', 'documentation_ref'
]

def ensure_table(conn: sqlite3.Connection) -> None:
    conn.executescript(TABLE_SQL)
    conn.commit()

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
                row.get('reporting_quarter'),
                row.get('product_cn_code'),
                row.get('country_of_origin'),
                _to_float(row.get('quantity_tonnes')),
                _to_float(row.get('direct_emissions_tco2e_per_tonne')),
                _to_float(row.get('indirect_emissions_tco2e_per_tonne')),
                row.get('emission_calculation_method'),
                row.get('installation_id'),
                row.get('production_route'),
                _to_float(row.get('electricity_emissions_factor')),
                row.get('documentation_ref'),
            ]
            cur.execute(INSERT_SQL, vals)
            count += 1
        conn.commit()
    conn.close()
    return count

def _to_float(val) -> None:
    if val is None or val == '':
        return None
    try:
        return float(val)
    except Exception:
        return None

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
    logging.info(f"Import tamam: {n} satır → {db_path} (cbam_imports)")

if __name__ == '__main__':
    main()
