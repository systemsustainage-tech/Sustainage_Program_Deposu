#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analiz ve Dashboard
Trend analizi, karşılaştırmalar ve özet göstergeler
"""

import logging
import os
from typing import Dict, List


class Analytics:
    """Analiz ve dashboard metrikleri"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')

    def get_carbon_trend(self, company_id: int, years: List[int]) -> List[Dict]:
        """Karbon emisyon trendi"""
        try:
            from modules.environmental import CarbonCalculator
            calc = CarbonCalculator(self.db_path)

            trend = []
            for year in years:
                summary = calc.get_company_summary(company_id, year)
                trend.append({
                    'year': year,
                    'total': summary['total_ton'],
                    'scope1': summary['scope1_ton'],
                    'scope2': summary['scope2_ton'],
                    'scope3': summary['scope3_ton']
                })

            return trend
        except Exception as e:
            logging.error(f"[HATA] Karbon trend: {e}")
            return []

    def get_energy_trend(self, company_id: int, years: List[int]) -> List[Dict]:
        """Enerji tüketim trendi"""
        try:
            from modules.environmental import EnergyManager
            energy = EnergyManager(self.db_path)

            trend = []
            for year in years:
                summary = energy.get_summary(company_id, year)
                trend.append({
                    'year': year,
                    'total_kwh': summary['total_kwh'],
                    'renewable_percent': summary['renewable_percent']
                })

            return trend
        except Exception as e:
            logging.error(f"[HATA] Enerji trend: {e}")
            return []

    def get_workforce_trend(self, company_id: int, years: List[int]) -> List[Dict]:
        """İş gücü trendi"""
        try:
            from modules.social import HRMetrics
            hr = HRMetrics(self.db_path)

            trend = []
            for year in years:
                workforce = hr.get_workforce_summary(company_id, year)
                diversity = hr.get_diversity_metrics(company_id, year)

                trend.append({
                    'year': year,
                    'total_employees': workforce['total_employees'],
                    'female_percent': diversity.get('female_percent', 0)
                })

            return trend
        except Exception as e:
            logging.error(f"[HATA] Is gucu trend: {e}")
            return []

    def get_dashboard_summary(self, company_id: int, year: int) -> Dict:
        """Özet dashboard metrikleri"""
        summary = {
            'year': year,
            'environmental': {},
            'social': {},
            'economic': {}
        }

        try:
            # Çevresel
            from modules.environmental import CarbonCalculator, EnergyManager, WasteManager, WaterManager

            carbon = CarbonCalculator(self.db_path)
            carbon_data = carbon.get_company_summary(company_id, year)
            summary['environmental']['carbon_ton'] = carbon_data['total_ton']

            energy = EnergyManager(self.db_path)
            energy_data = energy.get_summary(company_id, year)
            summary['environmental']['energy_kwh'] = energy_data['total_kwh']
            summary['environmental']['renewable_percent'] = energy_data['renewable_percent']

            water = WaterManager(self.db_path)
            water_data = water.get_summary(company_id, year)
            summary['environmental']['water_m3'] = water_data['total_m3']

            waste = WasteManager(self.db_path)
            waste_data = waste.get_summary(company_id, year)
            summary['environmental']['waste_ton'] = waste_data['total_ton']
            summary['environmental']['recycle_percent'] = waste_data['recycle_percent']

        except Exception as e:
            logging.info(f"[UYARI] Cevresel veri: {e}")

        try:
            # Sosyal
            from modules.social import HRMetrics, OHSMetrics, TrainingMetrics

            hr = HRMetrics(self.db_path)
            workforce = hr.get_workforce_summary(company_id, year)
            summary['social']['employees'] = workforce['total_employees']

            diversity = hr.get_diversity_metrics(company_id, year)
            summary['social']['female_percent'] = diversity.get('female_percent', 0)

            ohs = OHSMetrics(self.db_path)
            ohs_data = ohs.get_summary(company_id, year)
            summary['social']['ltifr'] = ohs_data['ltifr']

            training = TrainingMetrics(self.db_path)
            training_data = training.get_summary(company_id, year)
            summary['social']['training_hours'] = training_data['avg_hours_per_employee']

        except Exception as e:
            logging.info(f"[UYARI] Sosyal veri: {e}")

        try:
            # Ekonomik
            from modules.economic import EconomicMetrics

            economic = EconomicMetrics(self.db_path)
            economic_data = economic.get_summary(company_id, year)
            summary['economic'] = economic_data

        except Exception as e:
            logging.info(f"[UYARI] Ekonomik veri: {e}")

        return summary

    def compare_years(self, company_id: int, year1: int, year2: int) -> Dict:
        """Yıl karşılaştırması"""
        data1 = self.get_dashboard_summary(company_id, year1)
        data2 = self.get_dashboard_summary(company_id, year2)

        comparison = {
            'year1': year1,
            'year2': year2,
            'changes': {}
        }

        # Karbon değişimi
        if 'carbon_ton' in data1['environmental'] and 'carbon_ton' in data2['environmental']:
            c1 = data1['environmental']['carbon_ton']
            c2 = data2['environmental']['carbon_ton']
            change = ((c2 - c1) / c1 * 100) if c1 > 0 else 0
            comparison['changes']['carbon_percent'] = round(change, 2)

        # Enerji değişimi
        if 'energy_kwh' in data1['environmental'] and 'energy_kwh' in data2['environmental']:
            e1 = data1['environmental']['energy_kwh']
            e2 = data2['environmental']['energy_kwh']
            change = ((e2 - e1) / e1 * 100) if e1 > 0 else 0
            comparison['changes']['energy_percent'] = round(change, 2)

        return comparison

