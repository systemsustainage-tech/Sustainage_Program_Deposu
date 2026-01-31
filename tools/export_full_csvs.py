#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanından Tam CSV Exporter
- sdg_goals, sdg_targets, sdg_indicators, question_bank (varsa) CSV üretir

Kullanım:
  python tools/export_full_csvs.py --db data/sdg_desktop.sqlite --outdir data/imports/generated
"""
import logging
import argparse
import csv
import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def export_table(cur, query, headers, out_path) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        wr = csv.writer(f)
        wr.writerow(headers)
        for row in cur.execute(query):
            wr.writerow(row)
    logging.info("Export edildi:", out_path)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--outdir", required=True)
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    export_table(
        cur,
        "SELECT code, title_tr FROM sdg_goals ORDER BY code",
        ["sdg_no", "title_tr"],
        os.path.join(args.outdir, "sdg_goals.csv")
    )

    export_table(
        cur,
        """
        SELECT g.code AS sdg_no, t.code AS target_code, t.title_tr
        FROM sdg_targets t JOIN sdg_goals g ON t.goal_id = g.id
        ORDER BY g.code, t.code
        """,
        ["sdg_no", "target_code", "title_tr"],
        os.path.join(args.outdir, "sdg_targets.csv")
    )

    # sdg_indicators şema farklılıklarına karşı esnek export
    cur.execute("PRAGMA table_info(sdg_indicators)")
    cols = {row[1] for row in cur.fetchall()}
    has_basic = {"code", "title_tr", "target_id"}.issubset(cols)
    # Her durumda temel alanları yazalım
    if has_basic:
        if {"unit", "frequency", "topic"}.issubset(cols):
            ind_query = (
                """
                SELECT g.code AS sdg_no, t.code AS target_code, i.code AS indicator_code,
                       i.title_tr, i.unit, i.frequency, i.topic
                FROM sdg_indicators i
                JOIN sdg_targets t ON i.target_id = t.id
                JOIN sdg_goals g ON t.goal_id = g.id
                ORDER BY g.code, t.code, i.code
                """
            )
            ind_headers = ["sdg_no", "target_code", "indicator_code", "title_tr", "unit", "frequency", "topic"]
        else:
            # Genişletilmiş şemada unit/frequency/topic yoksa sadece temel alanları export et
            ind_query = (
                """
                SELECT g.code AS sdg_no, t.code AS target_code, i.code AS indicator_code,
                       i.title_tr
                FROM sdg_indicators i
                JOIN sdg_targets t ON i.target_id = t.id
                JOIN sdg_goals g ON t.goal_id = g.id
                ORDER BY g.code, t.code, i.code
                """
            )
            ind_headers = ["sdg_no", "target_code", "indicator_code", "title_tr"]
        export_table(
            cur,
            ind_query,
            ind_headers,
            os.path.join(args.outdir, "sdg_indicators.csv")
        )
    else:
        logging.warning("Uyarı: sdg_indicators şeması beklenen temel alanları içermiyor, export atlandı.")

    # question_bank opsiyonel
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='question_bank'")
    if cur.fetchone():
        export_table(
            cur,
            "SELECT indicator_code, q1, q2, q3, default_unit, default_frequency, default_owner, default_source FROM question_bank ORDER BY indicator_code",
            ["indicator_code","q1","q2","q3","default_unit","default_frequency","default_owner","default_source"],
            os.path.join(args.outdir, "question_bank.csv")
        )

    conn.close()
    logging.info("Tam CSV export tamamlandı:", args.outdir)

if __name__ == "__main__":
    main()
