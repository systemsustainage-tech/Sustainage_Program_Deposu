#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESG→SDG/GRI/TSRS eşleme görüntüleyici CLI.

Kullanım:
  python tools/esg_mapping_cli.py --db data/sdg_desktop.sqlite --company 1
  python tools/esg_mapping_cli.py --pillar E

Çıktı: Her sütun için GRI/TSRS eşlemeleri ve DB sayaçları.
"""

import logging
import argparse
import json
import os
import sqlite3
from typing import Dict, List
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(base_dir: str) -> Dict:
    cfg_path = os.path.join(base_dir, 'config', 'esg_config.json')
    with open(cfg_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def connect(db_path: str) -> None:
    return sqlite3.connect(db_path)


def count_gris(conn, pillar_cfg: Dict, company_id: int = None, period: str = None) -> None:
    cur = conn.cursor()
    where_total = []
    where_ans = []
    params_total: List = []
    params_ans: List = []

    # Toplam için standard kategori/kod filtresi
    if pillar_cfg.get('gri_categories'):
        where_total.append("s.category IN (%s)" % (",".join(['?'] * len(pillar_cfg['gri_categories']))))
        params_total += pillar_cfg['gri_categories']
        where_ans.append("s.category IN (%s)" % (",".join(['?'] * len(pillar_cfg['gri_categories']))))
        params_ans += pillar_cfg['gri_categories']
    if pillar_cfg.get('gri_standards'):
        where_total.append("s.code IN (%s)" % (",".join(['?'] * len(pillar_cfg['gri_standards']))))
        params_total += pillar_cfg['gri_standards']
        where_ans.append("s.code IN (%s)" % (",".join(['?'] * len(pillar_cfg['gri_standards']))))
        params_ans += pillar_cfg['gri_standards']

    # Cevaplar için şirket ve dönem filtresi
    where_ans.append("r.response_value IS NOT NULL")
    if company_id is not None:
        where_ans.append("r.company_id = ?")
        params_ans.append(company_id)
    if period:
        where_ans.append("r.period = ?")
        params_ans.append(period)

    q_total = "SELECT COUNT(*) FROM gri_indicators i JOIN gri_standards s ON i.standard_id=s.id"
    if where_total:
        q_total += " WHERE " + " AND ".join(where_total)

    q_ans = "SELECT COUNT(*) FROM gri_responses r JOIN gri_indicators i ON r.indicator_id=i.id JOIN gri_standards s ON i.standard_id=s.id WHERE " + " AND ".join(where_ans)

    try:
        cur.execute(q_total, params_total)
        total = cur.fetchone()[0] or 0
    except Exception:
        total = 0
    try:
        cur.execute(q_ans, params_ans)
        answered = cur.fetchone()[0] or 0
    except Exception:
        answered = 0
    return total, answered


def count_tsrs(conn, pillar_cfg: Dict, company_id: int = None, period: str = None) -> None:
    cur = conn.cursor()
    where_total = []
    where_ans = []
    params_total: List = []
    params_ans: List = []

    if pillar_cfg.get('tsrs_sections'):
        where_total.append("s.code IN (%s)" % (",".join(['?'] * len(pillar_cfg['tsrs_sections']))))
        params_total += pillar_cfg['tsrs_sections']
        where_ans.append("s.code IN (%s)" % (",".join(['?'] * len(pillar_cfg['tsrs_sections']))))
        params_ans += pillar_cfg['tsrs_sections']

    where_ans.append("r.response_value IS NOT NULL")
    if company_id is not None:
        where_ans.append("r.company_id = ?")
        params_ans.append(company_id)
    if period:
        where_ans.append("r.reporting_period = ?")
        params_ans.append(period)

    q_total = "SELECT COUNT(*) FROM tsrs_indicators i JOIN tsrs_standards s ON i.standard_id=s.id"
    if where_total:
        q_total += " WHERE " + " AND ".join(where_total)
    q_ans = "SELECT COUNT(*) FROM tsrs_responses r JOIN tsrs_indicators i ON r.indicator_id=i.id JOIN tsrs_standards s ON i.standard_id=s.id WHERE " + " AND ".join(where_ans)

    try:
        cur.execute(q_total, params_total)
        total = cur.fetchone()[0] or 0
    except Exception:
        total = 0
    try:
        cur.execute(q_ans, params_ans)
        answered = cur.fetchone()[0] or 0
    except Exception:
        answered = 0
    return total, answered


def count_sdg_hints(conn, goals_hint: List[int]) -> None:
    if not goals_hint:
        return 0
    cur = conn.cursor()
    q = (
        "SELECT COUNT(*) FROM sdg_indicators i "
        "JOIN sdg_targets t ON i.target_id=t.id "
        "JOIN sdg_goals g ON t.goal_id=g.id "
        "WHERE g.goal_number IN (%s)" % (",".join(['?'] * len(goals_hint)))
    )
    try:
        cur.execute(q, goals_hint)
        return cur.fetchone()[0] or 0
    except Exception:
        return 0


def show_pillar(conn, name: str, pillar_cfg: Dict, company_id: int = None, period: str = None) -> None:
    gri_tot, gri_ans = count_gris(conn, pillar_cfg, company_id, period)
    tsrs_tot, tsrs_ans = count_tsrs(conn, pillar_cfg, company_id, period)
    sdg_cnt = count_sdg_hints(conn, pillar_cfg.get('sdg_hint_goals', []))

    logging.info(f"\n[{name}]")
    logging.info("- GRI standards:", ", ".join(pillar_cfg.get('gri_standards', pillar_cfg.get('gri_categories', []))))
    logging.info("- TSRS sections:", ", ".join(pillar_cfg.get('tsrs_sections', [])))
    logging.info("- SDG hint goals:", ", ".join(map(str, pillar_cfg.get('sdg_hint_goals', []))))
    logging.info(f"- GRI answered/total: {gri_ans}/{gri_tot}")
    logging.info(f"- TSRS answered/total: {tsrs_ans}/{tsrs_tot}")
    logging.info(f"- SDG indicators in hint goals: {sdg_cnt}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=DB_PATH)
    ap.add_argument('--company', type=int, default=1)
    ap.add_argument('--pillar', choices=['E','S','G'])
    ap.add_argument('--period')
    args = ap.parse_args()

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    cfg = load_config(base_dir)
    conn = connect(args.db)

    try:
        mappings = cfg.get('mappings', {})
        if args.pillar:
            show_pillar(conn, args.pillar, mappings.get(args.pillar, {}), args.company, args.period)
        else:
            for p in ['E','S','G']:
                show_pillar(conn, p, mappings.get(p, {}), args.company, args.period)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
