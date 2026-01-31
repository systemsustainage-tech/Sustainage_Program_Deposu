#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESG politika/taahhüt kütüphanesi tablolarını oluşturur.

Kullanım:
  python tools/init_esg_policy_library.py --db data/sdg_desktop.sqlite
"""

import logging
import argparse
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def init_tables(conn) -> None:
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS esg_policies (
          id INTEGER PRIMARY KEY,
          company_id INTEGER NOT NULL,
          pillar TEXT NOT NULL,               -- 'E' | 'S' | 'G'
          policy_name TEXT NOT NULL,
          status TEXT DEFAULT 'Planned',      -- Planned/Approved/Published
          document_url TEXT,
          notes TEXT,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_esg_policies_company ON esg_policies(company_id);
        CREATE INDEX IF NOT EXISTS idx_esg_policies_pillar ON esg_policies(pillar);
        """
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True)
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    try:
        init_tables(conn)
        conn.commit()
        logging.info('ESG politika kütüphanesi tabloları hazırlandı:', args.db)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
