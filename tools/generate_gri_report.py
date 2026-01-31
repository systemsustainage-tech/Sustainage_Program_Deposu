#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Rapor üretim aracı (CLI)
Kullanım:
  python tools/generate_gri_report.py --company 1 --format PDF --out reports/gri_report.pdf [--period 2025]
"""

import logging
import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from modules.gri.gri_reporting import GRIReporting

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    ap = argparse.ArgumentParser(description='GRI rapor üretimi')
    ap.add_argument('--company', type=int, required=True, help='Şirket ID')
    ap.add_argument('--format', type=str, choices=['PDF','DOCX'], default='PDF', help='Çıktı formatı')
    ap.add_argument('--out', type=str, required=True, help='Çıktı dosya yolu')
    ap.add_argument('--period', type=str, default=None, help='Rapor dönemi (örn. 2025)')
    args = ap.parse_args()

    rep = GRIReporting()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    if args.format == 'PDF':
        ok = rep.create_pdf_report(args.company, args.out, period=args.period)
    else:
        ok = rep.create_docx_report(args.company, args.out, period=args.period)

    if not ok:
        logging.info('Rapor oluşturulamadı', file=sys.stderr)
        sys.exit(1)
    logging.info(f"Rapor oluşturuldu: {args.out}")


if __name__ == '__main__':
    main()
