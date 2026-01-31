#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basit Türkçe PDF Önizleme Testi
Türkçe karakterlerin (ÇĞİÖŞÜ çğıöşü) PDF'te doğru render edildiğini doğrular.
"""

import logging
import os

from raporlama.advanced_reporting_manager import AdvancedReportingManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    out_dir = os.path.join(os.getcwd(), 'data', 'test_reports')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'turkce_font_test.pdf')

    # Manager oluştur (DB kullanılmayacak, sadece PDF testi)
    mgr = AdvancedReportingManager(db_path=os.path.join('data', 'db', 'sdg.db'))

    report_data = {
        'template': {'name': 'Türkçe PDF Font Testi'},
        'company_info': {
            'name': 'Örnek Şirket A.Ş.',
            'sector': 'İmalat / Çelik Sanayi',
        },
        'reporting_period': '2024'
    }

    # Test paragrafı (Türkçe karakterler)
    report_data['content'] = (
        'Bu bir Türkçe font testi dokümanıdır. İçerik: ÇĞİÖŞÜ çğıöşü — '
        'Sürdürülebilirlik, yönetim ve çevresel performans göstergeleri. '
        'Adres: İstanbul, Türkiye. '
    )

    ok = mgr._create_pdf_report(report_data, out_path)
    logging.info(f"PDF oluşturma sonucu: {ok}, dosya: {out_path}")

if __name__ == '__main__':
    main()
