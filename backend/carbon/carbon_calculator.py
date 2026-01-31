#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
"""
KARBON HESAPLAMA MOTORU
GHG Protocol Scope 1, 2, 3 emisyon hesaplamaları
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List

from .emission_factors import EmissionFactors
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CarbonCalculator:
    """Karbon emisyon hesaplama sınıfı - GHG Protocol uyumlu"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.emission_factors = EmissionFactors(db_path)

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    # ==================== SCOPE 1 HESAPLAMALARI ====================

    def calculate_scope1_stationary(self, fuel_consumptions: List[Dict]) -> Dict:
        """
        Scope 1 - Sabit Yakma Kaynaklarından Emisyonlar
        
        Args:
            fuel_consumptions: [
                {
                    'fuel_type': 'natural_gas',
                    'quantity': 50000,  # m3
                    'period': '2024'
                },
                ...
            ]
        
        Returns:
            {
                'total_co2e': float,
                'breakdown': {...},
                'details': [...]
            }
        """
        total_co2e = 0.0
        breakdown = {}
        details = []

        for consumption in fuel_consumptions:
            fuel_type = consumption['fuel_type']
            quantity = consumption['quantity']

            # Emisyon hesapla
            result = self.emission_factors.calculate_co2e(
                scope='scope1',
                category='stationary',
                fuel_type=fuel_type,
                quantity=quantity
            )

            total_co2e += result['co2e']
            breakdown[fuel_type] = result['co2e']

            details.append({
                'fuel_type': fuel_type,
                'quantity': quantity,
                'unit': result['unit'],
                'co2': result['co2'],
                'ch4': result['ch4'],
                'n2o': result['n2o'],
                'co2e': result['co2e'],
                'source': result['source']
            })

        return {
            'total_co2e': round(total_co2e, 3),
            'breakdown': breakdown,
            'details': details
        }

    # ==================== SCOPE 3 HESAPLAMALARI ====================
    def calculate_scope3_generic(self, scope3_data: List[Dict]) -> Dict:
        """
        Scope 3 - Genel Hesaplama (Satın Alma, Nakliye, Seyahat vb.)
        
        Args:
            scope3_data: [
                {
                    'category': 'transport', # veya purchased_goods, travel
                    'fuel_type': 'road_freight', # air_freight, steel, etc.
                    'quantity': 10000, # tkm, ton, pkm
                    'period': '2024'
                }
            ]
        """
        total_co2e = 0.0
        breakdown = {}
        details = []
        
        for item in scope3_data:
            fuel_type = item['fuel_type']
            quantity = item['quantity']
            
            # Kategori kontrolü - Eğer veri içinde yoksa emisyon faktöründen al
            category = item.get('category', 'generic')

            result = self.emission_factors.calculate_co2e(
                scope='scope3',
                category=category,
                fuel_type=fuel_type,
                quantity=quantity
            )
            
            total_co2e += result['co2e']
            
            # Breakdown'ı faktördeki kategoriye göre yapalım
            factor_info = self.emission_factors.SCOPE3_FACTORS.get(fuel_type)
            cat_name = factor_info['category'] if factor_info else category
            
            breakdown[cat_name] = breakdown.get(cat_name, 0) + result['co2e']
            
            details.append({
                'fuel_type': fuel_type,
                'quantity': quantity,
                'category': cat_name,
                'co2e': result['co2e'],
                'unit': result['unit'],
                'source': result['source']
            })
            
        return {
            'total_co2e': round(total_co2e, 3),
            'breakdown': breakdown,
            'details': details
        }


    def calculate_scope1_mobile(self, vehicle_data: List[Dict]) -> Dict:
        """
        Scope 1 - Mobil Yakma (Araç Filosu)
        
        Args:
            vehicle_data: [
                {
                    'fuel_type': 'gasoline',
                    'quantity': 5000,  # litre
                    'vehicle_count': 10,
                    'period': '2024'
                },
                ...
            ]
        """
        total_co2e = 0.0
        breakdown = {}
        details = []

        for vehicle in vehicle_data:
            fuel_type = vehicle['fuel_type']
            quantity = vehicle['quantity']

            result = self.emission_factors.calculate_co2e(
                scope='scope1',
                category='mobile',
                fuel_type=fuel_type,
                quantity=quantity
            )

            total_co2e += result['co2e']
            breakdown[fuel_type] = breakdown.get(fuel_type, 0) + result['co2e']

            details.append({
                'fuel_type': fuel_type,
                'quantity': quantity,
                'vehicle_count': vehicle.get('vehicle_count', 0),
                'co2e': result['co2e'],
                'unit': result['unit']
            })

        return {
            'total_co2e': round(total_co2e, 3),
            'breakdown': breakdown,
            'details': details
        }

    def calculate_scope1_fugitive(self, refrigerant_data: List[Dict]) -> Dict:
        """
        Scope 1 - Kaçak Emisyonlar (Soğutucu Gazlar)
        
        Args:
            refrigerant_data: [
                {
                    'refrigerant_type': 'r134a',
                    'leakage_kg': 5.2,  # kg
                    'period': '2024'
                },
                ...
            ]
        """
        total_co2e = 0.0
        breakdown = {}
        details = []

        for ref in refrigerant_data:
            ref_type = ref['refrigerant_type']
            leakage = ref['leakage_kg']

            result = self.emission_factors.calculate_co2e(
                scope='scope1',
                category='fugitive',
                fuel_type=ref_type,
                quantity=leakage
            )

            total_co2e += result['co2e']
            breakdown[ref_type] = result['co2e']

            details.append({
                'refrigerant_type': ref_type,
                'leakage_kg': leakage,
                'co2e': result['co2e']
            })

        return {
            'total_co2e': round(total_co2e, 3),
            'breakdown': breakdown,
            'details': details
        }

    def calculate_scope1_total(self, company_id: int, period: str) -> Dict:
        """
        Scope 1 Toplam Emisyon
        
        Tüm Scope 1 kaynaklarını toplar:
        - Sabit yakma
        - Mobil yakma
        - Kaçak emisyonlar
        """
        # Veritabanından tüm Scope 1 verilerini al
        stationary = self.get_scope1_stationary_data(company_id, period)
        mobile = self.get_scope1_mobile_data(company_id, period)
        fugitive = self.get_scope1_fugitive_data(company_id, period)

        # Hesapla
        stationary_result = self.calculate_scope1_stationary(stationary)
        mobile_result = self.calculate_scope1_mobile(mobile)
        fugitive_result = self.calculate_scope1_fugitive(fugitive)

        total = (stationary_result['total_co2e'] +
                mobile_result['total_co2e'] +
                fugitive_result['total_co2e'])

        return {
            'total_co2e': round(total, 3),
            'stationary': stationary_result,
            'mobile': mobile_result,
            'fugitive': fugitive_result
        }

    # ==================== SCOPE 2 HESAPLAMALARI ====================

    def calculate_scope2_electricity(self, electricity_data: List[Dict],
                                    location_based: bool = True) -> Dict:
        """
        Scope 2 - Satın Alınan Elektrik
        
        Args:
            electricity_data: [
                {
                    'grid_type': 'turkey',  # or renewable
                    'quantity_kwh': 100000,
                    'period': '2024'
                },
                ...
            ]
            location_based: True = lokasyon bazlı, False = piyasa bazlı
        """
        total_co2e = 0.0
        breakdown = {}
        details = []

        for elec in electricity_data:
            grid_type = elec['grid_type']
            quantity = elec['quantity_kwh']

            result = self.emission_factors.calculate_co2e(
                scope='scope2',
                category='electricity',
                fuel_type=grid_type,
                quantity=quantity
            )

            total_co2e += result['co2e']
            breakdown[grid_type] = result['co2e']

            details.append({
                'grid_type': grid_type,
                'quantity_kwh': quantity,
                'co2e': result['co2e'],
                'method': 'location_based' if location_based else 'market_based'
            })

        return {
            'total_co2e': round(total_co2e, 3),
            'breakdown': breakdown,
            'details': details,
            'method': 'location_based' if location_based else 'market_based'
        }

    def calculate_scope2_heating(self, heating_data: List[Dict]) -> Dict:
        """
        Scope 2 - Satın Alınan Isıtma/Soğutma
        """
        total_co2e = 0.0
        breakdown = {}
        details = []

        for heat in heating_data:
            heat_type = heat['heat_type']
            quantity = heat['quantity']

            result = self.emission_factors.calculate_co2e(
                scope='scope2',
                category='heating',
                fuel_type=heat_type,
                quantity=quantity
            )

            total_co2e += result['co2e']
            breakdown[heat_type] = result['co2e']

            details.append({
                'heat_type': heat_type,
                'quantity': quantity,
                'unit': result['unit'],
                'co2e': result['co2e']
            })

        return {
            'total_co2e': round(total_co2e, 3),
            'breakdown': breakdown,
            'details': details
        }

    def calculate_scope2_total(self, company_id: int, period: str) -> Dict:
        """Scope 2 Toplam Emisyon"""
        electricity_data = self.get_scope2_electricity_data(company_id, period)
        heating_data = self.get_scope2_heating_data(company_id, period)

        electricity_result = self.calculate_scope2_electricity(electricity_data)
        heating_result = self.calculate_scope2_heating(heating_data)

        total = electricity_result['total_co2e'] + heating_result['total_co2e']

        return {
            'total_co2e': round(total, 3),
            'electricity': electricity_result,
            'heating': heating_result
        }

    # ==================== SCOPE 3 HESAPLAMALARI ====================

    def calculate_scope3_category(self, category: str, data: List[Dict]) -> Dict:
        """
        Scope 3 - Belirli Kategori Hesaplama
        
        Args:
            category: 'business_travel', 'employee_commuting', 'waste', etc.
            data: Kategori özel veri listesi
        """
        total_co2e = 0.0
        details = []

        category_info = self.emission_factors.SCOPE3_CATEGORIES.get(category)
        if not category_info:
            raise ValueError(f"Geçersiz Scope 3 kategori: {category}")

        # Kategori özel hesaplama
        if category == 'business_travel':
            for trip in data:
                if 'spend_usd' in trip:
                    spend = trip.get('spend_usd', 0)
                    sf = category_info.get('spend_factor_usd', 0)
                    co2e = spend * sf
                    total_co2e += co2e
                    details.append({
                        'method': 'spend_based',
                        'spend_usd': spend,
                        'co2e': round(co2e, 3)
                    })
                else:
                    travel_type = trip.get('travel_type', 'flight_medium')
                    distance = trip.get('distance_km', 0)
                    factor = category_info['factors'].get(travel_type, 0)
                    co2e = distance * factor
                    total_co2e += co2e
                    details.append({
                        'method': 'distance_based',
                        'travel_type': travel_type,
                        'distance_km': distance,
                        'co2e': round(co2e, 3)
                    })

        elif category == 'employee_commuting':
            for commute in data:
                transport_mode = commute.get('transport_mode', 'car_gasoline')
                total_distance = commute.get('total_distance_km', 0)

                factor = category_info['factors'].get(transport_mode, 0)
                co2e = total_distance * factor

                total_co2e += co2e
                details.append({
                    'transport_mode': transport_mode,
                    'total_distance_km': total_distance,
                    'co2e': round(co2e, 3)
                })

        elif category == 'waste':
            for waste_item in data:
                waste_type = waste_item.get('waste_type', 'landfill')
                quantity_ton = waste_item.get('quantity_ton', 0)

                factor = category_info['factors'].get(waste_type, 0)
                co2e = quantity_ton * factor

                total_co2e += co2e
                details.append({
                    'waste_type': waste_type,
                    'quantity_ton': quantity_ton,
                    'co2e': round(co2e, 3)
                })

        else:
            # Genel hesaplama (basit faktör)
            for item in data:
                quantity = item.get('quantity', 0)
                co2e = quantity * category_info.get('factor', 0)

                total_co2e += co2e
                details.append({
                    'quantity': quantity,
                    'co2e': round(co2e, 3)
                })

        return {
            'category': category,
            'category_name': category_info['name'],
            'total_co2e': round(total_co2e, 3),
            'details': details,
            'calculation_method': category_info.get('calculation_method', 'standard_factor')
        }

    def calculate_scope3_total(self, company_id: int, period: str,
                              selected_categories: List[str] = None) -> Dict:
        """
        Scope 3 Toplam Emisyon (Seçilen Kategoriler)
        
        Args:
            selected_categories: None ise tüm kategoriler, yoksa seçilen kategoriler
        """
        if selected_categories is None:
            selected_categories = list(self.emission_factors.SCOPE3_CATEGORIES.keys())

        total_co2e = 0.0
        category_results = {}

        for category in selected_categories:
            # Veritabanından kategori verilerini al
            category_data = self.get_scope3_category_data(company_id, period, category)

            if category_data:
                result = self.calculate_scope3_category(category, category_data)
                total_co2e += result['total_co2e']
                category_results[category] = result

        return {
            'total_co2e': round(total_co2e, 3),
            'categories': category_results,
            'selected_count': len(selected_categories),
            'total_categories': 15  # GHG Protocol Scope 3 standart
        }

    # ==================== TOPLAM HESAPLAMA ====================

    def calculate_total_footprint(self, company_id: int, period: str,
                                 include_scope3: bool = False) -> Dict:
        """
        Toplam Karbon Ayak İzi
        
        Args:
            company_id: Şirket ID
            period: Raporlama dönemi
            include_scope3: Scope 3 dahil edilsin mi?
        
        Returns:
            {
                'scope1_total': float,
                'scope2_total': float,
                'scope3_total': float (opsiyonel),
                'total_co2e': float,
                'breakdown': {...}
            }
        """
        # Scope 1
        scope1_result = self.calculate_scope1_total(company_id, period)

        # Scope 2
        scope2_result = self.calculate_scope2_total(company_id, period)

        # Toplam (Scope 1 + 2)
        total = scope1_result['total_co2e'] + scope2_result['total_co2e']

        result = {
            'company_id': company_id,
            'period': period,
            'scope1_total': scope1_result['total_co2e'],
            'scope2_total': scope2_result['total_co2e'],
            'scope1_2_total': round(total, 3),
            'scope1_breakdown': scope1_result,
            'scope2_breakdown': scope2_result,
            'calculated_at': datetime.now().isoformat()
        }

        # Scope 3 (opsiyonel)
        if include_scope3:
            scope3_result = self.calculate_scope3_total(company_id, period)
            result['scope3_total'] = scope3_result['total_co2e']
            result['scope3_breakdown'] = scope3_result
            result['total_co2e'] = round(total + scope3_result['total_co2e'], 3)
        else:
            result['total_co2e'] = result['scope1_2_total']

        return result

    # ==================== HEDEF VE AZALTMA ====================

    def calculate_reduction_percentage(self, baseline_co2e: float,
                                      current_co2e: float) -> float:
        """
        Emisyon azaltma yüzdesi hesapla
        
        Returns:
            Pozitif değer = azalma, Negatif değer = artış
        """
        if baseline_co2e == 0:
            return 0.0

        reduction = ((baseline_co2e - current_co2e) / baseline_co2e) * 100
        return round(reduction, 2)

    def calculate_target_progress(self, baseline_co2e: float,
                                 current_co2e: float,
                                 target_co2e: float) -> Dict:
        """
        Hedef ilerleme hesapla
        
        Returns:
            {
                'target_reduction_pct': float,
                'achieved_reduction_pct': float,
                'progress_pct': float,
                'on_track': bool
            }
        """
        target_reduction = self.calculate_reduction_percentage(baseline_co2e, target_co2e)
        achieved_reduction = self.calculate_reduction_percentage(baseline_co2e, current_co2e)

        progress = (achieved_reduction / target_reduction * 100) if target_reduction != 0 else 0

        return {
            'baseline_co2e': baseline_co2e,
            'current_co2e': current_co2e,
            'target_co2e': target_co2e,
            'target_reduction_pct': target_reduction,
            'achieved_reduction_pct': achieved_reduction,
            'progress_pct': round(progress, 1),
            'on_track': progress >= 100,
            'remaining_co2e': round(current_co2e - target_co2e, 3)
        }

    def calculate_intensity_metrics(self, total_co2e: float,
                                   revenue: float = None,
                                   employees: int = None,
                                   production: float = None) -> Dict:
        """
        Emisyon yoğunluk metrikleri hesapla
        
        Returns:
            {
                'co2e_per_revenue': float,      # tCO2e / $1M revenue
                'co2e_per_employee': float,     # tCO2e / employee
                'co2e_per_unit': float          # tCO2e / production unit
            }
        """
        metrics = {}

        if revenue:
            metrics['co2e_per_million_revenue'] = round(total_co2e / (revenue / 1000000), 3)

        if employees:
            metrics['co2e_per_employee'] = round(total_co2e / employees, 3)

        if production:
            metrics['co2e_per_production_unit'] = round(total_co2e / production, 3)

        return metrics

    # ==================== VERİTABANI YARDIMCI METODLAR ====================

    def get_scope1_stationary_data(self, company_id: int, period: str) -> List[Dict]:
        """Scope 1 sabit yakma verilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT fuel_type, SUM(quantity) as total_quantity
                FROM carbon_emissions
                WHERE company_id = ? AND period = ? AND scope = 'scope1' AND category = 'stationary'
                GROUP BY fuel_type
            """, (company_id, period))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'fuel_type': row[0],
                    'quantity': row[1],
                    'period': period
                })

            return results

        except Exception as e:
            logging.error(f"Scope 1 stationary veri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_scope1_mobile_data(self, company_id: int, period: str) -> List[Dict]:
        """Scope 1 mobil yakma verilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT fuel_type, SUM(quantity) as total_quantity, 
                       COUNT(DISTINCT source) as vehicle_count
                FROM carbon_emissions
                WHERE company_id = ? AND period = ? AND scope = 'scope1' AND category = 'mobile'
                GROUP BY fuel_type
            """, (company_id, period))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'fuel_type': row[0],
                    'quantity': row[1],
                    'vehicle_count': row[2],
                    'period': period
                })

            return results

        except Exception as e:
            logging.error(f"Scope 1 mobile veri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_scope1_fugitive_data(self, company_id: int, period: str) -> List[Dict]:
        """Scope 1 kaçak emisyon verilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT fuel_type as refrigerant_type, SUM(quantity) as leakage_kg
                FROM carbon_emissions
                WHERE company_id = ? AND period = ? AND scope = 'scope1' AND category = 'fugitive'
                GROUP BY fuel_type
            """, (company_id, period))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'refrigerant_type': row[0],
                    'leakage_kg': row[1],
                    'period': period
                })

            return results

        except Exception as e:
            logging.error(f"Scope 1 fugitive veri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_scope2_electricity_data(self, company_id: int, period: str) -> List[Dict]:
        """Scope 2 elektrik verilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT fuel_type as grid_type, SUM(quantity) as quantity_kwh
                FROM carbon_emissions
                WHERE company_id = ? AND period = ? AND scope = 'scope2' AND category = 'electricity'
                GROUP BY fuel_type
            """, (company_id, period))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'grid_type': row[0],
                    'quantity_kwh': row[1],
                    'period': period
                })

            return results

        except Exception as e:
            logging.error(f"Scope 2 electricity veri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_scope2_heating_data(self, company_id: int, period: str) -> List[Dict]:
        """Scope 2 ısıtma verilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT fuel_type as heat_type, SUM(quantity) as quantity
                FROM carbon_emissions
                WHERE company_id = ? AND period = ? AND scope = 'scope2' AND category = 'heating'
                GROUP BY fuel_type
            """, (company_id, period))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'heat_type': row[0],
                    'quantity': row[1],
                    'period': period
                })

            return results

        except Exception as e:
            logging.error(f"Scope 2 heating veri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_scope3_category_data(self, company_id: int, period: str,
                                 category: str) -> List[Dict]:
        """Scope 3 kategori verilerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT data_json
                FROM carbon_emissions
                WHERE company_id = ? AND period = ? AND scope = 'scope3' AND category = ?
            """, (company_id, period, category))

            results = []
            for row in cursor.fetchall():
                if row[0]:
                    try:
                        data = json.loads(row[0])
                        results.append(data)
                    except Exception as e:
                        logging.error(f'Silent error in carbon_calculator.py: {str(e)}')

            return results

        except Exception as e:
            logging.error(f"Scope 3 kategori veri getirme hatası: {e}")
            return []
        finally:
            conn.close()
