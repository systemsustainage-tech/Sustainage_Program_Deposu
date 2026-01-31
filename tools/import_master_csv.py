#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV → SQLite Master Importer
- SDG hedefleri, alt hedefler, göstergeler ve soru bankası

Kullanım örneği:
  python tools/import_master_csv.py --db data/sdg_desktop.sqlite \
    --goals data/imports/sdg_goals.csv \
    --targets data/imports/sdg_targets.csv \
    --indicators data/imports/sdg_indicators.csv \
    --questions data/imports/question_bank.csv
"""

import logging
import argparse
import csv
import os
import sqlite3
import sys
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def ensure_question_bank(conn) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS question_bank (
          id INTEGER PRIMARY KEY,
          indicator_code TEXT NOT NULL,
          q1 TEXT, q2 TEXT, q3 TEXT,
          default_unit TEXT,
          default_frequency TEXT,
          default_owner TEXT,
          default_source TEXT
        )
        """
    )
    conn.commit()


def load_goals(conn, csv_path) -> None:
    cur = conn.cursor()
    count = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = int(row['sdg_no'])
            title = row['title_tr']
            cur.execute(
                """
                INSERT INTO sdg_goals(code, title_tr)
                VALUES(?, ?)
                ON CONFLICT(code) DO UPDATE SET title_tr=excluded.title_tr
                """,
                (code, title),
            )
            count += 1
    conn.commit()
    return count


def get_goals_map(conn) -> None:
    cur = conn.cursor()
    cur.execute("SELECT id, code FROM sdg_goals")
    return {code: id for (id, code) in cur.fetchall()}


def load_targets(conn, csv_path, goals_map) -> None:
    cur = conn.cursor()
    count = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sdg_no = int(row['sdg_no'])
            code = row['target_code']
            title = row['title_tr']
            goal_id = goals_map.get(sdg_no)
            if not goal_id:
                logging.warning(f"Uyarı: hedef bulunamadı sdg_no={sdg_no} (target {code})")
                continue
            # UPSERT by unique(goal_id, code)
            cur.execute(
                """
                INSERT INTO sdg_targets(goal_id, code, title_tr)
                VALUES(?, ?, ?)
                ON CONFLICT(goal_id, code) DO UPDATE SET title_tr=excluded.title_tr
                """,
                (goal_id, code, title),
            )
            count += 1
    conn.commit()
    return count


def get_targets_map(conn) -> None:
    cur = conn.cursor()
    cur.execute("SELECT id, goal_id, code FROM sdg_targets")
    m = {}
    for (id_, goal_id, code) in cur.fetchall():
        m[(goal_id, code)] = id_
    return m


def load_indicators(conn, csv_path, goals_map, targets_map) -> None:
    cur = conn.cursor()
    count = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sdg_no = int(row['sdg_no'])
            target_code = row['target_code']
            code = row['indicator_code']
            title = row.get('title_tr') or row.get('title') or ''
            unit = row.get('unit')
            frequency = row.get('frequency') or 'Yıllık'
            topic = row.get('topic')

            goal_id = goals_map.get(sdg_no)
            if not goal_id:
                logging.warning(f"Uyarı: hedef bulunamadı sdg_no={sdg_no} (indicator {code})")
                continue
            target_id = targets_map.get((goal_id, target_code))
            if not target_id:
                logging.warning(f"Uyarı: alt hedef bulunamadı (sdg_no={sdg_no}, target_code={target_code})")
                continue

            cur.execute(
                """
                INSERT INTO sdg_indicators(target_id, code, title_tr, unit, frequency, topic)
                VALUES(?, ?, ?, ?, ?, ?)
                ON CONFLICT(target_id, code) DO UPDATE SET 
                  title_tr=excluded.title_tr,
                  unit=excluded.unit,
                  frequency=excluded.frequency,
                  topic=excluded.topic
                """,
                (target_id, code, title, unit, frequency, topic),
            )
            count += 1
    conn.commit()
    return count


def load_questions(conn, csv_path) -> None:
    ensure_question_bank(conn)
    cur = conn.cursor()
    count = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row['indicator_code']
            q1 = row.get('q1')
            q2 = row.get('q2')
            q3 = row.get('q3')
            unit = row.get('default_unit')
            freq = row.get('default_frequency') or 'Yıllık'
            owner = row.get('default_owner')
            source = row.get('default_source')
            # UPSERT mantığı: önce var mı kontrol et, varsa UPDATE, yoksa INSERT
            cur.execute("SELECT id FROM question_bank WHERE indicator_code=?", (code,))
            row_existing = cur.fetchone()
            if row_existing:
                cur.execute(
                    """
                    UPDATE question_bank
                    SET q1=?, q2=?, q3=?, default_unit=?, default_frequency=?, default_owner=?, default_source=?
                    WHERE indicator_code=?
                    """,
                    (q1, q2, q3, unit, freq, owner, source, code),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO question_bank(indicator_code,q1,q2,q3,default_unit,default_frequency,default_owner,default_source)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (code, q1, q2, q3, unit, freq, owner, source),
                )
            count += 1
    conn.commit()
    return count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=DB_PATH)
    ap.add_argument('--goals')
    ap.add_argument('--targets')
    ap.add_argument('--indicators')
    ap.add_argument('--questions')
    args = ap.parse_args()

    if not (args.goals or args.targets or args.indicators or args.questions):
        logging.info('Kullanım: en az bir CSV dosyası belirtin. --goals/--targets/--indicators/--questions')
        sys.exit(1)

    # DB
    db_path = args.db
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)

    try:
        total = 0
        if args.goals:
            logging.info('Hedefler içe aktarılıyor:', args.goals)
            total += load_goals(conn, args.goals)
        goals_map = get_goals_map(conn)

        if args.targets:
            logging.info('Alt hedefler içe aktarılıyor:', args.targets)
            total += load_targets(conn, args.targets, goals_map)
        targets_map = get_targets_map(conn)

        if args.indicators:
            logging.info('Göstergeler içe aktarılıyor:', args.indicators)
            total += load_indicators(conn, args.indicators, goals_map, targets_map)

        if args.questions:
            logging.info('Soru bankası içe aktarılıyor:', args.questions)
            total += load_questions(conn, args.questions)

        logging.info('İçe aktarma tamamlandı. Toplam kayıt/işlem:', total)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
