#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Göstergelerini Resmî 232 Listeye Hizalama

- Kaynak: data/imports/generated/sdg_16_169_232/sdg_indicators.csv (Excel'den üretilen)
- Varyantları (ör. 16.7.1a, 3.3.2(b)) kanonik kök koda indirger: 16.7.1, 3.3.2
- Aynı kök koda sahip gösterge kayıtlarını tekilleştirir:
  * responses.indicator_id değerlerini kanonik gösterge id’sine taşır
  * duplikat sdg_indicators satırlarını siler
- Gösterge-target tutarlılığı: code → target_code eşlemesine göre target_id düzeltir

Kullanım:
  python tools/align_to_official_232.py --db data/sdg_desktop.sqlite --apply
Opsiyonel:
  --canonical_csv data/imports/generated/sdg_16_169_232/sdg_indicators.csv
"""

import logging
import argparse
import csv
import os
import re
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def normalize_indicator_code(code: str) -> str:
    """Kanonikleştirme: g.t.iX → g.t.i (üçüncü segmentteki harf/parenleri temizler).
    Örn: 16.7.1a → 16.7.1, 3.3.2(b) → 3.3.2. İkinci segmentteki harfler (a,b) hedef kodunun parçasıdır ve korunur.
    """
    code = (code or "").strip()
    parts = code.split('.')
    if len(parts) != 3:
        return code
    g, t, i = parts[0], parts[1], parts[2]
    # üçüncü segmentten parantez ve harfleri kaldır
    i = re.sub(r"[^0-9]", "", i)
    return f"{g}.{t}.{i}" if i else f"{g}.{t}"


def load_allowed_set_from_csv(csv_path: str) -> set:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Kanonik CSV bulunamadı: {csv_path}")
    allowed = set()
    with open(csv_path, newline='', encoding='utf-8') as f:
        rd = csv.reader(f)
        next(rd, None)
        # Beklenen header: sdg_no,target_code,indicator_code,title_tr,unit,frequency,topic
        for row in rd:
            if not row or len(row) < 3:
                continue
            indicator_code = row[2].strip()
            allowed.add(indicator_code)
    return allowed


def get_target_id_by_code(cur, target_code: str) -> None:
    cur.execute("SELECT id FROM sdg_targets WHERE code=?", (target_code,))
    r = cur.fetchone()
    return r[0] if r else None


def ensure_indicator_target_consistency(cur) -> None:
    rows = cur.execute("SELECT i.id, i.code, t.code FROM sdg_indicators i JOIN sdg_targets t ON i.target_id=t.id").fetchall()
    fixes = 0
    for iid, icode, tcode in rows:
        # hedef kodu: code'in ilk iki segmenti
        parts = icode.split('.')
        if len(parts) < 2:
            continue
        desired_t = f"{parts[0]}.{parts[1]}"
        if desired_t != tcode:
            new_tid = get_target_id_by_code(cur, desired_t)
            if new_tid:
                # UNIQUE(target_id,code) çakışmaları için korumalı taşıma
                existing = cur.execute("SELECT id FROM sdg_indicators WHERE target_id=? AND code=?", (new_tid, icode)).fetchone()
                if existing and existing[0] != iid:
                    # responses taşı → eski kayıt sil
                    cur.execute("UPDATE responses SET indicator_id=? WHERE indicator_id=?", (existing[0], iid))
                    cur.execute("DELETE FROM sdg_indicators WHERE id=?", (iid,))
                else:
                    cur.execute("UPDATE sdg_indicators SET target_id=? WHERE id=?", (new_tid, iid))
                fixes += 1
    return fixes


def align_indicators(cur, allowed_set: set, apply: bool) -> None:
    rows = cur.execute("SELECT id, target_id, code FROM sdg_indicators").fetchall()
    by_norm = {}
    for iid, tid, code in rows:
        norm = normalize_indicator_code(code)
        by_norm.setdefault(norm, []).append((iid, tid, code))

    moved_responses = 0
    deleted = 0
    renamed = 0
    for norm_code, items in by_norm.items():
        if norm_code not in allowed_set:
            # Beklenmeyen kod grubu: genelde olmamalı. Tedbiren atla.
            continue
        # Kanonik kayıt: norm koda eşit code varsa onu seç; yoksa en küçük id
        canonical = None
        for (iid, _tid, code) in items:
            if code == norm_code:
                canonical = iid
                break
        if canonical is None:
            canonical = min(items, key=lambda x: x[0])[0]
        # Diğerlerini kanoniğe taşı → sil
        for (iid, _tid, code) in items:
            if iid == canonical:
                continue
            if apply:
                cur.execute("UPDATE responses SET indicator_id=? WHERE indicator_id=?", (canonical, iid))
                cur.execute("DELETE FROM sdg_indicators WHERE id=?", (iid,))
                moved_responses += cur.rowcount  # approx
                deleted += 1
        # Kanonik kaydın kodunu norm_code’a ayarla
        # Çakışma kontrolü
        if apply:
            existing = cur.execute("SELECT id FROM sdg_indicators WHERE id<>? AND code=?", (canonical, norm_code)).fetchone()
            if existing:
                # responses merge ve dup sil
                cur.execute("UPDATE responses SET indicator_id=? WHERE indicator_id=?", (canonical, existing[0]))
                cur.execute("DELETE FROM sdg_indicators WHERE id=?", (existing[0],))
                deleted += 1
            # Güncelle
            cur.execute("UPDATE sdg_indicators SET code=? WHERE id=?", (norm_code, canonical))
            renamed += 1

    # Önce, allowed_set dışındaki doğrudan kodları temizle (normalize eşleşmesi yoksa)
    if apply:
        disallowed = cur.execute("SELECT id, code FROM sdg_indicators WHERE code NOT IN (" + ",".join(["?"]*len(allowed_set)) + ")", tuple(allowed_set)).fetchall()
        for iid, code in disallowed:
            norm = normalize_indicator_code(code)
            if norm in allowed_set:
                # doğrudan güncelle: kodu kanoniğe çek
                cur.execute("UPDATE sdg_indicators SET code=? WHERE id=?", (norm, iid))
                renamed += 1
            else:
                # responses sil ve göstergeyi kaldır
                cur.execute("DELETE FROM responses WHERE indicator_id=?", (iid,))
                cur.execute("DELETE FROM sdg_indicators WHERE id=?", (iid,))
                deleted += 1

    # Gösterge-target tutarlılığı
    fixes = ensure_indicator_target_consistency(cur) if apply else 0
    return {
        'groups': len(by_norm),
        'moved_responses': moved_responses,
        'deleted_indicators': deleted,
        'renamed_indicators': renamed,
        'target_link_fixes': fixes,
    }


def get_counts(cur) -> None:
    def c(sql) -> None:
        return cur.execute(sql).fetchone()[0]
    return {
        'goals': c("SELECT COUNT(*) FROM sdg_goals"),
        'targets': c("SELECT COUNT(*) FROM sdg_targets"),
        'indicators': c("SELECT COUNT(*) FROM sdg_indicators"),
        'distinct_target_codes': c("SELECT COUNT(DISTINCT code) FROM sdg_targets"),
        'distinct_indicator_codes': c("SELECT COUNT(DISTINCT code) FROM sdg_indicators"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--canonical_csv", default=os.path.join("data","imports","generated","sdg_16_169_232","sdg_indicators.csv"))
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    con = sqlite3.connect(args.db)
    cur = con.cursor()

    logging.info("Başlangıç sayımları:", get_counts(cur))
    allowed = load_allowed_set_from_csv(args.canonical_csv)
    logging.info(f"Kanonik liste boyutu: {len(allowed)} (beklenen: 232)")

    res = align_indicators(cur, allowed, apply=args.apply)
    logging.info("Hizalama özeti:", res)

    if args.apply:
        con.commit()
        logging.info("Değişiklikler uygulandı.")
    else:
        logging.info("Dry-run: değişiklik uygulanmadı.")

    logging.info("Son sayımlar:", get_counts(cur))

if __name__ == "__main__":
    main()
