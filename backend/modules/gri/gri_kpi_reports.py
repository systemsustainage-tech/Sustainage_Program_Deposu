#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI KPI & Target Progress Reports - Sprint 3
KPI Dashboard ve Target Progress raporları
"""

import logging
import os
import sqlite3
from typing import Dict

import pandas as pd
from config.database import DB_PATH


class GRIKPIReports:
    """GRI KPI ve Target Progress raporları sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        # db_path göreli ise proje köküne göre mutlak hale getir
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def generate_kpi_dashboard(self, company_id: int = 1) -> Dict:
        """KPI Dashboard oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("GRI KPI Dashboard oluşturuluyor...")

            # KPI verilerini al
            cursor.execute("""
                SELECT 
                    k.id,
                    k.indicator_id,
                    k.name as kpi_name,
                    k.formula,
                    k.unit,
                    k.frequency,
                    k.owner,
                    k.notes,
                    gi.code as disclosure_code,
                    gi.title as disclosure_title,
                    gi.description,
                    gs.code as standard_code,
                    gs.category,
                    gr.response_value,
                    gr.numerical_value,
                    gr.reporting_status,
                    gr.period
                FROM gri_kpis k
                JOIN gri_indicators gi ON k.indicator_id = gi.id
                JOIN gri_standards gs ON gi.standard_id = gs.id
                LEFT JOIN gri_responses gr ON gi.id = gr.indicator_id AND gr.company_id = ?
                ORDER BY gs.category, gi.code
            """, (company_id,))

            kpi_data = cursor.fetchall()

            # KPI'ları kategorilere göre organize et
            kpi_dashboard = {
                'universal': [],
                'economic': [],
                'environmental': [],
                'social': [],
                'sector': [],
                'summary': {
                    'total_kpis': len(kpi_data),
                    'reported_kpis': 0,
                    'pending_kpis': 0,
                    'categories': {}
                }
            }

            for kpi in kpi_data:
                category = kpi[12]  # gs.category
                has_response = kpi[13] is not None  # gr.response_value

                kpi_info = {
                    'kpi_id': kpi[0],
                    'indicator_id': kpi[1],
                    'kpi_name': kpi[2],
                    'formula': kpi[3],
                    'unit': kpi[4],
                    'frequency': kpi[5],
                    'owner': kpi[6],
                    'notes': kpi[7],
                    'disclosure_code': kpi[8],
                    'disclosure_title': kpi[9],
                    'description': kpi[10],
                    'standard_code': kpi[11],
                    'category': category,
                    'response_value': kpi[13],
                    'numerical_value': kpi[14],
                    'reporting_status': kpi[15],
                    'period': kpi[16],
                    'has_response': has_response
                }

                if category == 'Universal':
                    kpi_dashboard['universal'].append(kpi_info)
                elif category == 'Economic':
                    kpi_dashboard['economic'].append(kpi_info)
                elif category == 'Environmental':
                    kpi_dashboard['environmental'].append(kpi_info)
                elif category == 'Social':
                    kpi_dashboard['social'].append(kpi_info)
                elif category == 'Sector-Specific':
                    kpi_dashboard['sector'].append(kpi_info)

                # Summary güncelle
                if has_response:
                    kpi_dashboard['summary']['reported_kpis'] += 1
                else:
                    kpi_dashboard['summary']['pending_kpis'] += 1

                # Kategori bazında sayım
                if category not in kpi_dashboard['summary']['categories']:
                    kpi_dashboard['summary']['categories'][category] = {
                        'total': 0,
                        'reported': 0,
                        'pending': 0
                    }

                kpi_dashboard['summary']['categories'][category]['total'] += 1
                if has_response:
                    kpi_dashboard['summary']['categories'][category]['reported'] += 1
                else:
                    kpi_dashboard['summary']['categories'][category]['pending'] += 1

            return kpi_dashboard

        except Exception as e:
            logging.error(f"KPI Dashboard oluşturma hatası: {e}")
            return {}
        finally:
            conn.close()

    def generate_target_progress(self, company_id: int = 1) -> Dict:
        """Target Progress raporu oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("GRI Target Progress raporu oluşturuluyor...")

            # Target verilerini al
            cursor.execute("""
                SELECT 
                    t.id,
                    t.indicator_id,
                    t.year,
                    t.target_value,
                    t.unit,
                    t.method,
                    t.notes,
                    gi.code as disclosure_code,
                    gi.title as disclosure_title,
                    gs.code as standard_code,
                    gs.category,
                    gr.response_value,
                    gr.numerical_value,
                    gr.reporting_status,
                    gr.period
                FROM gri_targets t
                JOIN gri_indicators gi ON t.indicator_id = gi.id
                JOIN gri_standards gs ON gi.standard_id = gs.id
                LEFT JOIN gri_responses gr ON gi.id = gr.indicator_id AND gr.company_id = ?
                ORDER BY t.year, gs.category, gi.code
            """, (company_id,))

            target_data = cursor.fetchall()

            # Target'ları yıllara göre organize et
            target_progress = {
                '2024': [],
                '2025': [],
                'summary': {
                    'total_targets': len(target_data),
                    'targets_2024': 0,
                    'targets_2025': 0,
                    'achieved_targets': 0,
                    'on_track_targets': 0,
                    'at_risk_targets': 0
                }
            }

            for target in target_data:
                year = str(target[2])  # t.year
                has_response = target[11] is not None  # gr.response_value
                target_value = target[3]  # t.target_value
                actual_value = target[12]  # gr.numerical_value

                target_info = {
                    'target_id': target[0],
                    'indicator_id': target[1],
                    'year': year,
                    'target_value': target_value,
                    'unit': target[4],
                    'method': target[5],
                    'notes': target[6],
                    'disclosure_code': target[7],
                    'disclosure_title': target[8],
                    'standard_code': target[9],
                    'category': target[10],
                    'response_value': target[11],
                    'actual_value': actual_value,
                    'reporting_status': target[13],
                    'period': target[14],
                    'has_response': has_response,
                    'progress_status': self.calculate_progress_status(target_value, actual_value, has_response)
                }

                if year == '2024':
                    target_progress['2024'].append(target_info)
                    target_progress['summary']['targets_2024'] += 1
                elif year == '2025':
                    target_progress['2025'].append(target_info)
                    target_progress['summary']['targets_2025'] += 1

                # Progress status'a göre sayım
                if target_info['progress_status'] == 'Achieved':
                    target_progress['summary']['achieved_targets'] += 1
                elif target_info['progress_status'] == 'On Track':
                    target_progress['summary']['on_track_targets'] += 1
                elif target_info['progress_status'] == 'At Risk':
                    target_progress['summary']['at_risk_targets'] += 1

            return target_progress

        except Exception as e:
            logging.error(f"Target Progress oluşturma hatası: {e}")
            return {}
        finally:
            conn.close()

    def calculate_progress_status(self, target_value, actual_value, has_response) -> None:
        """Progress status hesapla"""
        if not has_response or not target_value or not actual_value:
            return 'No Data'

        try:
            target_num = float(target_value)
            actual_num = float(actual_value)

            if actual_num >= target_num:
                return 'Achieved'
            elif actual_num >= target_num * 0.8:  # %80'ine ulaştıysa
                return 'On Track'
            elif actual_num >= target_num * 0.5:  # %50'sine ulaştıysa
                return 'At Risk'
            else:
                return 'Behind Schedule'

        except (ValueError, TypeError):
            return 'Invalid Data'

    def export_kpi_dashboard_excel(self, output_path: str, company_id: int = 1) -> bool:
        """KPI Dashboard'u Excel'e export et"""
        try:
            logging.info(f"GRI KPI Dashboard Excel export başlıyor: {output_path}")

            # KPI Dashboard oluştur
            kpi_data = self.generate_kpi_dashboard(company_id)
            if not kpi_data:
                logging.info("KPI Dashboard oluşturulamadı!")
                return False

            # Excel writer oluştur
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

                # 1. Özet Sayfası
                self.create_kpi_summary_sheet(writer, kpi_data)

                # 2. Universal KPI'lar
                self.create_kpi_category_sheet(writer, kpi_data['universal'], 'Universal KPIs')

                # 3. Economic KPI'lar
                self.create_kpi_category_sheet(writer, kpi_data['economic'], 'Economic KPIs')

                # 4. Environmental KPI'lar
                self.create_kpi_category_sheet(writer, kpi_data['environmental'], 'Environmental KPIs')

                # 5. Social KPI'lar
                self.create_kpi_category_sheet(writer, kpi_data['social'], 'Social KPIs')

                # 6. Sector KPI'lar
                self.create_kpi_category_sheet(writer, kpi_data['sector'], 'Sector KPIs')

            logging.info(f"GRI KPI Dashboard başarıyla export edildi: {output_path}")
            return True

        except Exception as e:
            logging.error(f"KPI Dashboard Excel export hatası: {e}")
            return False

    def export_target_progress_excel(self, output_path: str, company_id: int = 1) -> bool:
        """Target Progress'i Excel'e export et"""
        try:
            logging.info(f"GRI Target Progress Excel export başlıyor: {output_path}")

            # Target Progress oluştur
            target_data = self.generate_target_progress(company_id)
            if not target_data:
                logging.info("Target Progress oluşturulamadı!")
                return False

            # Excel writer oluştur
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

                # 1. Özet Sayfası
                self.create_target_summary_sheet(writer, target_data)

                # 2. 2024 Hedefleri
                self.create_target_year_sheet(writer, target_data['2024'], '2024 Targets')

                # 3. 2025 Hedefleri
                self.create_target_year_sheet(writer, target_data['2025'], '2025 Targets')

                # 4. Progress Status
                self.create_progress_status_sheet(writer, target_data)

            logging.info(f"GRI Target Progress başarıyla export edildi: {output_path}")
            return True

        except Exception as e:
            logging.error(f"Target Progress Excel export hatası: {e}")
            return False

    def create_kpi_summary_sheet(self, writer, kpi_data) -> None:
        """KPI özet sayfası oluştur"""
        summary = kpi_data['summary']

        # Özet verisi
        summary_data = [
            {'Metrik': 'Toplam KPI', 'Değer': summary['total_kpis']},
            {'Metrik': 'Raporlanan KPI', 'Değer': summary['reported_kpis']},
            {'Metrik': 'Bekleyen KPI', 'Değer': summary['pending_kpis']},
            {'Metrik': 'Raporlama Oranı (%)', 'Değer': round((summary['reported_kpis'] / summary['total_kpis'] * 100) if summary['total_kpis'] > 0 else 0, 1)}
        ]

        # Kategori bazında özet
        for category, stats in summary['categories'].items():
            summary_data.append({
                'Metrik': f'{category} - Toplam',
                'Değer': stats['total']
            })
            summary_data.append({
                'Metrik': f'{category} - Raporlanan',
                'Değer': stats['reported']
            })
            summary_data.append({
                'Metrik': f'{category} - Bekleyen',
                'Değer': stats['pending']
            })

        df = pd.DataFrame(summary_data)
        df.to_excel(writer, sheet_name='KPI Özet', index=False)

    def create_kpi_category_sheet(self, writer, kpis, sheet_name) -> None:
        """KPI kategori sayfası oluştur"""
        if not kpis:
            df = pd.DataFrame({'Mesaj': ['Bu kategoride KPI bulunmamaktadır.']})
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            return

        sheet_data = []

        for kpi in kpis:
            sheet_data.append({
                'Standard Code': kpi['standard_code'],
                'Disclosure Code': kpi['disclosure_code'],
                'KPI Name': kpi['kpi_name'],
                'Formula': kpi['formula'],
                'Unit': kpi['unit'],
                'Frequency': kpi['frequency'],
                'Owner': kpi['owner'],
                'Notes': kpi['notes'],
                'Response Value': kpi['response_value'],
                'Numerical Value': kpi['numerical_value'],
                'Reporting Status': kpi['reporting_status'],
                'Period': kpi['period'],
                'Has Response': 'Yes' if kpi['has_response'] else 'No'
            })

        df = pd.DataFrame(sheet_data)
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    def create_target_summary_sheet(self, writer, target_data) -> None:
        """Target özet sayfası oluştur"""
        summary = target_data['summary']

        summary_info = [
            {'Metrik': 'Toplam Hedef', 'Değer': summary['total_targets']},
            {'Metrik': '2024 Hedefleri', 'Değer': summary['targets_2024']},
            {'Metrik': '2025 Hedefleri', 'Değer': summary['targets_2025']},
            {'Metrik': 'Başarılan Hedefler', 'Değer': summary['achieved_targets']},
            {'Metrik': 'Yolda Hedefler', 'Değer': summary['on_track_targets']},
            {'Metrik': 'Riskli Hedefler', 'Değer': summary['at_risk_targets']}
        ]

        df = pd.DataFrame(summary_info)
        df.to_excel(writer, sheet_name='Target Özet', index=False)

    def create_target_year_sheet(self, writer, targets, sheet_name) -> None:
        """Target yıl sayfası oluştur"""
        if not targets:
            df = pd.DataFrame({'Mesaj': ['Bu yıl için hedef bulunmamaktadır.']})
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            return

        sheet_data = []

        for target in targets:
            sheet_data.append({
                'Standard Code': target['standard_code'],
                'Disclosure Code': target['disclosure_code'],
                'Target Value': target['target_value'],
                'Actual Value': target['actual_value'],
                'Unit': target['unit'],
                'Method': target['method'],
                'Notes': target['notes'],
                'Response Value': target['response_value'],
                'Reporting Status': target['reporting_status'],
                'Period': target['period'],
                'Progress Status': target['progress_status'],
                'Has Response': 'Yes' if target['has_response'] else 'No'
            })

        df = pd.DataFrame(sheet_data)
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    def create_progress_status_sheet(self, writer, target_data) -> None:
        """Progress status sayfası oluştur"""
        all_targets = target_data['2024'] + target_data['2025']

        # Progress status'a göre grupla
        progress_stats = {}
        for target in all_targets:
            status = target['progress_status']
            if status not in progress_stats:
                progress_stats[status] = []
            progress_stats[status].append(target)

        # Her status için ayrı sheet oluştur
        for status, targets in progress_stats.items():
            if not targets:
                continue

            sheet_data = []
            for target in targets:
                sheet_data.append({
                    'Year': target['year'],
                    'Standard Code': target['standard_code'],
                    'Disclosure Code': target['disclosure_code'],
                    'Target Value': target['target_value'],
                    'Actual Value': target['actual_value'],
                    'Unit': target['unit'],
                    'Progress Status': target['progress_status'],
                    'Notes': target['notes']
                })

            df = pd.DataFrame(sheet_data)
            sheet_name = f'Progress {status}'[:31]  # Excel sheet name limit
            df.to_excel(writer, sheet_name=sheet_name, index=False)

def export_gri_kpi_dashboard(output_path: str, company_id: int = 1) -> None:
    """GRI KPI Dashboard export fonksiyonu"""
    kpi_reports = GRIKPIReports()
    return kpi_reports.export_kpi_dashboard_excel(output_path, company_id)

def export_gri_target_progress(output_path: str, company_id: int = 1) -> None:
    """GRI Target Progress export fonksiyonu"""
    kpi_reports = GRIKPIReports()
    return kpi_reports.export_target_progress_excel(output_path, company_id)

if __name__ == "__main__":
    # Test exports
    kpi_output = "gri/gri_kpi_dashboard_test.xlsx"
    target_output = "gri/gri_target_progress_test.xlsx"

    if export_gri_kpi_dashboard(kpi_output):
        logging.info(f"GRI KPI Dashboard başarıyla oluşturuldu: {kpi_output}")

    if export_gri_target_progress(target_output):
        logging.info(f"GRI Target Progress başarıyla oluşturuldu: {target_output}")
