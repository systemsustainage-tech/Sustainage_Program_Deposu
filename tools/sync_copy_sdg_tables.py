import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG tablolarını kaynak DB'den hedef DB'ye senkronize kopyalar.

İşlem:
- Hedef DB'de sdg_goals/targets/indicators ve question_bank tablolarını güvenli şekilde yeniden oluştur
- Kaynak DB'yi ATTACH ederek tabloları kopyala

Kullanım:
  python tools/sync_copy_sdg_tables.py --src backup/sdg_desktop.sqlite --dst data/sdg_desktop.sqlite
"""

import argparse
import os
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SCHEMA_SQL = os.path.join('data', 'db', 'schema.sql')


def run_sql(conn, path) -> None:
    with open(path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())


def ensure_question_bank(conn) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS question_bank (
          id INTEGER PRIMARY KEY,
          indicator_code TEXT NOT NULL,
          q1 TEXT, q2 TEXT, q3 TEXT,
          default_unit TEXT,
          default_frequency TEXT,
          default_owner TEXT,
          default_source TEXT
        );
        """
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True, help='Kaynak SQLite DB (doğru şema ve veri)')
    ap.add_argument('--dst', required=True, help='Hedef SQLite DB (uygulama tarafından kullanılan)')
    args = ap.parse_args()

    src = os.path.abspath(args.src)
    dst = os.path.abspath(args.dst)
    if not os.path.exists(src):
        raise SystemExit(f'Kaynak DB bulunamadı: {src}')

    conn = sqlite3.connect(dst, uri=True)
    try:
        cur = conn.cursor()
        # Hedefte SDG tablolarını temiz kur
        cur.executescript(
            """
            DROP TABLE IF EXISTS evidence;
            DROP TABLE IF EXISTS responses;
            DROP TABLE IF EXISTS sdg_indicators;
            DROP TABLE IF EXISTS sdg_targets;
            DROP TABLE IF EXISTS sdg_goals;
            DROP TABLE IF EXISTS question_bank;
            """
        )
        run_sql(conn, SCHEMA_SQL)
        ensure_question_bank(conn)

        # Kaynak DB'yi bağla
        cur.execute("ATTACH DATABASE ? AS src", (f"file:{src}?mode=ro",))

        # Goals: kod üzerinden yükle, id'yi hedefte yeniden üret
        cur.execute("SELECT code, title_tr FROM src.sdg_goals")
        rows = cur.fetchall()
        for code, title in rows:
            cur.execute("INSERT OR IGNORE INTO sdg_goals(code, title_tr) VALUES(?, ?)", (code, title))

        # Goal kod → id haritası
        goal_map = {code: gid for (gid, code) in cur.execute("SELECT id, code FROM sdg_goals").fetchall()}

        # Targets: target kodundan goal kodunu türet, goal_id'yi hedefteki id ile eşleştir
        cur.execute("SELECT code, title_tr FROM src.sdg_targets")
        rows = cur.fetchall()
        for t_code, t_title in rows:
            try:
                g_code = int(str(t_code).split('.')[0])
            except Exception:
                g_code = None
            g_id = goal_map.get(g_code)
            if g_id:
                cur.execute(
                    "INSERT OR IGNORE INTO sdg_targets(goal_id, code, title_tr) VALUES(?, ?, ?)",
                    (g_id, t_code, t_title)
                )

        # Target kod → id haritası
        target_map = {code: tid for (tid, code) in cur.execute("SELECT id, code FROM sdg_targets").fetchall()}

        # Indicators: indicator kodundan target kodunu türet, target_id'yi hedefteki id ile eşleştir
        cur.execute("SELECT code, title_tr, unit, frequency, topic FROM src.sdg_indicators")
        rows = cur.fetchall()
        for i_code, i_title, unit, freq, topic in rows:
            # 11.5.3 → 11.5 ; 7.a.1 → 7.a
            parts = str(i_code).split('.')
            t_code = None
            if len(parts) >= 2:
                t_code = parts[0] + '.' + parts[1]
            t_id = target_map.get(t_code)
            if t_id:
                cur.execute(
                    "INSERT OR IGNORE INTO sdg_indicators(target_id, code, title_tr, unit, frequency, topic) VALUES(?, ?, ?, ?, ?, ?)",
                    (t_id, i_code, i_title, unit, freq or 'Yıllık', topic)
                )

        # Question bank doğrudan kopyalanabilir (indicator_code ile bağ kuruyor)
        cur.execute("INSERT INTO question_bank(indicator_code, q1, q2, q3, default_unit, default_frequency, default_owner, default_source) SELECT indicator_code, q1, q2, q3, default_unit, default_frequency, default_owner, default_source FROM src.question_bank")

        # Responses: indicator_id'yi kod üzerinden eşle
        # Önce responses tablosunu oluşturmak için schema.sql zaten çalıştı
        cur.execute(
            """
            INSERT INTO responses(company_id, indicator_id, period, answer_json, value_num, progress_pct, request_status, policy_flag, evidence_url, approved_by_owner, notes)
            SELECT r.company_id, si_dst.id AS indicator_id, r.period, r.answer_json, r.value_num, r.progress_pct, r.request_status, r.policy_flag, r.evidence_url, r.approved_by_owner, r.notes
            FROM src.responses r
            JOIN src.sdg_indicators si_src ON si_src.id = r.indicator_id
            JOIN sdg_indicators si_dst ON si_dst.code = si_src.code
            """
        )

        # Evidence: response_id'yi company_id + indicator_code + period üzerinden hedef responses.id ile eşle
        cur.execute(
            """
            INSERT INTO evidence(response_id, kind, url, description)
            SELECT r_dst.id AS response_id, e.kind, e.url, e.description
            FROM src.evidence e
            JOIN src.responses r_src ON r_src.id = e.response_id
            JOIN src.sdg_indicators si_src ON si_src.id = r_src.indicator_id
            JOIN sdg_indicators si_dst ON si_dst.code = si_src.code
            JOIN responses r_dst ON r_dst.company_id = r_src.company_id
                                 AND r_dst.indicator_id = si_dst.id
                                 AND r_dst.period = r_src.period
            """
        )

        try:
            cur.execute("DETACH DATABASE src")
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
        conn.commit()
        logging.info('SDG tabloları başarıyla senkronize edildi.')
    except Exception as e:
        conn.rollback()
        logging.error('Hata:', e)
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
