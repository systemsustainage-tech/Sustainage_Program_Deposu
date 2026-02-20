#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDP Veri Toplama Modülü
Mevcut verilerden CDP raporları için gerekli bilgileri toplar
"""

import os
import sqlite3
from typing import Any, Dict
from config.database import DB_PATH


class CDPDataCollector:
    """CDP raporları için veri toplama"""

    def __init__(self, db_path: str = DB_PATH):
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path

    def collect_climate_data(self, company_id: int, year: int) -> Dict[str, Any]:
        """İklim değişikliği verileri topla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        data = {
            'company_id': company_id,
            'year': year,
            'emissions': {},
            'energy': {},
            'targets': {},
            'risks': {},
            'opportunities': {},
            'governance': {}
        }

        try:
            # Scope 1, 2, 3 Emisyonları
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN scope = 'Scope 1' THEN total_emissions ELSE 0 END) as scope1,
                    SUM(CASE WHEN scope = 'Scope 2' THEN total_emissions ELSE 0 END) as scope2,
                    SUM(CASE WHEN scope = 'Scope 3' THEN total_emissions ELSE 0 END) as scope3,
                    SUM(total_emissions) as total
                FROM carbon_emissions
                WHERE company_id = ? AND strftime('%Y', date) = ?
            """, (company_id, str(year)))

            emissions_row = cursor.fetchone()
            if emissions_row:
                data['emissions'] = {
                    'scope1': emissions_row[0] or 0,
                    'scope2': emissions_row[1] or 0,
                    'scope3': emissions_row[2] or 0,
                    'total': emissions_row[3] or 0,
                    'unit': 'tCO2e'
                }

            # Enerji tüketimi
            cursor.execute("""
                SELECT 
                    SUM(elektrik_tuketimi) as elektrik,
                    SUM(dogalgaz_tuketimi) as dogalgaz,
                    SUM(yenilenebilir_enerji) as yenilenebilir
                FROM energy_data
                WHERE company_id = ? AND yil = ?
            """, (company_id, year))

            energy_row = cursor.fetchone()
            if energy_row:
                data['energy'] = {
                    'electricity': energy_row[0] or 0,
                    'natural_gas': energy_row[1] or 0,
                    'renewable': energy_row[2] or 0,
                    'unit': 'MWh'
                }

            # CDP Climate Change yanıtları
            cursor.execute("""
                SELECT question_id, question_category, response, evidence
                FROM cdp_climate_change
                WHERE company_id = ? AND reporting_year = ?
                ORDER BY question_id
            """, (company_id, year))

            responses = cursor.fetchall()
            data['cdp_responses'] = [{
                'question_id': r[0],
                'category': r[1],
                'response': r[2],
                'evidence': r[3]
            } for r in responses]

            # Hedefler
            cursor.execute("""
                SELECT target_type, target_value, target_year, progress
                FROM sustainability_targets
                WHERE company_id = ? AND target_category = 'Climate'
            """, (company_id,))

            targets = cursor.fetchall()
            data['targets'] = [{
                'type': t[0],
                'value': t[1],
                'year': t[2],
                'progress': t[3]
            } for t in targets]

        finally:
            conn.close()

        return data

    def collect_water_data(self, company_id: int, year: int) -> Dict[str, Any]:
        """Su güvenliği verileri topla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        data = {
            'company_id': company_id,
            'year': year,
            'water_consumption': {},
            'water_discharge': {},
            'water_recycling': {},
            'water_risks': {}
        }

        try:
            # Su tüketimi
            cursor.execute("""
                SELECT 
                    SUM(cekilen_su) as withdrawn,
                    SUM(tuketilen_su) as consumed,
                    SUM(deşarj_edilen_su) as discharged,
                    SUM(geri_donusturulen_su) as recycled
                FROM water_data
                WHERE company_id = ? AND yil = ?
            """, (company_id, year))

            water_row = cursor.fetchone()
            if water_row:
                data['water_consumption'] = {
                    'withdrawn': water_row[0] or 0,
                    'consumed': water_row[1] or 0,
                    'discharged': water_row[2] or 0,
                    'recycled': water_row[3] or 0,
                    'unit': 'm³'
                }

            # CDP Water Security yanıtları
            cursor.execute("""
                SELECT question_id, question_category, response, evidence
                FROM cdp_water_security
                WHERE company_id = ? AND reporting_year = ?
                ORDER BY question_id
            """, (company_id, year))

            responses = cursor.fetchall()
            data['cdp_responses'] = [{
                'question_id': r[0],
                'category': r[1],
                'response': r[2],
                'evidence': r[3]
            } for r in responses]

        finally:
            conn.close()

        return data

    def collect_forests_data(self, company_id: int, year: int) -> Dict[str, Any]:
        """Ormanlar verileri topla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        data = {
            'company_id': company_id,
            'year': year,
            'forest_commodities': {},
            'deforestation_risk': {},
            'forest_management': {}
        }

        try:
            # CDP Forests yanıtları
            cursor.execute("""
                SELECT question_id, question_category, response, evidence
                FROM cdp_forests
                WHERE company_id = ? AND reporting_year = ?
                ORDER BY question_id
            """, (company_id, year))

            responses = cursor.fetchall()
            data['cdp_responses'] = [{
                'question_id': r[0],
                'category': r[1],
                'response': r[2],
                'evidence': r[3]
            } for r in responses]

        finally:
            conn.close()

        return data

    def collect_company_info(self, company_id: int) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        info: Dict[str, Any] = {}
        try:
            cursor.execute(
                "SELECT COALESCE(ticari_unvan, sirket_adi), sektor, 'Türkiye', calisan_sayisi, 0 FROM company_info WHERE company_id = ?",
                (company_id,),
            )
            row = cursor.fetchone()
            if row:
                info = {
                    'name': row[0] or 'Şirket Adı',
                    'sector': row[1] or 'Belirtilmemiş',
                    'country': row[2] or 'Türkiye',
                    'employees': row[3] or 0,
                    'revenue': row[4] or 0
                }
        finally:
            conn.close()
        return info

    def get_previous_year_comparison(self, company_id: int, year: int) -> Dict[str, Any]:
        """Önceki yıl ile karşılaştırma verilerini al"""
        previous_year = year - 1

        current_climate = self.collect_climate_data(company_id, year)
        previous_climate = self.collect_climate_data(company_id, previous_year)

        comparison = {
            'year': year,
            'previous_year': previous_year,
            'emissions_change': {},
            'energy_change': {}
        }

        # Emisyon değişimi
        if current_climate['emissions'] and previous_climate['emissions']:
            current_total = current_climate['emissions'].get('total', 0)
            previous_total = previous_climate['emissions'].get('total', 0)

            if previous_total > 0:
                change_pct = ((current_total - previous_total) / previous_total) * 100
                comparison['emissions_change'] = {
                    'current': current_total,
                    'previous': previous_total,
                    'absolute_change': current_total - previous_total,
                    'percentage_change': round(change_pct, 2)
                }

        return comparison

    def calculate_intensity_metrics(self, company_id: int, year: int) -> Dict[str, float]:
        """Yoğunluk metrikleri hesapla"""
        climate_data = self.collect_climate_data(company_id, year)
        company_info = self.collect_company_info(company_id)

        metrics = {}

        total_emissions = climate_data['emissions'].get('total', 0)
        employees = company_info.get('employees', 0)
        revenue = company_info.get('revenue', 0)

        # Çalışan başına emisyon
        if employees > 0:
            metrics['emissions_per_employee'] = round(total_emissions / employees, 2)

        # Gelir başına emisyon
        if revenue > 0:
            metrics['emissions_per_revenue'] = round(total_emissions / revenue, 2)

        return metrics

