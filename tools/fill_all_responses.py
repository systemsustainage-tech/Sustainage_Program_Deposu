#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tüm SDG göstergeleri için örnek yanıt doldurma
Kullanım:
  python tools/fill_all_responses.py --db data/sdg_desktop.sqlite --company_id 1 --period 2024 --limit 0

Notlar:
- Var olan yanıtlar ON CONFLICT ile güncellenir.
- limit=0 veya belirtilmezse tüm göstergeler için veri ekler.
"""
import logging
import argparse
import json
import random
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

STATUSES = ["Gönderildi", "İncelemede", "Cevaplandı"]

def ensure_company(cur, company_id: int) -> None:
    r = cur.execute("SELECT id FROM companies WHERE id=?", (company_id,)).fetchone()
    if not r:
        cur.execute(
            "INSERT INTO companies(id, name, sector, country) VALUES (?,?,?,?)",
            (company_id, f"Örnek Şirket {company_id}", "Genel", "Türkiye")
        )

def list_indicators(cur, limit: int = 0) -> None:
    q = "SELECT id, code FROM sdg_indicators ORDER BY id"
    rows = cur.execute(q).fetchall()
    if limit and limit > 0:
        rows = rows[:limit]
    return rows

def upsert_response(cur, company_id: int, indicator_id: int, period: str, code: str) -> None:
    value_num = round(random.uniform(5.0, 100.0), 2)
    progress_pct = random.randint(35, 90)
    status = random.choice(STATUSES)
    policy_flag = random.choice(["Evet", "Hayır"])
    answer = {
        "soru_1": f"{code} için ölçüm açıklaması",
        "soru_2": "Metodoloji: örnek veri",
        "soru_3": "Kanıt: iç politika dokümanı"
    }
    cur.execute(
        """
        INSERT INTO responses(company_id, indicator_id, period, answer_json, value_num,
                              progress_pct, request_status, policy_flag, notes)
        VALUES (?,?,?,?,?,?,?,?,?)
        ON CONFLICT(company_id, indicator_id, period) DO UPDATE SET
          answer_json=excluded.answer_json,
          value_num=excluded.value_num,
          progress_pct=excluded.progress_pct,
          request_status=excluded.request_status,
          policy_flag=excluded.policy_flag,
          notes=excluded.notes
        """,
        (
            company_id,
            indicator_id,
            period,
            json.dumps(answer, ensure_ascii=False),
            value_num,
            progress_pct,
            status,
            policy_flag,
            f"Otomatik örnek veri ({code})"
        )
    )

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--company_id", type=int, default=1)
    ap.add_argument("--period", default="2024")
    ap.add_argument("--limit", type=int, default=0, help="Kaç gösterge için veri eklenecek (0=tümü)")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    cur = con.cursor()

    ensure_company(cur, args.company_id)
    inds = list_indicators(cur, args.limit)
    cnt = 0
    for iid, code in inds:
        upsert_response(cur, args.company_id, iid, args.period, code)
        cnt += 1

    con.commit()
    con.close()
    logging.info(f"Eklenen/güncellenen örnek yanıt sayısı: {cnt}")

if __name__ == "__main__":
    main()
