#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hızlı doğrulama: ReportingManager liste/lock/sil/geri yükle"""
import logging
import os
import sys
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(base_dir))

def main() -> None:
    from raporlama.reporting_manager import ReportingManager
    m = ReportingManager(DB_PATH)
    rows = m.list_reports(limit=5, include_deleted=True)
    logging.info(f"rows={rows}")
    logging.info(f"count={len(rows)}")
    if rows:
        rid = rows[0][0]
        logging.info(f"first id={rid}")
        m.set_lock(rid, True)
        logging.info(f"locked={m.get_report(rid)}")
        m.set_lock(rid, False)
        logging.info(f"unlocked={m.get_report(rid)}")
        m.delete_report(rid)
        logging.info(f"deleted={m.get_report(rid)}")
        m.restore_report(rid)
        logging.info(f"restored={m.get_report(rid)}")

if __name__ == "__main__":
    main()
