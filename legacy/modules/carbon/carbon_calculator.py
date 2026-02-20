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

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    # ==================== SCOPE 1 HESAPLAMALARI ====================

    def calculate_scope1_stationary(self, fuel_consumptions: List[Dict]) -> Dict:
        """
        Scope 1 - Sabit Yakma Kaynaklarından Emisyonlar
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

    def calculate_scope1_mobile(self, vehicle_data: List[Dict]) -> Dict:
        """
        Scope 1 - Mobil Yakma (Araç Filosu)
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

    # ==================== SCOPE 2 HESAPLAMALARI ====================

    def calculate_scope2_electricity(self, electricity_data: List[Dict],
                                    location_based: bool = True) -> Dict:
        """
        Scope 2 - Satın Alınan Elektrik
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

    # ==================== SCOPE 3 HESAPLAMALARI ====================

    def calculate_scope3_category(self, category: str, data: List[Dict]) -> Dict:
        """
        Scope 3 - Belirli Kategori Hesaplama
        """
        total_co2e = 0.0
        details = []

        category_info = self.emission_factors.SCOPE3_CATEGORIES.get(category)
        if not category_info:
            # Fallback for unknown categories or just return 0 if strictly checked
            # raise ValueError(f"Geçersiz Scope 3 kategori: {category}")
            return {'total_co2e': 0.0, 'details': []}

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
                co2e = quantity * category_info.get('default_factor', 0)

                total_co2e += co2e
                details.append({
                    'quantity': quantity,
                    'co2e': round(co2e, 3)
                })

        return {
            'total_co2e': round(total_co2e, 3),
            'details': details
        }
