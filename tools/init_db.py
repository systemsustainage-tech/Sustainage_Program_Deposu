#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite başlangıç: şema + seed + seed_plus
Kullanım:
  python tools/init_db.py --db mydb.sqlite --schema data/db/schema.sql --seed data/seeds/seed_sdg.sql --plus data/seeds/seed_plus.sql
"""
import logging
import argparse
import os
import sqlite3
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_sql(conn, path) -> None:
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--schema", default="schema.sql")
    ap.add_argument("--seed",   default="data/seeds/seed_sdg.sql")
    ap.add_argument("--plus",   default="data/seeds/seed_plus.sql")
    args = ap.parse_args()

    if not os.path.exists(args.schema):
        sys.exit("schema yok: "+args.schema)
    if not os.path.exists(args.seed):
        sys.exit("seed yok: "+args.seed)
    if not os.path.exists(args.plus):
        sys.exit("seed_plus yok: "+args.plus)

    conn = sqlite3.connect(args.db)
    run_sql(conn, args.schema)
    run_sql(conn, args.seed)
    run_sql(conn, args.plus)
    conn.commit()
    conn.close()
    logging.info("DB init tamam:", args.db)

if __name__ == "__main__":
    main()
