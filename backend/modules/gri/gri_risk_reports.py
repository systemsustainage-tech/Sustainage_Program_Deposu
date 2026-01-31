#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Risk Reports & SDG/TSRS Mapping Summaries - Sprint 4
Risk değerlendirme raporları ve eşleştirme özetleri
"""

import logging
import os
import sqlite3
from typing import Dict

import pandas as pd
from config.database import DB_PATH


class GRIRiskReports:
    """GRI Risk ve Eşleştirme raporları sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        # db_path göreli ise proje köküne göre mutlak hale getir
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def generate_risk_assessment(self, company_id: int = 1) -> Dict:
        """Risk değerlendirme raporu oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("GRI Risk Değerlendirme raporu oluşturuluyor...")

            # Risk verilerini al
            cursor.execute("""
                SELECT 
                    r.id,
                    r.indicator_id,
                    r.risk_level,
                    r.impact,
                    r.likelihood,
                    r.notes,
                    gi.code as disclosure_code,
                    gi.title as disclosure_title,
                    gi.description,
                    gs.code as standard_code,
                    gs.category,
                    gr.response_value,
                    gr.numerical_value,
                    gr.reporting_status,
                    gr.period
                FROM gri_risks r
                JOIN gri_indicators gi ON r.indicator_id = gi.id
                JOIN gri_standards gs ON gi.standard_id = gs.id
                LEFT JOIN gri_responses gr ON gi.id = gr.indicator_id AND gr.company_id = ?
                ORDER BY 
                    CASE r.risk_level 
                        WHEN 'Critical' THEN 1
                        WHEN 'High' THEN 2
                        WHEN 'Medium' THEN 3
                        WHEN 'Low' THEN 4
                        ELSE 5
                    END,
                    gs.category, gi.code
            """, (company_id,))

            risk_data = cursor.fetchall()

            # Risk'leri seviyeye göre organize et
            risk_assessment = {
                'critical': [],
                'high': [],
                'medium': [],
                'low': [],
                'summary': {
                    'total_risks': len(risk_data),
                    'critical_risks': 0,
                    'high_risks': 0,
                    'medium_risks': 0,
                    'low_risks': 0,
                    'categories': {}
                }
            }

            for risk in risk_data:
                risk_level = risk[2]  # r.risk_level
                has_response = risk[11] is not None  # gr.response_value

                risk_info = {
                    'risk_id': risk[0],
                    'indicator_id': risk[1],
                    'risk_level': risk_level,
                    'impact': risk[3],
                    'likelihood': risk[4],
                    'notes': risk[5],
                    'disclosure_code': risk[6],
                    'disclosure_title': risk[7],
                    'description': risk[8],
                    'standard_code': risk[9],
                    'category': risk[10],
                    'response_value': risk[11],
                    'numerical_value': risk[12],
                    'reporting_status': risk[13],
                    'period': risk[14],
                    'has_response': has_response,
                    'risk_score': self.calculate_risk_score(risk[3], risk[4])
                }

                # Risk seviyesine göre kategorize et
                if risk_level == 'Critical':
                    risk_assessment['critical'].append(risk_info)
                    risk_assessment['summary']['critical_risks'] += 1
                elif risk_level == 'High':
                    risk_assessment['high'].append(risk_info)
                    risk_assessment['summary']['high_risks'] += 1
                elif risk_level == 'Medium':
                    risk_assessment['medium'].append(risk_info)
                    risk_assessment['summary']['medium_risks'] += 1
                elif risk_level == 'Low':
                    risk_assessment['low'].append(risk_info)
                    risk_assessment['summary']['low_risks'] += 1

                # Kategori bazında sayım
                category = risk[10]  # gs.category
                if category not in risk_assessment['summary']['categories']:
                    risk_assessment['summary']['categories'][category] = {
                        'total': 0,
                        'critical': 0,
                        'high': 0,
                        'medium': 0,
                        'low': 0
                    }

                risk_assessment['summary']['categories'][category]['total'] += 1
                # Risk level'ı güvenli şekilde map et
                risk_level_key = risk_level.lower() if risk_level else 'unknown'
                if risk_level_key in risk_assessment['summary']['categories'][category]:
                    risk_assessment['summary']['categories'][category][risk_level_key] += 1

            return risk_assessment

        except Exception as e:
            logging.error(f"Risk Değerlendirme oluşturma hatası: {e}")
            return {}
        finally:
            conn.close()

    def calculate_risk_score(self, impact, likelihood) -> None:
        """Risk skoru hesapla (1-25)"""
        impact_scores = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
        likelihood_scores = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}

        impact_score = impact_scores.get(impact, 1)
        likelihood_score = likelihood_scores.get(likelihood, 1)

        return impact_score * likelihood_score

    def generate_sdg_gri_mapping_summary(self) -> Dict:
        """SDG-GRI eşleştirme özeti oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("SDG-GRI eşleştirme özeti oluşturuluyor...")

            # SDG-GRI eşleştirmelerini al
            cursor.execute("""
                SELECT 
                    sg.sdg_indicator_code,
                    sg.gri_standard,
                    sg.gri_disclosure,
                    gi.code as disclosure_code,
                    gi.title as disclosure_title,
                    gs.category,
                    gs.code as standard_code
                FROM map_sdg_gri sg
                LEFT JOIN gri_indicators gi ON sg.gri_disclosure = gi.code
                LEFT JOIN gri_standards gs ON gi.standard_id = gs.id
                ORDER BY sg.sdg_indicator_code, sg.gri_standard, sg.gri_disclosure
            """)

            mapping_data = cursor.fetchall()

            # SDG bazında grupla
            sdg_mapping = {}

            for mapping in mapping_data:
                sdg_code = mapping[0]  # sg.sdg_indicator_code

                if sdg_code not in sdg_mapping:
                    sdg_mapping[sdg_code] = {
                        'sdg_indicator': sdg_code,
                        'gri_standards': [],
                        'total_gri_disclosures': 0
                    }

                gri_info = {
                    'gri_standard': mapping[1],
                    'gri_disclosure': mapping[2],
                    'disclosure_code': mapping[3],
                    'disclosure_title': mapping[4],
                    'category': mapping[5],
                    'standard_code': mapping[6]
                }

                sdg_mapping[sdg_code]['gri_standards'].append(gri_info)
                sdg_mapping[sdg_code]['total_gri_disclosures'] += 1

            # Özet bilgileri
            mapping_summary = {
                'mappings': sdg_mapping,
                'summary': {
                    'total_sdg_indicators': len(sdg_mapping),
                    'total_mappings': len(mapping_data),
                    'avg_mappings_per_sdg': round(len(mapping_data) / len(sdg_mapping), 2) if sdg_mapping else 0,
                    'categories': {}
                }
            }

            # Kategori bazında sayım
            for sdg_code, data in sdg_mapping.items():
                for gri_standard in data['gri_standards']:
                    category = gri_standard['category']
                    if category not in mapping_summary['summary']['categories']:
                        mapping_summary['summary']['categories'][category] = 0
                    mapping_summary['summary']['categories'][category] += 1

            return mapping_summary

        except Exception as e:
            logging.error(f"SDG-GRI eşleştirme özeti oluşturma hatası: {e}")
            return {}
        finally:
            conn.close()

    def generate_gri_tsrs_mapping_summary(self) -> Dict:
        """GRI-TSRS eşleştirme özeti oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("GRI-TSRS eşleştirme özeti oluşturuluyor...")

            # GRI-TSRS eşleştirmelerini al
            cursor.execute("""
                SELECT 
                    gt.gri_disclosure,
                    gt.tsrs_section,
                    gt.tsrs_metric,
                    gi.code as disclosure_code,
                    gi.title as disclosure_title,
                    gs.category,
                    gs.code as standard_code
                FROM map_gri_tsrs gt
                LEFT JOIN gri_indicators gi ON gt.gri_disclosure = gi.code
                LEFT JOIN gri_standards gs ON gi.standard_id = gs.id
                ORDER BY gt.gri_disclosure, gt.tsrs_section, gt.tsrs_metric
            """)

            mapping_data = cursor.fetchall()

            # GRI bazında grupla
            gri_mapping = {}

            for mapping in mapping_data:
                gri_disclosure = mapping[0]  # gt.gri_disclosure

                if gri_disclosure not in gri_mapping:
                    gri_mapping[gri_disclosure] = {
                        'gri_disclosure': gri_disclosure,
                        'tsrs_sections': [],
                        'total_tsrs_metrics': 0
                    }

                tsrs_info = {
                    'tsrs_section': mapping[1],
                    'tsrs_metric': mapping[2],
                    'disclosure_code': mapping[3],
                    'disclosure_title': mapping[4],
                    'category': mapping[5],
                    'standard_code': mapping[6]
                }

                gri_mapping[gri_disclosure]['tsrs_sections'].append(tsrs_info)
                gri_mapping[gri_disclosure]['total_tsrs_metrics'] += 1

            # Özet bilgileri
            mapping_summary = {
                'mappings': gri_mapping,
                'summary': {
                    'total_gri_disclosures': len(gri_mapping),
                    'total_mappings': len(mapping_data),
                    'avg_mappings_per_gri': round(len(mapping_data) / len(gri_mapping), 2) if gri_mapping else 0,
                    'categories': {}
                }
            }

            # Kategori bazında sayım
            for gri_disclosure, data in gri_mapping.items():
                for tsrs_section in data['tsrs_sections']:
                    category = tsrs_section['category']
                    if category not in mapping_summary['summary']['categories']:
                        mapping_summary['summary']['categories'][category] = 0
                    mapping_summary['summary']['categories'][category] += 1

            return mapping_summary

        except Exception as e:
            logging.error(f"GRI-TSRS eşleştirme özeti oluşturma hatası: {e}")
            return {}
        finally:
            conn.close()

    def export_risk_assessment_excel(self, output_path: str, company_id: int = 1) -> bool:
        """Risk değerlendirme raporunu Excel'e export et"""
        try:
            logging.info(f"GRI Risk Assessment Excel export başlıyor: {output_path}")

            # Risk assessment oluştur
            risk_data = self.generate_risk_assessment(company_id)
            if not risk_data:
                logging.info("Risk Assessment oluşturulamadı!")
                return False

            # Excel writer oluştur
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

                # 1. Özet Sayfası
                self.create_risk_summary_sheet(writer, risk_data)

                # 2. Critical Risks
                self.create_risk_level_sheet(writer, risk_data['critical'], 'Critical Risks')

                # 3. High Risks
                self.create_risk_level_sheet(writer, risk_data['high'], 'High Risks')

                # 4. Medium Risks
                self.create_risk_level_sheet(writer, risk_data['medium'], 'Medium Risks')

                # 5. Low Risks
                self.create_risk_level_sheet(writer, risk_data['low'], 'Low Risks')

                # 6. Risk Matrix
                self.create_risk_matrix_sheet(writer, risk_data)

            logging.info(f"GRI Risk Assessment başarıyla export edildi: {output_path}")
            return True

        except Exception as e:
            logging.error(f"Risk Assessment Excel export hatası: {e}")
            return False

    def export_mapping_summaries_excel(self, output_path: str) -> bool:
        """Eşleştirme özetlerini Excel'e export et"""
        try:
            logging.info(f"GRI Mapping Summaries Excel export başlıyor: {output_path}")

            # Eşleştirme özetlerini oluştur
            sdg_mapping = self.generate_sdg_gri_mapping_summary()
            tsrs_mapping = self.generate_gri_tsrs_mapping_summary()

            if not sdg_mapping and not tsrs_mapping:
                logging.info("Eşleştirme özetleri oluşturulamadı!")
                return False

            # Excel writer oluştur
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

                # 1. SDG-GRI Özet
                if sdg_mapping:
                    self.create_sdg_gri_summary_sheet(writer, sdg_mapping)
                    self.create_sdg_gri_detail_sheet(writer, sdg_mapping)

                # 2. GRI-TSRS Özet
                if tsrs_mapping:
                    self.create_gri_tsrs_summary_sheet(writer, tsrs_mapping)
                    self.create_gri_tsrs_detail_sheet(writer, tsrs_mapping)

                # 3. Genel Özet
                self.create_mapping_overview_sheet(writer, sdg_mapping, tsrs_mapping)

            logging.info(f"GRI Mapping Summaries başarıyla export edildi: {output_path}")
            return True

        except Exception as e:
            logging.error(f"Mapping Summaries Excel export hatası: {e}")
            return False

    def create_risk_summary_sheet(self, writer, risk_data) -> None:
        """Risk özet sayfası oluştur"""
        summary = risk_data['summary']

        summary_info = [
            {'Metrik': 'Toplam Risk', 'Değer': summary['total_risks']},
            {'Metrik': 'Critical Riskler', 'Değer': summary['critical_risks']},
            {'Metrik': 'High Riskler', 'Değer': summary['high_risks']},
            {'Metrik': 'Medium Riskler', 'Değer': summary['medium_risks']},
            {'Metrik': 'Low Riskler', 'Değer': summary['low_risks']}
        ]

        # Kategori bazında özet
        for category, stats in summary['categories'].items():
            summary_info.append({
                'Metrik': f'{category} - Toplam',
                'Değer': stats['total']
            })
            summary_info.append({
                'Metrik': f'{category} - Critical',
                'Değer': stats['critical']
            })
            summary_info.append({
                'Metrik': f'{category} - High',
                'Değer': stats['high']
            })

        df = pd.DataFrame(summary_info)
        df.to_excel(writer, sheet_name='Risk Özet', index=False)

    def create_risk_level_sheet(self, writer, risks, sheet_name) -> None:
        """Risk seviye sayfası oluştur"""
        if not risks:
            df = pd.DataFrame({'Mesaj': ['Bu seviyede risk bulunmamaktadır.']})
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            return

        sheet_data = []

        for risk in risks:
            sheet_data.append({
                'Standard Code': risk['standard_code'],
                'Disclosure Code': risk['disclosure_code'],
                'Risk Level': risk['risk_level'],
                'Impact': risk['impact'],
                'Likelihood': risk['likelihood'],
                'Risk Score': risk['risk_score'],
                'Notes': risk['notes'],
                'Response Value': risk['response_value'],
                'Numerical Value': risk['numerical_value'],
                'Reporting Status': risk['reporting_status'],
                'Period': risk['period'],
                'Has Response': 'Yes' if risk['has_response'] else 'No'
            })

        df = pd.DataFrame(sheet_data)
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    def create_risk_matrix_sheet(self, writer, risk_data) -> None:
        """Risk matrix sayfası oluştur"""
        all_risks = (risk_data['critical'] + risk_data['high'] +
                    risk_data['medium'] + risk_data['low'])

        matrix_data = []
        for risk in all_risks:
            matrix_data.append({
                'Disclosure Code': risk['disclosure_code'],
                'Impact': risk['impact'],
                'Likelihood': risk['likelihood'],
                'Risk Level': risk['risk_level'],
                'Risk Score': risk['risk_score'],
                'Category': risk['category']
            })

        df = pd.DataFrame(matrix_data)
        df.to_excel(writer, sheet_name='Risk Matrix', index=False)

    def create_sdg_gri_summary_sheet(self, writer, sdg_mapping) -> None:
        """SDG-GRI özet sayfası oluştur"""
        summary = sdg_mapping['summary']

        summary_info = [
            {'Metrik': 'Toplam SDG Indicator', 'Değer': summary['total_sdg_indicators']},
            {'Metrik': 'Toplam Eşleştirme', 'Değer': summary['total_mappings']},
            {'Metrik': 'SDG Başına Ortalama Eşleştirme', 'Değer': summary['avg_mappings_per_sdg']}
        ]

        # Kategori bazında özet
        for category, count in summary['categories'].items():
            summary_info.append({
                'Metrik': f'{category} - Eşleştirme Sayısı',
                'Değer': count
            })

        df = pd.DataFrame(summary_info)
        df.to_excel(writer, sheet_name='SDG-GRI Özet', index=False)

    def create_sdg_gri_detail_sheet(self, writer, sdg_mapping) -> None:
        """SDG-GRI detay sayfası oluştur"""
        detail_data = []

        for sdg_code, data in sdg_mapping['mappings'].items():
            for gri_standard in data['gri_standards']:
                detail_data.append({
                    'SDG Indicator': sdg_code,
                    'GRI Standard': gri_standard['gri_standard'],
                    'GRI Disclosure': gri_standard['gri_disclosure'],
                    'Disclosure Code': gri_standard['disclosure_code'],
                    'Disclosure Title': gri_standard['disclosure_title'],
                    'Category': gri_standard['category'],
                    'Standard Code': gri_standard['standard_code']
                })

        df = pd.DataFrame(detail_data)
        df.to_excel(writer, sheet_name='SDG-GRI Detay', index=False)

    def create_gri_tsrs_summary_sheet(self, writer, tsrs_mapping) -> None:
        """GRI-TSRS özet sayfası oluştur"""
        summary = tsrs_mapping['summary']

        summary_info = [
            {'Metrik': 'Toplam GRI Disclosure', 'Değer': summary['total_gri_disclosures']},
            {'Metrik': 'Toplam Eşleştirme', 'Değer': summary['total_mappings']},
            {'Metrik': 'GRI Başına Ortalama Eşleştirme', 'Değer': summary['avg_mappings_per_gri']}
        ]

        # Kategori bazında özet
        for category, count in summary['categories'].items():
            summary_info.append({
                'Metrik': f'{category} - Eşleştirme Sayısı',
                'Değer': count
            })

        df = pd.DataFrame(summary_info)
        df.to_excel(writer, sheet_name='GRI-TSRS Özet', index=False)

    def create_gri_tsrs_detail_sheet(self, writer, tsrs_mapping) -> None:
        """GRI-TSRS detay sayfası oluştur"""
        detail_data = []

        for gri_disclosure, data in tsrs_mapping['mappings'].items():
            for tsrs_section in data['tsrs_sections']:
                detail_data.append({
                    'GRI Disclosure': gri_disclosure,
                    'TSRS Section': tsrs_section['tsrs_section'],
                    'TSRS Metric': tsrs_section['tsrs_metric'],
                    'Disclosure Code': tsrs_section['disclosure_code'],
                    'Disclosure Title': tsrs_section['disclosure_title'],
                    'Category': tsrs_section['category'],
                    'Standard Code': tsrs_section['standard_code']
                })

        df = pd.DataFrame(detail_data)
        df.to_excel(writer, sheet_name='GRI-TSRS Detay', index=False)

    def create_mapping_overview_sheet(self, writer, sdg_mapping, tsrs_mapping) -> None:
        """Eşleştirme genel bakış sayfası oluştur"""
        overview_data = []

        # SDG-GRI özeti
        if sdg_mapping:
            overview_data.append({
                'Mapping Type': 'SDG-GRI',
                'Total Indicators': sdg_mapping['summary']['total_sdg_indicators'],
                'Total Mappings': sdg_mapping['summary']['total_mappings'],
                'Average per Indicator': sdg_mapping['summary']['avg_mappings_per_sdg']
            })

        # GRI-TSRS özeti
        if tsrs_mapping:
            overview_data.append({
                'Mapping Type': 'GRI-TSRS',
                'Total Indicators': tsrs_mapping['summary']['total_gri_disclosures'],
                'Total Mappings': tsrs_mapping['summary']['total_mappings'],
                'Average per Indicator': tsrs_mapping['summary']['avg_mappings_per_gri']
            })

        df = pd.DataFrame(overview_data)
        df.to_excel(writer, sheet_name='Mapping Overview', index=False)

def export_gri_risk_assessment(output_path: str, company_id: int = 1) -> None:
    """GRI Risk Assessment export fonksiyonu"""
    risk_reports = GRIRiskReports()
    return risk_reports.export_risk_assessment_excel(output_path, company_id)

def export_gri_mapping_summaries(output_path: str) -> None:
    """GRI Mapping Summaries export fonksiyonu"""
    risk_reports = GRIRiskReports()
    return risk_reports.export_mapping_summaries_excel(output_path)

if __name__ == "__main__":
    # Test exports
    risk_output = "gri/gri_risk_assessment_test.xlsx"
    mapping_output = "gri/gri_mapping_summaries_test.xlsx"

    if export_gri_risk_assessment(risk_output):
        logging.info(f"GRI Risk Assessment başarıyla oluşturuldu: {risk_output}")

    if export_gri_mapping_summaries(mapping_output):
        logging.info(f"GRI Mapping Summaries başarıyla oluşturuldu: {mapping_output}")
