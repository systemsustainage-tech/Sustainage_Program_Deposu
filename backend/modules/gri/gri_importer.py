#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI importörü (SDG_232.xlsx / MASTER_232 uyumlu)
- MASTER_232 içindeki 'GRI Bağlantısı' verilerinden GRI standartlarını gri_standards tablosuna ekler
- Disclosure kodu yoksa yalnızca standartları günceller
"""

import logging
import argparse
import sqlite3
from typing import Optional

try:
    import pandas as pd
except Exception as e:
    raise RuntimeError("pandas paketine ihtiyaç var: pip install pandas openpyxl") from e


def find_column(df, candidates) -> None:
    for cand in candidates:
        if cand in df.columns:
            return cand
    return None


def guess_category(code: str) -> str:
    # Basit kategorizasyon
    if code.startswith('GRI 2') or code.startswith('GRI 3'):
        return 'Universal'
    try:
        num = int(code.split()[1].split('-')[0])
    except Exception:
        return 'Unknown'
    if 201 <= num <= 207:
        return 'Economic'
    if 301 <= num <= 308:
        return 'Environmental'
    if 401 <= num <= 419:
        return 'Social'
    return 'Unknown'


def upsert_standard(cur, code: str, title: Optional[str]) -> int:
    cur.execute("SELECT id FROM gri_standards WHERE code = ?", (code,))
    row = cur.fetchone()
    if row:
        return row[0]
    category = guess_category(code)
    cur.execute(
        "INSERT INTO gri_standards (code, title, category) VALUES (?, ?, ?)",
        (code, title or code, category),
    )
    return cur.lastrowid


def upsert_indicator(cur, standard_id: int, code: str, title: Optional[str], unit: Optional[str], methodology: Optional[str]) -> None:
    cur.execute("SELECT id FROM gri_indicators WHERE standard_id = ? AND code = ?", (standard_id, code))
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE gri_indicators SET title = ?, unit = ?, methodology = ? WHERE id = ?",
            (title, unit, methodology, row[0]),
        )
        return row[0]
    cur.execute(
        "INSERT INTO gri_indicators (standard_id, code, title, unit, methodology) VALUES (?, ?, ?, ?, ?)",
        (standard_id, code, title, unit, methodology),
    )
    return cur.lastrowid


def import_excel(db_path: str, excel_path: str, sheet: Optional[str]) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        # MASTER_232 sayfasını oku ve GRI Bağlantısı kolonundan standartları çıkar
        df = pd.read_excel(excel_path, sheet_name=sheet or 'MASTER_232')
        gri_col = find_column(df, ['GRI Bağlantısı'])

        if not gri_col:
            raise RuntimeError("'GRI Bağlantısı' kolonu bulunamadı (MASTER_232)")

        count_std = 0
        for _, row in df.iterrows():
            txt = row.get(gri_col)
            if not pd.notna(txt):
                continue
            parts = str(txt).replace('GRI', '').strip().split('/')
            for p in parts:
                code = p.strip()
                if not code:
                    continue
                upsert_standard(cur, f'GRI {code}', None)
                count_std += 1

        conn.commit()
        logging.info(f"Import tamamlandı: {count_std} GRI standardı işlendi")
    finally:
        conn.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True, help='SQLite DB yolu')
    ap.add_argument('--excel', required=True, help='Excel dosyası (örn. SDG_232.xlsx)')
    ap.add_argument('--sheet', required=False, help='Sayfa adı')
    args = ap.parse_args()
    import_excel(args.db, args.excel, args.sheet)


if __name__ == '__main__':
    main()
