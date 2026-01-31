#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import argparse
import json
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SAMPLES = [
    {"code": "7.2.1", "value_num": 35.0, "progress_pct": 60, "request_status": "Cevaplandı", "policy_flag": "Evet"},
    {"code": "12.5.1", "value_num": 45.0, "progress_pct": 50, "request_status": "İncelemede", "policy_flag": "Hayır"},
    {"code": "8.5.1", "value_num": 90.0, "progress_pct": 80, "request_status": "Gönderildi", "policy_flag": "Evet"},
    {"code": "11.6.2", "value_num": 12.0, "progress_pct": 40, "request_status": "Cevaplandı", "policy_flag": "Hayır"},
    {"code": "6.4.1", "value_num": 70.0, "progress_pct": 55, "request_status": "İncelemede", "policy_flag": "Evet"}
]

def ensure_company(cur, company_id) -> None:
    r = cur.execute("SELECT id FROM companies WHERE id=?", (company_id,)).fetchone()
    if not r:
        cur.execute("INSERT INTO companies(id, name, sector, country) VALUES (?,?,?,?)",
                    (company_id, f"Şirket {company_id}", "Genel", "TR"))

def get_indicator_id(cur, code) -> None:
    r = cur.execute("SELECT id FROM sdg_indicators WHERE code=?", (code,)).fetchone()
    return r[0] if r else None

def upsert_response(cur, company_id, indicator_id, period, payload) -> None:
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
        (company_id, indicator_id, period,
         json.dumps({"q1":"örnek","q2":"örnek","q3":"örnek"}, ensure_ascii=False),
         payload.get("value_num"), payload.get("progress_pct"),
         payload.get("request_status"), payload.get("policy_flag"),
         f"Örnek veri ({payload.get('code')})")
    )

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--company_id", type=int, default=1)
    ap.add_argument("--period", default="2024")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    cur = con.cursor()

    ensure_company(cur, args.company_id)
    inserted = 0
    for s in SAMPLES:
        iid = get_indicator_id(cur, s["code"]) 
        if not iid:
            continue
        upsert_response(cur, args.company_id, iid, args.period, s)
        inserted += 1

    con.commit()
    logging.info(f"Eklenen/güncellenen örnek cevap sayısı: {inserted}")

if __name__ == "__main__":
    main()
