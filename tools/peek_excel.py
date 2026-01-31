#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Basit Excel önizleme: sayfa adları ve ilk satırlar"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    try:
        import pandas as pd
    except Exception as e:
        logging.info(f"Pandas yüklenemedi: {e}")
        sys.exit(1)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_path = os.path.join(base_dir, "SDG_232.xlsx")
    path = sys.argv[1] if len(sys.argv) > 1 else default_path
    if not os.path.exists(path):
        logging.info(f"Dosya yok: {path}")
        sys.exit(1)

    try:
        xls = pd.ExcelFile(path)
        logging.info("Sheets:", xls.sheet_names)
        for name in xls.sheet_names[:2]:
            df = pd.read_excel(path, sheet_name=name)
            logging.info(f"\n--- {name} (ilk 5 satır) ---")
            try:
                logging.info(df.head().to_string(index=False))
            except Exception:
                logging.info(df.head())
    except Exception as e:
        logging.error(f"Okuma hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
