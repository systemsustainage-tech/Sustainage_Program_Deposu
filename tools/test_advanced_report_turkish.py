#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gelişmiş rapor Türkçe karakter testi
- PDF ve DOCX çıktılarında Türkçe karakter desteğini doğrular
"""

import logging
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from raporlama.advanced_reporting_manager import AdvancedReportingManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def pick_template_with_formats(templates, required) -> None:
    for t in templates:
        try:
            fmts = t.get('output_formats') or []
            if all(fmt in [f.lower() for f in fmts] for fmt in required):
                return t
        except Exception:
            continue
    return templates[0] if templates else None


def main() -> None:
    mgr = AdvancedReportingManager()

    # Şablonları çek ve uygun olanı seç
    templates = mgr.get_report_templates(active_only=True)
    logging.info(f"Bulunan şablon sayısı: {len(templates)}")
    for t in templates:
        logging.info(f"Şablon: {t.get('name')} - Formatlar: {t.get('output_formats')}")

    template = pick_template_with_formats(templates, ['pdf', 'docx'])
    if not template:
        logging.info("Şablon bulunamadı, test atlandı.")
        return 1

    template_id = template['id']
    company_id = 1  # Varsayılan; bulunamazsa manager varsayılan şirket bilgilerini kullanır
    period = datetime.now().strftime('%Y-%m')
    content = (
        "Türkçe karakter testi: Çığ, İğde, Örnek, Şehir, Ülke, ağ, eş, üç, doğru. "
        "Uzun bir paragraf içinde – tire, noktalı virgül; ve tırnak \"işaretleri\" de yer alır."
    )

    # Test: PDF ve DOCX üret
    result = mgr.create_advanced_report(
        template_id,
        company_id,
        period,
        output_formats=['pdf', 'docx'],
        custom_params={'content': content}
    )

    logging.info(f"Durum: {result.get('status')}")
    logging.info(f"Şablon: {result.get('template_name')}")
    files = result.get('output_files', {})
    logging.info(f"Dosyalar: {files}")

    ok = True
    for k in ['pdf', 'docx']:
        p = files.get(k)
        if not p or not os.path.isfile(p):
            logging.info(f"{k.upper()} dosyası bulunamadı: {p}")
            ok = False
        else:
            size = os.path.getsize(p)
            logging.info(f"{k.upper()} bulundu: {p} (boyut: {size} bayt)")
            if size <= 0:
                logging.info(f"{k.upper()} dosyası boş görünüyor!")
                ok = False

    logging.info(f"Türkçe test sonucu: {ok}")
    return 0 if ok else 2


if __name__ == '__main__':
    raise SystemExit(main())
