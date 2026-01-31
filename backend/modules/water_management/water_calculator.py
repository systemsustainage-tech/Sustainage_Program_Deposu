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
from config.database import DB_PATH


class WaterCalculator:
    """Su hesaplama sınıfı - ISO 14046 ve WFN standartlarına uygun"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.water_factors = WaterFactors(db_path)

    def calculate_blue_water_consumption(self, consumption_data: List[Dict]) -> Dict:
        """
        Mavi su tüketimi hesapla (yüzey ve yer altı suyu)
        
        Args:
            consumption_data: [{
                'water_source': 'groundwater',
                'quantity': 1000,
                'unit': 'm3',
                'location': 'Plant A',
                'process': 'cooling'
            }]
        
        Returns:
            {
                'total_blue_water': 1000,
                'breakdown': {...},
                'details': [...]
            }
        """
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
        """
        Yeşil su tüketimi hesapla (yağmur suyu)
        
        Args:
            consumption_data: [{
                'water_source': 'rainwater',
                'quantity': 500,
                'unit': 'm3',
                'crop_type': 'wheat',
                'location': 'Agricultural Area'
            }]
        
        Returns:
            {
                'total_green_water': 500,
                'breakdown': {...},
                'details': [...]
            }
        """
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
        """
        Gri su tüketimi hesapla (kirlenmiş su)
        
        Args:
            pollution_data: [{
                'pollutant': 'BOD',
                'concentration': 50,
                'unit': 'mg/L',
                'flow_rate': 100,
                'flow_unit': 'm3/day',
                'natural_background': 2,
                'max_acceptable': 30
            }]
        
        Returns:
            {
                'total_grey_water': 160,
                'breakdown': {...},
                'details': [...]
            }
        """
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

    def calculate_water_intensity(self, total_water: float, production_data: Dict) -> Dict:
        """
        Su yoğunluğu hesapla
        
        Args:
            total_water: Toplam su tüketimi (m³)
            production_data: {
                'product_quantity': 1000,
                'product_unit': 'ton',
                'product_type': 'steel'
            }
        
        Returns:
            {
                'water_intensity': 2.5,  # m³/ton
                'product_quantity': 1000,
                'product_unit': 'ton',
                'product_type': 'steel'
            }
        """
        product_quantity = production_data.get('product_quantity', 1)
        product_unit = production_data.get('product_unit', 'unit')
        product_type = production_data.get('product_type', 'product')

        if product_quantity > 0:
            water_intensity = total_water / product_quantity
        else:
            water_intensity = 0

        return {
            'water_intensity': round(water_intensity, 3),
            'product_quantity': product_quantity,
            'product_unit': product_unit,
            'product_type': product_type,
            'total_water': total_water
        }

    def calculate_recycling_rate(self, total_consumption: float, recycled_water: float) -> Dict:
        """
        Geri dönüşüm oranı hesapla
        
        Args:
            total_consumption: Toplam su tüketimi (m³)
            recycled_water: Geri dönüştürülen su (m³)
        
        Returns:
            {
                'recycling_rate': 0.25,  # %25
                'recycled_water': 250,
                'total_consumption': 1000,
                'fresh_water_need': 750
            }
        """
        if total_consumption > 0:
            recycling_rate = recycled_water / total_consumption
        else:
            recycling_rate = 0

        fresh_water_need = total_consumption - recycled_water

        return {
            'recycling_rate': round(recycling_rate, 3),
            'recycled_water': recycled_water,
            'total_consumption': total_consumption,
            'fresh_water_need': round(fresh_water_need, 2)
        }

    def calculate_efficiency_ratio(self, actual_consumption: float, standard_consumption: float) -> Dict:
        """
        Su verimlilik oranı hesapla
        
        Args:
            actual_consumption: Gerçek tüketim (m³)
            standard_consumption: Standart/beklenen tüketim (m³)
        
        Returns:
            {
                'efficiency_ratio': 0.8,  # %80 verimlilik
                'actual_consumption': 800,
                'standard_consumption': 1000,
                'savings': 200,
                'efficiency_percentage': 80.0
            }
        """
        if standard_consumption > 0:
            efficiency_ratio = actual_consumption / standard_consumption
        else:
            efficiency_ratio = 1

        savings = standard_consumption - actual_consumption
        efficiency_percentage = (1 - efficiency_ratio) * 100

        return {
            'efficiency_ratio': round(efficiency_ratio, 3),
            'actual_consumption': actual_consumption,
            'standard_consumption': standard_consumption,
            'savings': round(savings, 2),
            'efficiency_percentage': round(efficiency_percentage, 1)
        }

    def calculate_water_stress_level(self, water_consumption: float, available_water: float,
                                   water_source: str = None) -> Dict:
        """
        Su stresi seviyesi hesapla
        
        Args:
            water_consumption: Su tüketimi (m³)
            available_water: Mevcut su miktarı (m³)
            water_source: Su kaynağı türü
        
        Returns:
            {
                'stress_level': 'medium',
                'stress_ratio': 0.6,
                'consumption': 600,
                'available': 1000,
                'remaining': 400
            }
        """
        if available_water > 0:
            stress_ratio = water_consumption / available_water
        else:
            stress_ratio = 1

        remaining_water = available_water - water_consumption

        # Stres seviyesi belirleme
        if stress_ratio <= 0.3:
            stress_level = 'low'
        elif stress_ratio <= 0.7:
            stress_level = 'medium'
        elif stress_ratio <= 0.9:
            stress_level = 'high'
        else:
            stress_level = 'critical'

        return {
            'stress_level': stress_level,
            'stress_ratio': round(stress_ratio, 3),
            'consumption': water_consumption,
            'available': available_water,
            'remaining': round(remaining_water, 2),
            'water_source': water_source
        }

    def calculate_sdg_6_progress(self, water_data: Dict) -> Dict:
        """
        SDG 6 ilerleme skoru hesapla
        
        Args:
            water_data: {
                'access_to_drinking_water': 95,  # %
                'access_to_sanitation': 90,      # %
                'water_quality': 85,             # %
                'water_efficiency': 80,          # %
                'water_governance': 75           # %
            }
        
        Returns:
            {
                'sdg_6_score': 85.0,
                'target_2030': 100.0,
                'progress_percentage': 85.0,
                'component_scores': {...}
            }
        """
        # SDG 6 alt hedefleri ve ağırlıkları
        sdg_6_components = {
            'access_to_drinking_water': 0.25,    # SDG 6.1
            'access_to_sanitation': 0.25,        # SDG 6.2
            'water_quality': 0.20,               # SDG 6.3
            'water_efficiency': 0.15,            # SDG 6.4
            'water_governance': 0.15             # SDG 6.5
        }

        total_score = 0.0
        component_scores = {}

        for component, weight in sdg_6_components.items():
            score = water_data.get(component, 0)
            component_scores[component] = score
            total_score += score * weight

        target_2030 = 100.0
        progress_percentage = (total_score / target_2030) * 100

        return {
            'sdg_6_score': round(total_score, 1),
            'target_2030': target_2030,
            'progress_percentage': round(progress_percentage, 1),
            'component_scores': component_scores,
            'calculated_at': datetime.now().isoformat()
        }

    def calculate_water_quality_index(self, quality_measurements: List[Dict]) -> Dict:
        """
        Su kalite indeksi hesapla
        
        Args:
            quality_measurements: [{
                'parameter': 'pH',
                'value': 7.2,
                'unit': 'pH',
                'standard': 6.5,
                'weight': 0.3
            }]
        
        Returns:
            {
                'water_quality_index': 85.5,
                'quality_category': 'good',
                'parameter_scores': {...},
                'compliance_rate': 0.8
            }
        """
        total_weighted_score = 0.0
        total_weight = 0.0
        parameter_scores = {}
        compliant_parameters = 0

        for measurement in quality_measurements:
            parameter = measurement['parameter']
            value = measurement['value']
            standard = measurement['standard']
            weight = measurement.get('weight', 1.0)

            # Kalite skoru hesapla (0-100)
            if value <= standard:
                score = 100.0
                compliant_parameters += 1
            else:
                # Standart değeri aşan durumda azalan skor
                excess_ratio = (value - standard) / standard
                if excess_ratio <= 0.1:  # %10 aşım
                    score = 90.0
                elif excess_ratio <= 0.5:  # %50 aşım
                    score = 70.0
                elif excess_ratio <= 1.0:  # %100 aşım
                    score = 50.0
                else:
                    score = 25.0

            parameter_scores[parameter] = score
            total_weighted_score += score * weight
            total_weight += weight

        if total_weight > 0:
            water_quality_index = total_weighted_score / total_weight
        else:
            water_quality_index = 0

        # Kalite kategorisi belirleme
        if water_quality_index >= 90:
            quality_category = 'excellent'
        elif water_quality_index >= 80:
            quality_category = 'good'
        elif water_quality_index >= 70:
            quality_category = 'fair'
        elif water_quality_index >= 60:
            quality_category = 'poor'
        else:
            quality_category = 'very_poor'

        compliance_rate = compliant_parameters / len(quality_measurements) if quality_measurements else 0

        return {
            'water_quality_index': round(water_quality_index, 1),
            'quality_category': quality_category,
            'parameter_scores': parameter_scores,
            'compliance_rate': round(compliance_rate, 3),
            'total_parameters': len(quality_measurements),
            'compliant_parameters': compliant_parameters
        }

    def calculate_water_trend(self, consumption_data: List[Dict], years: List[str]) -> Dict:
        """
        Su tüketimi trend analizi
        
        Args:
            consumption_data: Yıllık tüketim verileri
            years: Analiz edilecek yıllar
        
        Returns:
            {
                'trend_direction': 'decreasing',
                'trend_percentage': -5.2,
                'annual_changes': {...},
                'projected_next_year': 950
            }
        """
        if len(consumption_data) < 2:
            return {
                'trend_direction': 'insufficient_data',
                'trend_percentage': 0,
                'annual_changes': {},
                'projected_next_year': 0
            }

        # Yıllık değişim hesaplama
        annual_changes = {}
        total_change = 0

        for i in range(1, len(consumption_data)):
            current_year = years[i]
            years[i-1]

            current_consumption = consumption_data[i].get('total_consumption', 0)
            previous_consumption = consumption_data[i-1].get('total_consumption', 0)

            if previous_consumption > 0:
                change_percentage = ((current_consumption - previous_consumption) / previous_consumption) * 100
            else:
                change_percentage = 0

            annual_changes[current_year] = round(change_percentage, 1)
            total_change += change_percentage

        # Ortalama trend
        avg_change = total_change / (len(consumption_data) - 1)

        # Trend yönü
        if avg_change > 2:
            trend_direction = 'increasing'
        elif avg_change < -2:
            trend_direction = 'decreasing'
        else:
            trend_direction = 'stable'

        # Gelecek yıl projeksiyonu
        last_consumption = consumption_data[-1].get('total_consumption', 0)
        projected_next_year = last_consumption * (1 + avg_change / 100)

        return {
            'trend_direction': trend_direction,
            'trend_percentage': round(avg_change, 1),
            'annual_changes': annual_changes,
            'projected_next_year': round(projected_next_year, 2),
            'data_years': years,
            'data_points': len(consumption_data)
        }
