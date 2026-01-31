#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER_232 (SDG_232.xlsx) → SQLite Importer
- SDG hedef/alt hedef/gösterge kayıtlarını günceller
- SDG↔GRI ve SDG↔TSRS eşleştirmelerini günceller

Kullanım:
  python tools/import_from_master_excel.py --db data/sdg_desktop.sqlite --excel SDG_232.xlsx
"""

import logging
import argparse
import os
import sqlite3
from typing import List, Optional, Tuple
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    import pandas as pd
except Exception as e:
    raise RuntimeError("pandas + openpyxl gereklidir: pip install pandas openpyxl") from e


SHEET_NAME = 'MASTER_232'


def upsert_goal(cur, sdg_no: int, title_tr: str) -> int:
    cur.execute("SELECT id FROM sdg_goals WHERE code=?", (sdg_no,))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE sdg_goals SET title_tr=? WHERE id=?", (title_tr, row[0]))
        return row[0]
    cur.execute("INSERT INTO sdg_goals (code, title_tr) VALUES (?, ?)", (sdg_no, title_tr))
    return cur.lastrowid


def upsert_target(cur, goal_id: int, code: str, title_tr: str) -> int:
    cur.execute("SELECT id FROM sdg_targets WHERE goal_id=? AND code=?", (goal_id, code))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE sdg_targets SET title_tr=? WHERE id=?", (title_tr, row[0]))
        return row[0]
    cur.execute("INSERT INTO sdg_targets (goal_id, code, title_tr) VALUES (?, ?, ?)", (goal_id, code, title_tr))
    return cur.lastrowid


def upsert_indicator(cur, target_id: int, code: str, title_tr: str) -> int:
    cur.execute("SELECT id FROM sdg_indicators WHERE target_id=? AND code=?", (target_id, code))
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE sdg_indicators SET title_tr=? WHERE id=?", (title_tr, row[0]))
        return row[0]
    cur.execute("INSERT INTO sdg_indicators (target_id, code, title_tr) VALUES (?, ?, ?)", (target_id, code, title_tr))
    return cur.lastrowid


def parse_gri_connections(text: str) -> List[Tuple[str, Optional[str]]]:
    """'GRI 102/205/206' gibi değerleri [('GRI 102', None), ...] olarak döndür."""
    if not text:
        return []
    s = str(text).strip()
    if not s:
        return []
    parts = s.replace('GRI', '').strip()
    standards = [p.strip() for p in parts.split('/') if p.strip()]
    result = [(f'GRI {st}', None) for st in standards]
    return result


def parse_tsrs_connections(text: str) -> List[Tuple[str, Optional[str], Optional[str]]]:
    """'TSRS-1 (Yönetim/Genel)' -> [('TSRS-1', None, 'Yönetim/Genel')]"""
    if not text:
        return []
    s = str(text).strip()
    if not s:
        return []
    section = s
    notes = None
    if '(' in s and ')' in s:
        section = s.split('(')[0].strip()
        notes = s[s.find('(')+1:s.rfind(')')].strip()
    return [(section, None, notes)]


def upsert_map_sdg_gri(cur, sdg_indicator_code: str, gri_standard: str, gri_disclosure: Optional[str], relation_type: Optional[str], notes: Optional[str]) -> None:
    cur.execute(
        "SELECT id FROM map_sdg_gri WHERE sdg_indicator_code=? AND gri_standard=? AND COALESCE(gri_disclosure,'')=COALESCE(?, '')",
        (sdg_indicator_code, gri_standard, gri_disclosure)
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE map_sdg_gri SET relation_type=?, notes=? WHERE id=?",
            (relation_type, notes, row[0])
        )
        return row[0]
    cur.execute(
        "INSERT INTO map_sdg_gri (sdg_indicator_code, gri_standard, gri_disclosure, relation_type, notes) VALUES (?, ?, ?, ?, ?)",
        (sdg_indicator_code, gri_standard, gri_disclosure, relation_type, notes)
    )
    return cur.lastrowid


def upsert_map_sdg_tsrs(cur, sdg_indicator_code: str, tsrs_section: str, tsrs_metric: Optional[str], relation_type: Optional[str], notes: Optional[str]) -> None:
    # Bazı DB sürümlerinde tsrs_metric NOT NULL; güvenli varsayılan üret
    safe_metric = tsrs_metric if (tsrs_metric and str(tsrs_metric).strip()) else (notes if (notes and str(notes).strip()) else 'Genel')
    cur.execute(
        "SELECT id FROM map_sdg_tsrs WHERE sdg_indicator_code=? AND tsrs_section=? AND COALESCE(tsrs_metric,'')=COALESCE(?, '')",
        (sdg_indicator_code, tsrs_section, safe_metric)
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE map_sdg_tsrs SET relation_type=?, notes=? WHERE id=?",
            (relation_type, notes, row[0])
        )
        return row[0]
    cur.execute(
        "INSERT INTO map_sdg_tsrs (sdg_indicator_code, tsrs_section, tsrs_metric, relation_type, notes) VALUES (?, ?, ?, ?, ?)",
        (sdg_indicator_code, tsrs_section, safe_metric, relation_type, notes)
    )
    return cur.lastrowid


def import_master(db_path: str, excel_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        df = pd.read_excel(excel_path, sheet_name=SHEET_NAME)

        cols = df.columns
        required = ['Sürdürülebilir Kalkınma Hedefi No:', 'SDG Başlık', 'Alt Hedef Kodu', 'Alt Hedef Tanımı (TR)', 'Gösterge Kodu', 'Gösterge Tanımı (TR)']
        for r in required:
            if r not in cols:
                raise RuntimeError(f"Gerekli kolon eksik: {r}")

        gri_col = 'GRI Bağlantısı' if 'GRI Bağlantısı' in cols else None
        tsrs_col = 'TSRS Bağlantısı' if 'TSRS Bağlantısı' in cols else None

        total_rows = 0
        total_gri = 0
        total_tsrs = 0

        for _, row in df.iterrows():
            sdg_no = int(row['Sürdürülebilir Kalkınma Hedefi No:'])
            sdg_title = str(row['SDG Başlık']).strip()
            target_code = str(row['Alt Hedef Kodu']).strip()
            target_title = str(row['Alt Hedef Tanımı (TR)']).strip()
            indicator_code = str(row['Gösterge Kodu']).strip()
            indicator_title = str(row['Gösterge Tanımı (TR)']).strip()

            goal_id = upsert_goal(cur, sdg_no, sdg_title)
            target_id = upsert_target(cur, goal_id, target_code, target_title)
            upsert_indicator(cur, target_id, indicator_code, indicator_title)
            total_rows += 1

            # GRI eşleştirmeleri
            if gri_col:
                connections = parse_gri_connections(row.get(gri_col))
                for std, disc in connections:
                    upsert_map_sdg_gri(cur, indicator_code, std, disc, None, None)
                    total_gri += 1

            # TSRS eşleştirmeleri
            if tsrs_col:
                connections_t = parse_tsrs_connections(row.get(tsrs_col))
                for section, metric, notes in connections_t:
                    upsert_map_sdg_tsrs(cur, indicator_code, section, metric, None, notes)
                    total_tsrs += 1

        conn.commit()
        logging.info(f"İçe aktarma tamamlandı: {total_rows} satır; GRI eşleşme {total_gri}; TSRS eşleşme {total_tsrs}")
    finally:
        conn.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=DB_PATH)
    ap.add_argument('--excel', default='SDG_232.xlsx')
    args = ap.parse_args()
    if not os.path.exists(args.excel):
        raise SystemExit(f"Excel bulunamadı: {args.excel}")
    import_master(args.db, args.excel)


if __name__ == '__main__':
    main()
