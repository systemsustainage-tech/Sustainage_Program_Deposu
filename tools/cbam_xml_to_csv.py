#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
CBAM XML → CSV dönüştürücü

Kaynak: Avrupa Komisyonu CBAM Geçiş Kayıt Defteri XSD (v23.00)
- QReport_ver23.00.xsd
- stypes_ver23.00.xsd

Girdi: CBAM XML dosyası (QReport)
Çıktı: CSV satırları (data/imports/templates/eu/cbam/reports.csv şablonuna uyumlu)

Kullanım:
  python tools/cbam_xml_to_csv.py --xml docs/eu_cbam/samples/QReport.xml \
      --out data/imports/generated/eu/cbam/report.csv \
      --company-from declarant

Notlar:
- Ürün miktarı için ImportedGood/MeasureImported içindeki MeasurementUnit'e göre dönüşüm yapılır:
  * 'TNE' ise doğrudan ton cinsinden alınır.
  * 'KGM' ise kilogram → ton (bölü 1000) dönüşümü yapılır.
  * Diğer birimler bulunursa konservatif şekilde NetMass kullanılır (dönüşüm yapılmadan).
- Doğrudan gömülü emisyonlar (tCO2e/t): DirectEmissions/SpecificEmbeddedEmissions
- Dolaylı gömülü emisyonlar (tCO2e/t): IndirectEmissions/SpecificEmbeddedEmissions
- Elektrik emisyon faktörü (tCO2e/MWh gibi): IndirectEmissions/EmissionFactor (varsa)
- Hesaplama yöntemi: DirectEmissions/ApplicableReportingTypeMethodology
"""

import logging
import argparse
import csv
import os
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NS = {
    'cbam': 'http://xmlns.ec.eu/BusinessObjects/CBAM/Types/V1'
}

CSV_HEADERS = [
    'company_id', 'reporting_quarter', 'product_cn_code', 'country_of_origin',
    'quantity_tonnes', 'direct_emissions_tco2e_per_tonne', 'indirect_emissions_tco2e_per_tonne',
    'emission_calculation_method', 'installation_id', 'production_route',
    'electricity_emissions_factor', 'documentation_ref'
]

def _txt(el: Optional[ET.Element]) -> Optional[str]:
    return el.text.strip() if (el is not None and el.text is not None) else None

def _find(parent: ET.Element, path: str) -> Optional[ET.Element]:
    return parent.find(path, NS)

def _findall(parent: ET.Element, path: str) -> None:
    return parent.findall(path, NS)

def build_reporting_quarter(root: ET.Element) -> str:
    year = _txt(_find(root, 'cbam:Year'))
    period = _txt(_find(root, 'cbam:ReportingPeriod'))  # beklenen: '01','02','03','04'
    qmap = {'01': 'Q1', '02': 'Q2', '03': 'Q3', '04': 'Q4'}
    q = qmap.get(period, f'Q{period}') if period else 'Q?'
    return f"{year}{q}" if year else q

def get_company_id(root: ET.Element, company_from: str) -> Optional[str]:
    company_from = (company_from or 'declarant').lower()
    if company_from == 'declarant':
        return _txt(_find(_find(root, 'cbam:Declarant') or root, 'cbam:Declarant/cbam:IdentificationNumber'))
    elif company_from == 'importer':
        return _txt(_find(_find(root, 'cbam:Importer') or root, 'cbam:Importer/cbam:IdentificationNumber'))
    else:
        # Varsayılan: Declarant
        return _txt(_find(_find(root, 'cbam:Declarant') or root, 'cbam:Declarant/cbam:IdentificationNumber'))

def convert_unit_to_tonnes(net_mass: Optional[str], unit: Optional[str]) -> Optional[float]:
    if net_mass is None:
        return None
    try:
        val = float(net_mass)
    except Exception as e:
        logging.warning(f"Failed to convert net_mass '{net_mass}' to float: {e}")
        return None
    if unit == 'KGM':
        return val / 1000.0
    # TNE veya bilinmeyen birim için dönüşümsüz (TNE olduğunu varsay)
    return val

def extract_row_for_imported_good(qreport: ET.Element, ig: ET.Element, company_id: str, reporting_quarter: str) -> Dict[str, Any]:
    cn_code = _txt(_find(ig, 'cbam:CommodityCode/cbam:CnCode'))
    if not cn_code:
        cn_code = _txt(_find(ig, 'cbam:CommodityCode/cbam:HsCode'))
    origin = _txt(_find(ig, 'cbam:OriginCountry/cbam:Country'))

    # MeasureImported (ilk kayıt esas alınır)
    measure = _find(ig, 'cbam:MeasureImported')
    net_mass = _txt(_find(measure, 'cbam:NetMass')) if measure is not None else None
    unit = _txt(_find(measure, 'cbam:MeasurementUnit')) if measure is not None else None
    qty_tonnes = convert_unit_to_tonnes(net_mass, unit) if net_mass else None

    # GoodsEmissions (birden fazla olabilir → her biri için satır)
    # Basit yaklaşım: ilk GoodsEmissions kaydı ile eşleştir
    ge = _find(ig, 'cbam:GoodsEmissions')
    direct = _find(ge, 'cbam:DirectEmissions') if ge is not None else None
    indirect = _find(ge, 'cbam:IndirectEmissions') if ge is not None else None
    installation_id = _txt(_find(ge, 'cbam:Installation/cbam:InstallationId')) if ge is not None else None
    production_route = _txt(_find(ge, 'cbam:ProdMethodQualifyingParams/cbam:MethodId')) if ge is not None else None

    direct_specific = _txt(_find(direct, 'cbam:SpecificEmbeddedEmissions')) if direct is not None else None
    method_code = _txt(_find(direct, 'cbam:ApplicableReportingTypeMethodology')) if direct is not None else None

    indirect_specific = _txt(_find(indirect, 'cbam:SpecificEmbeddedEmissions')) if indirect is not None else None
    electricity_factor = _txt(_find(indirect, 'cbam:EmissionFactor')) if indirect is not None else None

    # Dokümantasyon referansı: önce ReportId, yoksa SupportingDocuments/ReferenceNumber
    doc_ref = _txt(_find(qreport, 'cbam:ReportId'))
    if not doc_ref:
        sd = _find(ig, 'cbam:SupportingDocuments')
        doc_ref = _txt(_find(sd, 'cbam:ReferenceNumber')) if sd is not None else None

    row = {
        'company_id': company_id or '',
        'reporting_quarter': reporting_quarter or '',
        'product_cn_code': cn_code or '',
        'country_of_origin': origin or '',
        'quantity_tonnes': f"{qty_tonnes}" if qty_tonnes is not None else '',
        'direct_emissions_tco2e_per_tonne': direct_specific or '',
        'indirect_emissions_tco2e_per_tonne': indirect_specific or '',
        'emission_calculation_method': method_code or '',
        'installation_id': installation_id or '',
        'production_route': production_route or '',
        'electricity_emissions_factor': electricity_factor or '',
        'documentation_ref': doc_ref or ''
    }
    return row

def parse_and_convert(xml_path: str, out_csv: str, company_from: str = 'declarant') -> int:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # Kök eleman (QReport) olabilir; değilse bul
    qreport = root
    if qreport.tag.endswith('QReport') is False:
        qreport = root.find('cbam:QReport', NS)
        if qreport is None:
            raise RuntimeError('QReport elemanı bulunamadı')

    company_id = get_company_id(qreport, company_from)
    reporting_quarter = build_reporting_quarter(qreport)

    imported_goods = _findall(qreport, 'cbam:ImportedGood')
    rows = []
    for ig in imported_goods:
        row = extract_row_for_imported_good(qreport, ig, company_id or '', reporting_quarter)
        rows.append(row)

    # CSV yaz
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return len(rows)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--xml', required=True, help='Girdi CBAM XML (QReport)')
    ap.add_argument('--out', required=False, help='Çıktı CSV yolu')
    ap.add_argument('--company-from', default='declarant', choices=['declarant','importer'], help='company_id kaynağı')
    args = ap.parse_args()

    xml_path = os.path.abspath(args.xml)
    if not os.path.exists(xml_path):
        sys.exit(f"XML bulunamadı: {xml_path}")

    out_csv = args.out
    if not out_csv:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        out_csv = os.path.join(base_dir, 'data', 'imports', 'generated', 'eu', 'cbam', 'report.csv')

    out_csv = os.path.abspath(out_csv)
    count = parse_and_convert(xml_path, out_csv, company_from=args.company_from)
    logging.info(f"Dönüşüm tamam: {count} satır → {out_csv}")

if __name__ == '__main__':
    main()
