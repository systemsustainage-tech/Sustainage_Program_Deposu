#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI doküman tarayıcı
- docs/gri ve sdg/gri/standarts klasörlerindeki PDF/DOCX dosyalarını tarar
- GRI standart kodlarını (örn. "GRI 302") dosya adından/klasör adından çıkarır
- Envanter ve olası eksikleri raporlar
"""

import logging
import os
import re
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def find_gri_codes_in_name(name: str) -> None:
    """Dosya/klasör adından olası GRI kod(lar)ını çıkarır."""
    patterns = [
        r"\bGRI\s*(\d{1,3})\b",       # GRI 302
        r"\bGRI-(\d{1,3})\b",          # GRI-302
        r"\bGRI_(\d{1,3})\b",          # GRI_302
    ]
    codes = set()
    for pat in patterns:
        for m in re.finditer(pat, name, flags=re.IGNORECASE):
            num = m.group(1)
            codes.add(f"GRI {num}")
    return sorted(codes)


def scan_dirs(paths) -> None:
    """Verilen dizinleri tarar ve GRI kod envanteri döner."""
    inventory = defaultdict(list)
    files_scanned = 0
    for p in paths:
        if not os.path.isabs(p):
            p = os.path.join(PROJECT_ROOT, p)
        if not os.path.isdir(p):
            continue
        for root, dirs, files in os.walk(p):
            # Klasör adında kod varsa işaretle
            folder_codes = find_gri_codes_in_name(os.path.basename(root))
            for fc in folder_codes:
                inventory[fc].append(root)
            # Dosyaları tara
            for fn in files:
                files_scanned += 1
                ext = os.path.splitext(fn)[1].lower()
                if ext not in ('.pdf', '.docx', '.doc'):
                    continue
                codes = find_gri_codes_in_name(fn)
                for code in codes:
                    inventory[code].append(os.path.join(root, fn))
    return inventory, files_scanned


def main() -> None:
    targets = [
        'docs/gri',
        'sdg/gri/standarts'
    ]
    inv, count = scan_dirs(targets)
    logging.info(f"Taranan dosya sayısı: {count}")
    found_codes = sorted(inv.keys(), key=lambda x: (int(x.split()[1]), x))
    logging.info(f"Bulunan GRI standart kodları: {len(found_codes)} adet")
    for code in found_codes:
        locs = inv[code]
        logging.info(f"- {code}: {len(locs)} dosya/klasör eşleşmesi")
        # İlk 5 yolu örnek olarak göster
        for path in locs[:5]:
            logging.info(f"  · {path}")

    # Olası eksikler: Universal (1,2,3) ve topic (201-419, 301-308, 302-306 vs.)
    expected = set([f"GRI {i}" for i in [1,2,3]])
    # Topic (201-208, 301-308, 401-419) ve 207, 306 gibi güncel sürümler
    expected.update([f"GRI {i}" for i in range(201, 209)])
    expected.update([f"GRI {i}" for i in range(301, 309)])
    expected.update([f"GRI {i}" for i in range(401, 420)])

    set(found_codes)
    missing = sorted(list(expected - set(found_codes)), key=lambda x: int(x.split()[1]))
    if missing:
        logging.info("\nBeklenen fakat dosyalarda bulunmayan GRI kodları:")
        logging.info(", ".join(missing))
    else:
        logging.info("\nBeklenen tüm temel GRI kodları dosyalarda yer alıyor.")


if __name__ == '__main__':
    main()
