#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Organizasyon Şeması Geliştirici
- departments, sections ve user_departments tablolarını ekler (yoksa)

Kullanım:
  python tools/ensure_org_schema.py --db data/sdg_desktop.sqlite
"""
import logging
import argparse
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def ensure_org_tables(conn) -> None:
    cur = conn.cursor()
    # Departmanlar
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS departments (
          id INTEGER PRIMARY KEY,
          company_id INTEGER NOT NULL,
          name TEXT NOT NULL,
          parent_department_id INTEGER,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
          FOREIGN KEY(parent_department_id) REFERENCES departments(id) ON DELETE SET NULL,
          UNIQUE(company_id, name)
        )
        """
    )
    # Bölümler (Sekmeler)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sections (
          id INTEGER PRIMARY KEY,
          company_id INTEGER NOT NULL,
          department_id INTEGER NOT NULL,
          name TEXT NOT NULL,
          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
          FOREIGN KEY(department_id) REFERENCES departments(id) ON DELETE CASCADE,
          UNIQUE(company_id, department_id, name)
        )
        """
    )
    # Kullanıcı-Departman eşleştirmesi
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_departments (
          user_id INTEGER NOT NULL,
          department_id INTEGER NOT NULL,
          role TEXT,
          PRIMARY KEY(user_id, department_id),
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
          FOREIGN KEY(department_id) REFERENCES departments(id) ON DELETE CASCADE
        )
        """
    )
    conn.commit()

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    args = ap.parse_args()
    conn = sqlite3.connect(args.db)
    ensure_org_tables(conn)
    conn.close()
    logging.info("Organizasyon şeması tabloları hazırlandı:", args.db)

if __name__ == "__main__":
    main()
