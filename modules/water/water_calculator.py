#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SU HESAPLAMA SINIFI
Su ayak izi, verimlilik ve kalite hesaplamaları
"""

import os
from datetime import datetime
from typing import Dict, List

from .water_factors import WaterFactors

class WaterCalculator:
    """Su hesaplama sınıfı - ISO 14046 ve WFN standartlarına uygun"""

    def __init__(self, db_path: str = None) -> None:
        if db_path is None:
             # Default to sustainage.db in project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, 'sustainage.db')
        self.db_path = db_path
        self.water_factors = WaterFactors(db_path)

    def calculate_blue_water_consumption(self, consumption_data: List[Dict]) -> Dict:
        """Mavi su tüketimi hesapla"""
        total_blue_water = 0.0
        breakdown = {}
        details = []

        for data in consumption_data:
            water_source = data['water_source']
            quantity = data['quantity']

            # Mavi su faktörü (genellikle 1:1, ancak kaynak türüne göre değişebilir)
            blue_water_factor = self.water_factors.get_blue_water_factor(water_source)
            blue_water = quantity * blue_water_factor

            total_blue_water += blue_water

            # Dağılım
            if water_source not in breakdown:
                breakdown[water_source] = 0
            breakdown[water_source] += blue_water

            # Detay
            details.append({
                'water_source': water_source,
                'quantity': quantity,
                'unit': data.get('unit', 'm3'),
                'blue_water_factor': blue_water_factor,
                'blue_water': blue_water,
                'location': data.get('location', ''),
                'process': data.get('process', '')
            })

        return {
            'total_blue_water': round(total_blue_water, 2),
            'breakdown': breakdown,
            'details': details
        }

    def calculate_green_water_consumption(self, consumption_data: List[Dict]) -> Dict:
        """Yeşil su tüketimi hesapla"""
        total_green_water = 0.0
        breakdown = {}
        details = []

        for data in consumption_data:
            water_source = data['water_source']
            quantity = data['quantity']

            # Yeşil su faktörü (yağmur suyu için genellikle 1:1)
            green_water_factor = self.water_factors.get_green_water_factor(water_source)
            green_water = quantity * green_water_factor

            total_green_water += green_water

            # Dağılım
            if water_source not in breakdown:
                breakdown[water_source] = 0
            breakdown[water_source] += green_water

            # Detay
            details.append({
                'water_source': water_source,
                'quantity': quantity,
                'unit': data.get('unit', 'm3'),
                'green_water_factor': green_water_factor,
                'green_water': green_water,
                'crop_type': data.get('crop_type', ''),
                'location': data.get('location', '')
            })

        return {
            'total_green_water': round(total_green_water, 2),
            'breakdown': breakdown,
            'details': details
        }

    def calculate_grey_water_consumption(self, pollution_data: List[Dict]) -> Dict:
        """Gri su tüketimi hesapla"""
        total_grey_water = 0.0
        breakdown = {}
        details = []

        for data in pollution_data:
            pollutant = data['pollutant']
            concentration = data['concentration']
            flow_rate = data['flow_rate']
            natural_background = data.get('natural_background', 0)
            max_acceptable = data.get('max_acceptable', 0)

            # Gri su hesaplama: (Emisyon - Doğal Arkaplan) / (Maksimum Kabul Edilebilir - Doğal Arkaplan)
            if max_acceptable > natural_background:
                dilution_factor = (concentration - natural_background) / (max_acceptable - natural_background)
                grey_water = flow_rate * dilution_factor
            else:
                grey_water = 0

            total_grey_water += grey_water

            # Dağılım
            if pollutant not in breakdown:
                breakdown[pollutant] = 0
            breakdown[pollutant] += grey_water

            # Detay
            details.append({
                'pollutant': pollutant,
                'concentration': concentration,
                'unit': data.get('unit', 'mg/L'),
                'flow_rate': flow_rate,
                'flow_unit': data.get('flow_unit', 'm3/day'),
                'natural_background': natural_background,
                'max_acceptable': max_acceptable,
                'dilution_factor': round(dilution_factor, 3),
                'grey_water': round(grey_water, 2)
            })

        return {
            'total_grey_water': round(total_grey_water, 2),
            'breakdown': breakdown,
            'details': details
        }
