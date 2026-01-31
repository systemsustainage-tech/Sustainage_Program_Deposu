#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG veri doğrulama ve temizlik aracı

Amaçlar:
- sdg_targets kodlarına göre doğru goal_id atansın (örn. 12.2 → goal_id=SDG 12)
- Aynı target code'a sahip kopya kayıtlar tekilleştirilsin
- sdg_indicators kodlarına göre doğru target_id atansın (örn. 12.2.1 → target 12.2)
- Aynı indicator code'a sahip kopya kayıtlar tekilleştirilsin
- responses tablosundaki indicator_id referansları, tekilleştirme sonrası canonical id'ye taşınsın

Kullanım:
python tools/validate_and_cleanup_sdg.py --db data/sdg_desktop.sqlite --dry-run
python tools/validate_and_cleanup_sdg.py --db data/sdg_desktop.sqlite --apply
"""

import logging
import argparse
import sqlite3
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetchall(cur, sql, params=None) -> None:
    cur.execute(sql, params or ())
    return cur.fetchall()


def get_goal_map(cur) -> None:
    rows = fetchall(cur, "SELECT id, code FROM sdg_goals")
    return {code: gid for gid, code in rows}


def ensure_target_goal_links(cur, goal_map, apply=False) -> None:
    rows = fetchall(cur, "SELECT id, goal_id, code FROM sdg_targets")
    fixes = []
    for tid, goal_id, code in rows:
        try:
            goal_code = int(str(code).split('.')[0])
        except Exception:
            continue
        expected_gid = goal_map.get(goal_code)
        if expected_gid and expected_gid != goal_id:
            fixes.append((tid, goal_id, expected_gid, code))
    if apply:
        for tid, old_gid, new_gid, code in fixes:
            cur.execute("UPDATE sdg_targets SET goal_id=? WHERE id=?", (new_gid, tid))
    return fixes


def dedupe_targets(cur, goal_map, apply=False) -> None:
    # Canonical id: tercih edilen, expected goal_id'ye sahip kayıt; yoksa minimum id
    rows = fetchall(cur, "SELECT id, goal_id, code FROM sdg_targets ORDER BY code, id")
    by_code = defaultdict(list)
    for r in rows:
        by_code[r[2]].append(r)

    reassign = []  # (from_tid, to_tid)
    to_delete = []
    for code, items in by_code.items():
        if len(items) <= 1:
            continue
        try:
            goal_code = int(str(code).split('.')[0])
        except Exception:
            goal_code = None
        expected_gid = goal_map.get(goal_code) if goal_code is not None else None

        # tercih edilen canonical: expected gid'e sahip
        canonical = None
        for (tid, gid, _c) in items:
            if expected_gid and gid == expected_gid:
                canonical = tid
                break
        if canonical is None:
            canonical = items[0][0]
        dups = [it[0] for it in items if it[0] != canonical]
        for dup_tid in dups:
            reassign.append((dup_tid, canonical))
            to_delete.append(dup_tid)

    if apply:
        # Indicators pointing to duplicate targets should be moved to canonical target
        for from_tid, to_tid in reassign:
            # Her bir göstergede çakışma kontrolü
            inds = fetchall(cur, "SELECT id, code FROM sdg_indicators WHERE target_id=?", (from_tid,))
            for iid, code in inds:
                # Canonical hedefte aynı koda sahip gösterge var mı?
                existing = fetchall(cur, "SELECT id FROM sdg_indicators WHERE target_id=? AND code=?", (to_tid, code))
                if existing:
                    canonical_iid = existing[0][0]
                    # responses'ı canonical iid'ye taşı ve dup'ı sil
                    cur.execute("UPDATE responses SET indicator_id=? WHERE indicator_id=?", (canonical_iid, iid))
                    cur.execute("DELETE FROM sdg_indicators WHERE id=?", (iid,))
                else:
                    # güvenle hedef id'yi güncelle
                    cur.execute("UPDATE sdg_indicators SET target_id=? WHERE id=?", (to_tid, iid))
        # Now safe to delete duplicate targets
        for tid in to_delete:
            cur.execute("DELETE FROM sdg_targets WHERE id=?", (tid,))
    return reassign, to_delete


def ensure_indicator_target_links(cur, apply=False) -> None:
    # Map target code -> id
    tmap = {code: tid for tid, code in fetchall(cur, "SELECT id, code FROM sdg_targets")}
    rows = fetchall(cur, "SELECT id, target_id, code FROM sdg_indicators")
    fixes = []
    for iid, target_id, code in rows:
        parts = str(code).split('.')
        if len(parts) < 2:
            continue
        tcode = '.'.join(parts[:2])
        expected_tid = tmap.get(tcode)
        if expected_tid and expected_tid != target_id:
            fixes.append((iid, target_id, expected_tid, code))
    if apply:
        for iid, old_tid, new_tid, code in fixes:
            cur.execute("UPDATE sdg_indicators SET target_id=? WHERE id=?", (new_tid, iid))
    return fixes


def dedupe_indicators(cur, apply=False) -> None:
    # Canonical id: minimum id for each code
    rows = fetchall(cur, "SELECT id, target_id, code FROM sdg_indicators ORDER BY code, id")
    by_code = defaultdict(list)
    for r in rows:
        by_code[r[2]].append(r)

    reassign_resp = []  # (from_iid, to_iid)
    to_delete = []
    for code, items in by_code.items():
        if len(items) <= 1:
            continue
        canonical = items[0][0]
        dups = [it[0] for it in items[1:]]
        for dup_iid in dups:
            reassign_resp.append((dup_iid, canonical))
            to_delete.append(dup_iid)

    if apply:
        # Move responses to canonical indicator
        for from_iid, to_iid in reassign_resp:
            cur.execute("UPDATE responses SET indicator_id=? WHERE indicator_id=?", (to_iid, from_iid))
        # Delete duplicate indicators
        for iid in to_delete:
            cur.execute("DELETE FROM sdg_indicators WHERE id=?", (iid,))
    return reassign_resp, to_delete


def counts(cur) -> None:
    def cnt(sql) -> None:
        cur.execute(sql)
        return cur.fetchone()[0]
    return {
        'goals': cnt("SELECT COUNT(*) FROM sdg_goals"),
        'targets': cnt("SELECT COUNT(*) FROM sdg_targets"),
        'indicators': cnt("SELECT COUNT(*) FROM sdg_indicators"),
        'distinct_target_codes': cnt("SELECT COUNT(DISTINCT code) FROM sdg_targets"),
        'distinct_indicator_codes': cnt("SELECT COUNT(DISTINCT code) FROM sdg_indicators"),
        'orphan_targets': cnt("SELECT COUNT(*) FROM sdg_targets WHERE goal_id NOT IN (SELECT id FROM sdg_goals)"),
        'orphan_indicators': cnt("SELECT COUNT(*) FROM sdg_indicators WHERE target_id NOT IN (SELECT id FROM sdg_targets)")
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--apply", action="store_true", help="Değişiklikleri uygula")
    ap.add_argument("--dry-run", action="store_true", help="Sadece raporla, değişiklik yapma")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()
    conn.execute("PRAGMA foreign_keys = ON")

    logging.info("Başlangıç sayımları:")
    logging.info(counts(cur))

    goal_map = get_goal_map(cur)
    # Önce target tekilleştirme (expected goal_id'ye sahip canonical seç)
    reassign_t, del_t = dedupe_targets(cur, goal_map, apply=args.apply)
    logging.info(f"Target tekilleştirme: taşınan göstergeler {len(reassign_t)}, silinen hedefler {len(del_t)}")

    # Sonra hedef-goal bağlantı düzeltmeleri (tekilleştirme sonrası çakışma riski azalır)
    fixes_tg = ensure_target_goal_links(cur, goal_map, apply=args.apply)
    logging.info(f"Hedef-goal bağlantı düzeltmeleri: {len(fixes_tg)}")

    fixes_ind = ensure_indicator_target_links(cur, apply=args.apply)
    logging.info(f"Gösterge-target bağlantı düzeltmeleri: {len(fixes_ind)}")

    reassign_i, del_i = dedupe_indicators(cur, apply=args.apply)
    logging.info(f"Indicator tekilleştirme: taşınan yanıtlar {len(reassign_i)}, silinen göstergeler {len(del_i)}")

    if args.apply:
        conn.commit()
        logging.info("Değişiklikler uygulandı.")
    else:
        logging.info("Dry-run: değişiklik uygulanmadı.")

    logging.info("Son sayımlar:")
    logging.info(counts(cur))
    conn.close()


if __name__ == "__main__":
    main()
