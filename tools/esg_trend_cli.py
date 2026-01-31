import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESG Trend ve Risk CLI özeti.

Kullanım:
  python tools/esg_trend_cli.py --db data/sdg_desktop.sqlite --company 1
  python tools/esg_trend_cli.py --company 1 --period 2023
"""

import argparse
import json
import os
import sqlite3
from typing import Dict, List, Set, Tuple
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_config(base_dir: str) -> Dict:
    with open(os.path.join(base_dir, 'config', 'esg_config.json'), 'r', encoding='utf-8') as f:
        return json.load(f)


def connect(db_path: str) -> None:
    return sqlite3.connect(db_path)


def discover_periods(conn) -> Set[str]:
    cur = conn.cursor()
    periods: Set[str] = set()
    try:
        cur.execute("SELECT DISTINCT period FROM gri_responses WHERE period IS NOT NULL")
        periods |= {row[0] for row in cur.fetchall() if row[0]}
    except Exception as e:
        logging.error(f"Silent error caught: {str(e)}")
    try:
        cur.execute("SELECT DISTINCT reporting_period FROM tsrs_responses WHERE reporting_period IS NOT NULL")
        periods |= {row[0] for row in cur.fetchall() if row[0]}
    except Exception as e:
        logging.error(f"Silent error caught: {str(e)}")
    if not periods:
        periods.add('GENEL')
    return periods


def count_gris(conn, pillar_cfg: Dict, company_id: int, period: str = None) -> Tuple[int,int]:
    cur = conn.cursor()
    cur.execute("CREATE TEMP TABLE IF NOT EXISTS tmp_gri_cat(val TEXT)")
    cur.execute("DELETE FROM tmp_gri_cat")
    cur.execute("CREATE TEMP TABLE IF NOT EXISTS tmp_gri_std(val TEXT)")
    cur.execute("DELETE FROM tmp_gri_std")
    cats = pillar_cfg.get('gri_categories') or []
    stds = pillar_cfg.get('gri_standards') or []
    if cats:
        cur.executemany("INSERT INTO tmp_gri_cat(val) VALUES (?)", [(c,) for c in cats])
    if stds:
        cur.executemany("INSERT INTO tmp_gri_std(val) VALUES (?)", [(s,) for s in stds])

    q_total = (
        "SELECT COUNT(*) FROM gri_indicators i "
        "JOIN gri_standards s ON i.standard_id=s.id "
        "WHERE 1=1 "
        + (" AND s.category IN (SELECT val FROM tmp_gri_cat)" if cats else "")
        + (" AND s.code IN (SELECT val FROM tmp_gri_std)" if stds else "")
    )
    params_ans: List = [company_id]
    q_ans = (
        "SELECT COUNT(*) FROM gri_responses r "
        "JOIN gri_indicators i ON r.indicator_id=i.id "
        "JOIN gri_standards s ON i.standard_id=s.id "
        "WHERE r.response_value IS NOT NULL AND r.company_id = ? "
        + (" AND s.category IN (SELECT val FROM tmp_gri_cat)" if cats else "")
        + (" AND s.code IN (SELECT val FROM tmp_gri_std)" if stds else "")
    )
    if period and period != 'GENEL':
        q_ans += " AND r.period = ?"
        params_ans.append(period)

    try:
        cur.execute(q_total)
        total = cur.fetchone()[0] or 0
    except Exception:
        total = 0
    try:
        cur.execute(q_ans, params_ans)
        answered = cur.fetchone()[0] or 0
    except Exception:
        answered = 0
    return total, answered


def count_tsrs(conn, pillar_cfg: Dict, company_id: int, period: str = None) -> Tuple[int,int]:
    cur = conn.cursor()
    cur.execute("CREATE TEMP TABLE IF NOT EXISTS tmp_tsrs_sec(val TEXT)")
    cur.execute("DELETE FROM tmp_tsrs_sec")
    secs = pillar_cfg.get('tsrs_sections') or []
    if secs:
        cur.executemany("INSERT INTO tmp_tsrs_sec(val) VALUES (?)", [(s,) for s in secs])

    q_total = (
        "SELECT COUNT(*) FROM tsrs_indicators i "
        "JOIN tsrs_standards s ON i.standard_id=s.id "
        "WHERE 1=1 "
        + (" AND s.code IN (SELECT val FROM tmp_tsrs_sec)" if secs else "")
    )
    params_ans: List = [company_id]
    q_ans = (
        "SELECT COUNT(*) FROM tsrs_responses r "
        "JOIN tsrs_indicators i ON r.indicator_id=i.id "
        "JOIN tsrs_standards s ON i.standard_id=s.id "
        "WHERE r.response_value IS NOT NULL AND r.company_id = ? "
        + (" AND s.code IN (SELECT val FROM tmp_tsrs_sec)" if secs else "")
    )
    if period and period != 'GENEL':
        q_ans += " AND r.reporting_period = ?"
        params_ans.append(period)

    try:
        cur.execute(q_total)
        total = cur.fetchone()[0] or 0
    except Exception:
        total = 0
    try:
        cur.execute(q_ans, params_ans)
        answered = cur.fetchone()[0] or 0
    except Exception:
        answered = 0
    return total, answered


def apply_bonuses(conn, cfg: Dict, company_id: int) -> Tuple[float, float]:
    # ESGManager’daki bonus mantığının basit karşılığı
    evidence_bonus = cfg.get('scoring', {}).get('evidence_bonus', 0.05)
    materiality_bonus_cfg = cfg.get('scoring', {}).get('materiality_bonus', 0.1)
    bonus_evidence = 0.0
    bonus_materiality = 0.0
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM sdg_question_responses WHERE company_id=? AND (answer_text IS NOT NULL OR answer_value IS NOT NULL)", (company_id,))
        if (cur.fetchone()[0] or 0) > 0:
            bonus_evidence = evidence_bonus
    except Exception as e:
        logging.error(f"Silent error caught: {str(e)}")
    try:
        cur.execute("SELECT COUNT(*) FROM tsrs_materiality_assessment WHERE company_id=? AND is_material=1", (company_id,))
        if (cur.fetchone()[0] or 0) > 0:
            bonus_materiality = materiality_bonus_cfg
    except Exception as e:
        logging.error(f"Silent error caught: {str(e)}")
    return bonus_evidence, bonus_materiality


def compute_period_scores(conn, cfg: Dict, company_id: int, period: str) -> Dict:
    mappings = cfg.get('mappings', {})
    # GRI+TSRS oranları
    e_tot_gri, e_ans_gri = count_gris(conn, mappings.get('E', {}), company_id, period)
    e_tot_tsrs, e_ans_tsrs = count_tsrs(conn, mappings.get('E', {}), company_id, period)
    s_tot_gri, s_ans_gri = count_gris(conn, mappings.get('S', {}), company_id, period)
    s_tot_tsrs, s_ans_tsrs = count_tsrs(conn, mappings.get('S', {}), company_id, period)
    g_tot_gri, g_ans_gri = count_gris(conn, mappings.get('G', {}), company_id, period)
    g_tot_tsrs, g_ans_tsrs = count_tsrs(conn, mappings.get('G', {}), company_id, period)

    def ratio(a: int, t: int) -> float:
        return float(a) / float(t) if t > 0 else 0.0

    e_ratio = ratio(e_ans_gri + e_ans_tsrs, e_tot_gri + e_tot_tsrs)
    s_ratio = ratio(s_ans_gri + s_ans_tsrs, s_tot_gri + s_tot_tsrs)
    g_ratio = ratio(g_ans_gri + g_ans_tsrs, g_tot_gri + g_tot_tsrs)

    ev_bonus, mat_bonus = apply_bonuses(conn, cfg, company_id)
    E = min(e_ratio + ev_bonus, 1.0)
    S = min(s_ratio + ev_bonus, 1.0)
    G = min(g_ratio + mat_bonus, 1.0)

    w = cfg.get('weights', {'E':0.4,'S':0.3,'G':0.3})
    overall = E*w['E'] + S*w['S'] + G*w['G']
    return {
        'period': period,
        'E': round(E*100,1), 'S': round(S*100,1), 'G': round(G*100,1), 'overall': round(overall*100,1)
    }


def classify_risk(overall: float, E: float, S: float, G: float) -> str:
    low = (E >= 70 and S >= 70 and G >= 70 and overall >= 70)
    high = (E < 50 or S < 50 or G < 50 or overall < 50)
    if high:
        return 'Yüksek Risk'
    if low:
        return 'Düşük Risk'
    return 'Orta Risk'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=DB_PATH)
    ap.add_argument('--company', type=int, default=1)
    ap.add_argument('--period')
    args = ap.parse_args()

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    cfg = load_config(base_dir)
    conn = connect(args.db)

    try:
        periods = {args.period} if args.period else discover_periods(conn)
        results: List[Dict] = []
        for p in sorted(periods):
            results.append(compute_period_scores(conn, cfg, args.company, p))
        logging.info("Periyot, E, S, G, Genel, Risk")
        for r in results:
            risk = classify_risk(r['overall'], r['E'], r['S'], r['G'])
            logging.info(f"{r['period']}, {r['E']}%, {r['S']}%, {r['G']}%, {r['overall']}%, {risk}")
    finally:
        conn.close()


if __name__ == '__main__':
    main()
