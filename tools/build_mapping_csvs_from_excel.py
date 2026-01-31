#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG_232.xlsx → eşleştirme CSV’leri üretici
- MASTER_232 sayfasındaki 'Gösterge Kodu', 'GRI Bağlantısı', 'TSRS Bağlantısı'
  kolonlarını okuyarak şu CSV’leri üretir:
  - eslestirme/sdg_gri/real_sdg_gri.csv (sdg_indicator_code, gri_standard, gri_disclosure)
  - eslestirme/sdg_tsrs/real_sdg_tsrs.csv (sdg_indicator_code, tsrs_section, tsrs_metric)
  - eslestirme/gri_tsrs/real_gri_tsrs.csv (gri_standard, gri_disclosure, tsrs_section, tsrs_metric)

Kullanım:
  python tools/build_mapping_csvs_from_excel.py --excel c:\SDG\SDG_232.xlsx
"""

import logging
import csv
import os
import re
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ALIAS = {
    'indicator': ['Gösterge Kodu','Indicator Code','Kod','GÖSTERGE KODU'],
    'gri': ['GRI Bağlantısı','GRI Connection','GRI','GRI BAGLANTISI'],
    'tsrs': ['TSRS Bağlantısı','TSRS Connection','TSRS','TSRS BAGLANTISI'],
}

def norm(s: str) -> str:
    return (s or '').strip()

def split_multi_gri(text: str) -> None:
    if not text:
        return []
    parts = re.split(r'[;,/\n]+', str(text))
    return [p.strip() for p in parts if p and p.strip() and p.strip().lower() != 'nan']

def split_multi_tsrs(text: str) -> None:
    """TSRS metnini ayırırken parantez içindeki '/' işaretini koru.
    Bu yüzden sadece ';', ',', ve satır sonlarına göre bölüyoruz."""
    if not text:
        return []
    parts = re.split(r'[;,\n]+', str(text))
    return [p.strip() for p in parts if p and p.strip() and p.strip().lower() != 'nan']

def parse_gri_token(tok: str) -> None:
    """Heuristik GRI ayrıştırıcı: 'GRI 102', '205-3', 'GRI 206' vb."""
    t = tok.strip()
    t = re.sub(r'^GRI\s*', '', t, flags=re.IGNORECASE)
    m = re.match(r'^(\d+)(?:[\s-]*([\d\.]+))?$', t)
    if m:
        std = m.group(1)
        disc = m.group(2) or ''
        std_label = f"GRI {std}"
        # Eğer disclosure içinde nokta veya tire varsa tam kodu sakla, yoksa boş bırak
        disc_label = f"{std}-{disc}" if disc else ''
        return std_label, disc_label
    # metin ise standart yapısını koru
    return f"GRI {t}", ''

def parse_tsrs_token(tok: str) -> None:
    """Heuristik TSRS ayrıştırıcı: 'TSRS-1 (Yönetişim/Genel)' -> ('TSRS-1','Yönetişim/Genel')"""
    t = tok.strip()
    t = re.sub(r'^TSRS\s*-?', '', t, flags=re.IGNORECASE)
    # Numara + parantezli açıklama
    m = re.match(r'^(\d+)(?:\s*\(([^)]*)\))?$', t)
    if m:
        sec = m.group(1)
        met = m.group(2) or ''
        return f"TSRS-{sec}", met.strip()
    # Yalın metin ise bölüm ve metrik ayrımı yapamıyorsak tümünü metrik olarak verelim
    return t if t else '', ''

def find_column(df, names) -> None:
    cols = list(df.columns)
    for n in names:
        for c in cols:
            if str(c).strip().lower() == str(n).strip().lower():
                return c
    return None

def build_from_excel(excel_path: str) -> None:
    try:
        import pandas as pd
    except Exception as e:
        logging.info(f"Pandas yüklenemedi: {e}")
        sys.exit(1)

    if not os.path.exists(excel_path):
        logging.info(f"Excel bulunamadı: {excel_path}")
        sys.exit(1)

    df = pd.read_excel(excel_path, sheet_name='MASTER_232')

    col_indicator = find_column(df, ALIAS['indicator'])
    col_gri = find_column(df, ALIAS['gri'])
    col_tsrs = find_column(df, ALIAS['tsrs'])
    if not col_indicator:
        logging.info("'Gösterge Kodu' kolonu bulunamadı (ALIAS: Gösterge Kodu/Indicator Code).")
        sys.exit(1)
    if not col_gri and not col_tsrs:
        logging.info("GRI/TSRS kolonları bulunamadı. İşlenecek veri yok.")
        sys.exit(1)

    rows_sdg_gri = []
    rows_sdg_tsrs = []
    rows_gri_tsrs = set()

    for _, r in df.iterrows():
        ind = norm(str(r.get(col_indicator, '')))
        if not ind:
            continue
        gri_raw = str(r.get(col_gri, '')).strip() if col_gri else ''
        tsrs_raw = str(r.get(col_tsrs, '')).strip() if col_tsrs else ''

        gri_list = [parse_gri_token(t) for t in split_multi_gri(gri_raw)] if gri_raw else []
        tsrs_list = [parse_tsrs_token(t) for t in split_multi_tsrs(tsrs_raw)] if tsrs_raw else []

        for std, disc in gri_list:
            rows_sdg_gri.append([ind, std, disc])
        for sec, met in tsrs_list:
            # Eğer parse_tsrs_token yalın metin döndürdüyse, bölüm boş kalabilir
            if sec and met:
                rows_sdg_tsrs.append([ind, sec, met])
            elif sec and not met:
                rows_sdg_tsrs.append([ind, sec, ''])

        # GRI-TSRS çapraz eşleştirme (satır bazlı birlikte geçiyorsa bağ kur)
        for std, disc in gri_list:
            for sec, met in tsrs_list:
                rows_gri_tsrs.add((std, disc, sec, met))

    # Çıktı dosyaları
    out_sdg_gri = os.path.join('eslestirme', 'sdg_gri', 'real_sdg_gri.csv')
    out_sdg_tsrs = os.path.join('eslestirme', 'sdg_tsrs', 'real_sdg_tsrs.csv')
    out_gri_tsrs = os.path.join('eslestirme', 'gri_tsrs', 'real_gri_tsrs.csv')
    os.makedirs(os.path.dirname(out_sdg_gri), exist_ok=True)
    os.makedirs(os.path.dirname(out_sdg_tsrs), exist_ok=True)
    os.makedirs(os.path.dirname(out_gri_tsrs), exist_ok=True)

    # Yaz
    if rows_sdg_gri:
        with open(out_sdg_gri, 'w', newline='', encoding='utf-8') as f:
            wr = csv.writer(f)
            wr.writerow(['sdg_indicator_code','gri_standard','gri_disclosure'])
            wr.writerows(rows_sdg_gri)
        logging.info(f"Yazıldı: {out_sdg_gri} ({len(rows_sdg_gri)} satır)")
    else:
        logging.warning("Uyarı: sdg_gri çıktısı için veri bulunamadı.")

    if rows_sdg_tsrs:
        with open(out_sdg_tsrs, 'w', newline='', encoding='utf-8') as f:
            wr = csv.writer(f)
            wr.writerow(['sdg_indicator_code','tsrs_section','tsrs_metric'])
            wr.writerows(rows_sdg_tsrs)
        logging.info(f"Yazıldı: {out_sdg_tsrs} ({len(rows_sdg_tsrs)} satır)")
    else:
        logging.warning("Uyarı: sdg_tsrs çıktısı için veri bulunamadı.")

    if rows_gri_tsrs:
        with open(out_gri_tsrs, 'w', newline='', encoding='utf-8') as f:
            wr = csv.writer(f)
            wr.writerow(['gri_standard','gri_disclosure','tsrs_section','tsrs_metric'])
            wr.writerows(sorted(rows_gri_tsrs))
        logging.info(f"Yazıldı: {out_gri_tsrs} ({len(rows_gri_tsrs)} satır)")
    else:
        logging.warning("Uyarı: gri_tsrs çıktısı için veri bulunamadı.")

def main() -> None:
    default_excel = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SDG_232.xlsx'))
    excel = sys.argv[1] if len(sys.argv) > 1 else default_excel
    build_from_excel(excel)

if __name__ == '__main__':
    main()
