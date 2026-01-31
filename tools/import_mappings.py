#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV → SQLite Importer
Kullanım örnekleri:
  python tools/import_mappings.py --db "%LOCALAPPDATA%/SDGDesktop/sdg_desktop.sqlite" --type sdg_gri eslestirme/sdg_gri/samples_sdg_gri.csv
  python tools/import_mappings.py --db "/Users/you/Library/Application Support/SDGDesktop/sdg_desktop.sqlite" --type sdg_tsrs eslestirme/sdg_tsrs/samples_sdg_tsrs.csv
"""
import logging
import argparse
import csv
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def upsert_sdg_gri(cur, row) -> None:
    cur.execute("""INSERT INTO map_sdg_gri(sdg_indicator_code,gri_standard,gri_disclosure,relation_type,notes)
                   VALUES(?,?,?,?,?)""", (row['sdg_indicator_code'], row['gri_standard'], row['gri_disclosure'], row.get('relation_type'), row.get('notes')))

def upsert_sdg_tsrs(cur, row) -> None:
    cur.execute("""INSERT INTO map_sdg_tsrs(sdg_indicator_code,tsrs_section,tsrs_metric,relation_type,notes)
                   VALUES(?,?,?,?,?)""", (row['sdg_indicator_code'], row['tsrs_section'], row['tsrs_metric'], row.get('relation_type'), row.get('notes')))

def upsert_gri_tsrs(cur, row) -> None:
    cur.execute("""INSERT INTO map_gri_tsrs(gri_standard,gri_disclosure,tsrs_section,tsrs_metric,relation_type,notes)
                   VALUES(?,?,?,?,?,?)""", (row['gri_standard'], row['gri_disclosure'], row['tsrs_section'], row['tsrs_metric'], row.get('relation_type'), row.get('notes')))

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--type", choices=["sdg_gri","sdg_tsrs","gri_tsrs"], required=True)
    ap.add_argument("csv_path")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur  = conn.cursor()

    with open(args.csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if args.type == "sdg_gri":
                upsert_sdg_gri(cur, row)
            elif args.type == "sdg_tsrs":
                upsert_sdg_tsrs(cur, row)
            else:
                upsert_gri_tsrs(cur, row)
    conn.commit()
    conn.close()
    logging.info("Import tamamlandı:", args.type, args.csv_path)

if __name__ == "__main__":
    main()
