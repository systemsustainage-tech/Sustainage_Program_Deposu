#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Tutarlılık ve Senkronizasyon Kontrolü

Kontroller:
- Hedef/Alt Hedef/Gösterge sayımları
- Gösterge kod örüntüsü ve target eşleşmesi (örn. 11.5.3 → target 11.5)
- map_sdg_gri / map_sdg_tsrs referanslarının sdg_indicators ile uyumu
- responses.indicator_id referanslarının mevcut göstergelere bağlılığı
- Belirli kodların varlığı (örn. 11.5.3)

Kullanım:
  python tools/check_sdg_consistency.py --db data/sdg_desktop.sqlite
"""

import logging
import argparse
import os
import re
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def fetch_one(cur, sql, params=()) -> None:
    cur.execute(sql, params)
    row = cur.fetchone()
    return row[0] if row and row[0] is not None else 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True, help='SQLite veritabanı yolu')
    args = ap.parse_args()

    db = os.path.abspath(args.db)
    if not os.path.exists(db):
        logging.info('Veritabanı bulunamadı:', db)
        return

    conn = sqlite3.connect(db)
    cur = conn.cursor()

    logging.info('=== SDG TUTARLILIK KONTROLÜ ===')
    logging.info('DB:', db)

    # Sayımlar
    goals = fetch_one(cur, 'SELECT COUNT(*) FROM sdg_goals')
    targets = fetch_one(cur, 'SELECT COUNT(*) FROM sdg_targets')
    indicators = fetch_one(cur, 'SELECT COUNT(*) FROM sdg_indicators')
    logging.info(f'Goals: {goals}, Targets: {targets}, Indicators: {indicators}')

    # Belirli kodlar
    has_1153 = fetch_one(cur, "SELECT COUNT(*) FROM sdg_indicators WHERE code='11.5.3'")
    logging.info('11.5.3 mevcut mu?:', 'EVET' if has_1153 else 'HAYIR')

    # Gösterge → target eşleşmesi kontrolü (örüntüden hedef kodu çıkar)
    mismatches = []
    for (code, target_id) in cur.execute('SELECT code, target_id FROM sdg_indicators').fetchall():
        # hedef kodunu tahmin et: 11.5.3 → 11.5 ; 7.a.1 → 7.a
        m = re.match(r'^(\d+\.[0-9a-z]+)\.', code)
        if not m:
            # Bazı kodlar 17.18.1 gibi; yukarıdaki örüntü yeterli
            m = re.match(r'^(\d+\.[0-9a-z]+)$', code)
        expected_target_code = m.group(1) if m else None
        if not expected_target_code:
            mismatches.append((code, 'Örüntü bulunamadı'))
            continue
        row = cur.execute('SELECT code FROM sdg_targets WHERE id=?', (target_id,)).fetchone()
        actual_target_code = row[0] if row else None
        if actual_target_code != expected_target_code:
            mismatches.append((code, f'beklenen={expected_target_code}, mevcut={actual_target_code}'))

    logging.error('Target eşleşme hataları:', len(mismatches))
    if mismatches:
        logging.info('Örnekler (ilk 10):')
        for i, (code, msg) in enumerate(mismatches[:10], 1):
            logging.info(f'  {i}. {code}: {msg}')

    # Mapping referans kontrolleri
    def count_invalid_map(table, code_col) -> None:
        sql = f"""
            SELECT COUNT(*)
            FROM {table} m
            LEFT JOIN sdg_indicators si ON si.code = m.{code_col}
            WHERE si.id IS NULL
        """
        return fetch_one(cur, sql)

    invalid_sdg_gri = count_invalid_map('map_sdg_gri', 'sdg_indicator_code')
    invalid_sdg_tsrs = count_invalid_map('map_sdg_tsrs', 'sdg_indicator_code')
    logging.error('Haritalama referans hataları → sdg_gri:', invalid_sdg_gri, ', sdg_tsrs:', invalid_sdg_tsrs)

    # Responses referansları
    invalid_responses = fetch_one(cur, """
        SELECT COUNT(*) FROM responses r
        LEFT JOIN sdg_indicators si ON si.id = r.indicator_id
        WHERE r.indicator_id IS NOT NULL AND si.id IS NULL
    """)
    logging.error('Responses referans hataları (indicator_id yok):', invalid_responses)

    conn.close()
    logging.info('Kontrol tamamlandı.')


if __name__ == '__main__':
    main()
