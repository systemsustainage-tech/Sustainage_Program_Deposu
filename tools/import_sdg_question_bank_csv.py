#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Soru Bankası CSV Importer
sdg_232_questions.csv dosyasındaki gerçek soruları sdg_question_bank tablosuna yükler.

Kullanım:
  python tools/import_sdg_question_bank_csv.py \
    --db data/sdg_desktop.sqlite \
    --csv sdg_232_questions.csv
"""

import logging
import argparse
import csv
import os
import sqlite3
import sys

# Tablo ve soru tipi kurulumunu gerekirse sdg_question_bank modülü üzerinden tetikleyebiliriz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sdg.sdg_question_bank import SDGQuestionBank
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def import_questions(db_path: str, csv_path: str) -> int:
    # Tabloların varlığını ve tiplerin kurulumunu garanti altına al
    SDGQuestionBank(db_path)  # constructor tablo oluşturmayı tetikliyor

    # Metin tipi ("Metin") ID'sini al
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id FROM sdg_question_types WHERE type_name=?", ("Metin",))
    row = cur.fetchone()
    text_type_id = row[0] if row else 1  # varsayılan 1 kabul

    imported = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Beklenen başlıklar: SDG No, Gösterge Kodu, Soru 1, Soru 2, Soru 3
        for row in reader:
            try:
                sdg_no_raw = row.get('SDG No') or row.get('sdg_no')
                indicator_code = row.get('Gösterge Kodu') or row.get('indicator_code')
                if not sdg_no_raw or not indicator_code:
                    continue
                sdg_no = int(str(sdg_no_raw).strip())

                questions = [
                    row.get('Soru 1') or row.get('q1'),
                    row.get('Soru 2') or row.get('q2'),
                    row.get('Soru 3') or row.get('q3'),
                ]

                for q in questions:
                    q_text = (q or '').strip()
                    if not q_text:
                        continue
                    cur.execute(
                        """
                        INSERT INTO sdg_question_bank (
                            sdg_no, indicator_code, question_text, question_type_id,
                            difficulty_level, is_required, points
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (sdg_no, indicator_code, q_text, text_type_id, 'medium', 1, 1),
                    )
                    imported += 1
            except Exception as e:
                logging.error(f"Satır import hatası (indicator={row.get('Gösterge Kodu') or row.get('indicator_code')}): {e}")
                continue

    conn.commit()
    conn.close()
    return imported


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=DB_PATH)
    ap.add_argument('--csv', required=True)
    args = ap.parse_args()

    if not os.path.exists(args.csv):
        logging.info(f"CSV dosyası bulunamadı: {args.csv}")
        sys.exit(1)

    total = import_questions(args.db, args.csv)
    logging.info(f"Toplam eklenen soru: {total}")


if __name__ == '__main__':
    main()
