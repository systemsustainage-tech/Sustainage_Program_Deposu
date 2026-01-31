#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATIK HESAPLAMA MOTORU
Atık azaltma, geri dönüşüm ve döngüsel ekonomi hesaplamaları
"""

import logging
from typing import Dict, List


class WasteCalculator:
    """Atık Hesaplama Motoru"""

    def __init__(self) -> None:
        self.waste_factors = {
            # Organik atık faktörleri (kg CO2e/kg)
            'organic_composting': 0.15,  # Kompostlama
            'organic_landfill': 0.45,   # Depolama
            'organic_incineration': 0.35, # Yakma
            'organic_biogas': -0.20,     # Biyogaz (negatif = azaltma)

            # Plastik atık faktörleri
            'plastic_recycling': -0.80,  # Geri dönüşüm (negatif = azaltma)
            'plastic_landfill': 0.15,    # Depolama
            'plastic_incineration': 0.25, # Yakma

            # Metal atık faktörleri
            'metal_recycling': -1.50,    # Geri dönüşüm (negatif = azaltma)
            'metal_landfill': 0.05,      # Depolama

            # Kağıt atık faktörleri
            'paper_recycling': -0.60,    # Geri dönüşüm (negatif = azaltma)
            'paper_landfill': 0.20,      # Depolama
            'paper_incineration': 0.30,  # Yakma

            # Cam atık faktörleri
            'glass_recycling': -0.40,    # Geri dönüşüm (negatif = azaltma)
            'glass_landfill': 0.05,      # Depolama

            # Elektronik atık faktörleri
            'ewaste_recycling': -2.00,   # Geri dönüşüm (negatif = azaltma)
            'ewaste_landfill': 0.80,     # Depolama

            # Tehlikeli atık faktörleri
            'hazardous_treatment': 0.60, # Özel işlem
            'hazardous_landfill': 1.20,  # Özel depolama

            # İnşaat atık faktörleri
            'construction_recycling': -0.30, # Geri dönüşüm (negatif = azaltma)
            'construction_landfill': 0.10,   # Depolama
        }

        # Atık azaltma potansiyeli (0-100%)
        self.reduction_potential = {
            'Organik': 80,      # Yüksek azaltma potansiyeli
            'Geri Dönüşüm': 70, # Orta-yüksek azaltma potansiyeli
            'Tehlikeli': 30,    # Düşük azaltma potansiyeli
            'İnşaat': 60,       # Orta azaltma potansiyeli
            'Tekstil': 50,      # Orta azaltma potansiyeli
            'Tıbbi': 20,        # Düşük azaltma potansiyeli
            'Genel': 40         # Düşük-orta azaltma potansiyeli
        }

        # Geri dönüşüm maliyeti (TL/kg)
        self.recycling_costs = {
            'Organik': 0.50,    # Kompostlama maliyeti
            'Geri Dönüşüm': 1.20, # Geri dönüşüm maliyeti
            'Tehlikeli': 5.00,  # Özel işlem maliyeti
            'İnşaat': 0.80,     # İnşaat geri dönüşüm maliyeti
            'Tekstil': 2.50,    # Tekstil geri dönüşüm maliyeti
            'Tıbbi': 8.00,      # Tıbbi atık işlem maliyeti
            'Genel': 1.50       # Genel atık işlem maliyeti
        }

    def calculate_carbon_footprint(self, waste_data: List[Dict]) -> Dict:
        """Atık karbon ayak izini hesapla"""
        try:
            total_carbon = 0.0
            category_carbon = {}

            for waste in waste_data:
                quantity = waste.get('quantity', 0)
                unit = waste.get('unit', 'kg')
                category = waste.get('waste_category', 'Genel')
                disposal_method = waste.get('disposal_method', 'Depolama')
                recycling_rate = waste.get('recycling_rate', 0) / 100

                # Birimi kg'ye çevir
                quantity_kg = self._convert_to_kg(quantity, unit)

                # Geri dönüşüm oranına göre hesapla
                recycled_quantity = quantity_kg * recycling_rate
                disposed_quantity = quantity_kg * (1 - recycling_rate)

                # Karbon faktörlerini belirle
                recycling_factor = self.waste_factors.get(f"{category.lower()}_recycling", 0)
                disposal_factor = self.waste_factors.get(f"{category.lower()}_{disposal_method.lower()}", 0)

                # Karbon hesaplama
                recycled_carbon = recycled_quantity * recycling_factor
                disposed_carbon = disposed_quantity * disposal_factor
                waste_carbon = recycled_carbon + disposed_carbon

                total_carbon += waste_carbon

                if category not in category_carbon:
                    category_carbon[category] = 0.0
                category_carbon[category] += waste_carbon

            return {
                'total_carbon_footprint': round(total_carbon, 2),
                'category_carbon': {k: round(v, 2) for k, v in category_carbon.items()},
                'unit': 'kg CO2e'
            }

        except Exception as e:
            logging.error(f"[HATA] Karbon ayak izi hesaplanirken hata: {e}")
            return {'total_carbon_footprint': 0.0, 'category_carbon': {}, 'unit': 'kg CO2e'}

    def calculate_waste_reduction_potential(self, waste_data: List[Dict]) -> Dict:
        """Atık azaltma potansiyelini hesapla"""
        try:
            total_waste = 0.0
            category_potential = {}

            for waste in waste_data:
                quantity = waste.get('quantity', 0)
                unit = waste.get('unit', 'kg')
                category = waste.get('waste_category', 'Genel')

                quantity_kg = self._convert_to_kg(quantity, unit)
                total_waste += quantity_kg

                if category not in category_potential:
                    category_potential[category] = {
                        'quantity': 0.0,
                        'potential': 0.0,
                        'reduction_amount': 0.0
                    }

                category_potential[category]['quantity'] += quantity_kg
                potential = self.reduction_potential.get(category, 40)
                category_potential[category]['potential'] = potential
                category_potential[category]['reduction_amount'] += quantity_kg * (potential / 100)

            # Toplam azaltma potansiyeli
            total_reduction_potential = sum(cat['reduction_amount'] for cat in category_potential.values())
            overall_potential = (total_reduction_potential / total_waste * 100) if total_waste > 0 else 0.0

            return {
                'total_waste': round(total_waste, 2),
                'total_reduction_potential': round(total_reduction_potential, 2),
                'overall_potential_percentage': round(overall_potential, 2),
                'category_potential': {
                    k: {
                        'quantity': round(v['quantity'], 2),
                        'potential_percentage': v['potential'],
                        'reduction_amount': round(v['reduction_amount'], 2)
                    }
                    for k, v in category_potential.items()
                }
            }

        except Exception as e:
            logging.error(f"[HATA] Atik azaltma potansiyeli hesaplanirken hata: {e}")
            return {}

    def calculate_recycling_economics(self, waste_data: List[Dict]) -> Dict:
        """Geri dönüşüm ekonomisini hesapla"""
        try:
            total_cost = 0.0
            total_savings = 0.0
            category_economics = {}

            for waste in waste_data:
                quantity = waste.get('quantity', 0)
                unit = waste.get('unit', 'kg')
                category = waste.get('waste_category', 'Genel')
                recycling_rate = waste.get('recycling_rate', 0) / 100
                disposal_cost = waste.get('disposal_cost', 0)

                quantity_kg = self._convert_to_kg(quantity, unit)
                recycled_quantity = quantity_kg * recycling_rate

                # Geri dönüşüm maliyeti
                recycling_cost_per_kg = self.recycling_costs.get(category, 1.50)
                recycling_cost = recycled_quantity * recycling_cost_per_kg

                # Bertaraf maliyeti (ger letilmiş)
                disposal_cost_per_kg = disposal_cost / quantity_kg if quantity_kg > 0 else 0
                avoided_disposal_cost = recycled_quantity * disposal_cost_per_kg

                # Net maliyet/kazanç
                net_cost = recycling_cost - avoided_disposal_cost

                total_cost += recycling_cost
                total_savings += avoided_disposal_cost

                if category not in category_economics:
                    category_economics[category] = {
                        'recycling_cost': 0.0,
                        'avoided_disposal_cost': 0.0,
                        'net_cost': 0.0,
                        'quantity': 0.0
                    }

                category_economics[category]['recycling_cost'] += recycling_cost
                category_economics[category]['avoided_disposal_cost'] += avoided_disposal_cost
                category_economics[category]['net_cost'] += net_cost
                category_economics[category]['quantity'] += recycled_quantity

            net_economic_impact = total_savings - total_cost

            return {
                'total_recycling_cost': round(total_cost, 2),
                'total_avoided_disposal_cost': round(total_savings, 2),
                'net_economic_impact': round(net_economic_impact, 2),
                'roi_percentage': round((net_economic_impact / total_cost * 100) if total_cost > 0 else 0, 2),
                'category_economics': {
                    k: {
                        'recycling_cost': round(v['recycling_cost'], 2),
                        'avoided_disposal_cost': round(v['avoided_disposal_cost'], 2),
                        'net_cost': round(v['net_cost'], 2),
                        'quantity': round(v['quantity'], 2)
                    }
                    for k, v in category_economics.items()
                }
            }

        except Exception as e:
            logging.error(f"[HATA] Geri donusum ekonomisi hesaplanirken hata: {e}")
            return {}

    def calculate_circular_economy_index(self, waste_data: List[Dict]) -> Dict:
        """Döngüsel ekonomi indeksini hesapla"""
        try:
            total_waste = 0.0
            total_recycled = 0.0
            total_reused = 0.0
            total_reduced = 0.0

            category_scores = {}

            for waste in waste_data:
                quantity = waste.get('quantity', 0)
                unit = waste.get('unit', 'kg')
                category = waste.get('waste_category', 'Genel')
                recycling_rate = waste.get('recycling_rate', 0) / 100

                quantity_kg = self._convert_to_kg(quantity, unit)
                total_waste += quantity_kg

                recycled_quantity = quantity_kg * recycling_rate
                total_recycled += recycled_quantity

                # Yeniden kullanım oranı (varsayılan %10)
                reuse_rate = 0.10
                reused_quantity = quantity_kg * reuse_rate
                total_reused += reused_quantity

                # Azaltma oranı (varsayılan %5)
                reduction_rate = 0.05
                reduced_quantity = quantity_kg * reduction_rate
                total_reduced += reduced_quantity

                if category not in category_scores:
                    category_scores[category] = {
                        'quantity': 0.0,
                        'recycled': 0.0,
                        'reused': 0.0,
                        'reduced': 0.0,
                        'score': 0.0
                    }

                category_scores[category]['quantity'] += quantity_kg
                category_scores[category]['recycled'] += recycled_quantity
                category_scores[category]['reused'] += reused_quantity
                category_scores[category]['reduced'] += reduced_quantity

                # Kategori skoru hesapla
                category_score = ((recycled_quantity + reused_quantity + reduced_quantity) / quantity_kg * 100) if quantity_kg > 0 else 0
                category_scores[category]['score'] = category_score

            # Genel döngüsel ekonomi indeksi
            total_circular = total_recycled + total_reused + total_reduced
            circular_economy_index = (total_circular / total_waste * 100) if total_waste > 0 else 0.0

            # Kategoriler için ortalama skor
            avg_category_score = sum(cat['score'] for cat in category_scores.values()) / len(category_scores) if category_scores else 0.0

            return {
                'circular_economy_index': round(circular_economy_index, 2),
                'average_category_score': round(avg_category_score, 2),
                'total_waste': round(total_waste, 2),
                'total_circular': round(total_circular, 2),
                'breakdown': {
                    'recycled': round(total_recycled, 2),
                    'reused': round(total_reused, 2),
                    'reduced': round(total_reduced, 2)
                },
                'category_scores': {
                    k: {
                        'quantity': round(v['quantity'], 2),
                        'score': round(v['score'], 2),
                        'circular_amount': round(v['recycled'] + v['reused'] + v['reduced'], 2)
                    }
                    for k, v in category_scores.items()
                }
            }

        except Exception as e:
            logging.error(f"[HATA] Dongusel ekonomi indeksi hesaplanirken hata: {e}")
            return {}

    def calculate_sdg12_contribution(self, waste_data: List[Dict]) -> Dict:
        """SDG 12 (Sorumlu Tüketim ve Üretim) katkısını hesapla"""
        try:
            # SDG 12.3: Gıda atığı azaltma
            food_waste = sum(w.get('quantity', 0) for w in waste_data
                           if 'gıda' in w.get('waste_name', '').lower() or
                              'mutfak' in w.get('waste_name', '').lower())

            # SDG 12.5: Atık azaltma
            total_waste = sum(w.get('quantity', 0) for w in waste_data)

            # SDG 12.6: Sürdürülebilir uygulamalar
            sustainable_practices = sum(1 for w in waste_data
                                      if w.get('recycling_rate', 0) > 50)

            # SDG 12.4: Kimyasal atık yönetimi
            chemical_waste = sum(w.get('quantity', 0) for w in waste_data
                               if w.get('waste_category') == 'Tehlikeli')

            # Skorlama (0-100)
            food_waste_score = max(0, 100 - (food_waste / total_waste * 100 * 2)) if total_waste > 0 else 100
            waste_reduction_score = max(0, 100 - (total_waste / 1000 * 10))  # Basit hesaplama
            sustainable_practices_score = min(100, sustainable_practices * 20)
            chemical_management_score = max(0, 100 - (chemical_waste / total_waste * 100 * 3)) if total_waste > 0 else 100

            overall_score = (food_waste_score + waste_reduction_score +
                           sustainable_practices_score + chemical_management_score) / 4

            return {
                'sdg12_overall_score': round(overall_score, 2),
                'sdg12_3_food_waste_score': round(food_waste_score, 2),
                'sdg12_4_chemical_management_score': round(chemical_management_score, 2),
                'sdg12_5_waste_reduction_score': round(waste_reduction_score, 2),
                'sdg12_6_sustainable_practices_score': round(sustainable_practices_score, 2),
                'indicators': {
                    'food_waste_quantity': round(food_waste, 2),
                    'total_waste_quantity': round(total_waste, 2),
                    'sustainable_practices_count': sustainable_practices,
                    'chemical_waste_quantity': round(chemical_waste, 2)
                }
            }

        except Exception as e:
            logging.error(f"[HATA] SDG 12 katkisi hesaplanirken hata: {e}")
            return {}

    def _convert_to_kg(self, quantity: float, unit: str) -> float:
        """Birimi kg'ye çevir"""
        unit_conversions = {
            'kg': 1.0,
            'ton': 1000.0,
            'g': 0.001,
            'lb': 0.453592,
            'oz': 0.0283495,
            'm3': 1000.0,  # Su için yaklaşık
            'l': 1.0,      # Su için yaklaşık
            'piece': 0.5,  # Ortalama parça ağırlığı
            'unit': 1.0
        }

        return quantity * unit_conversions.get(unit.lower(), 1.0)

    def generate_waste_report_summary(self, waste_data: List[Dict]) -> Dict:
        """Atık rapor özeti oluştur"""
        try:
            if not waste_data:
                return {
                    'total_waste': 0.0,
                    'total_categories': 0,
                    'average_recycling_rate': 0.0,
                    'carbon_footprint': 0.0,
                    'circular_economy_index': 0.0,
                    'sdg12_score': 0.0
                }

            # Temel istatistikler
            total_waste = sum(w.get('quantity', 0) for w in waste_data)
            categories = set(w.get('waste_category', 'Genel') for w in waste_data)
            avg_recycling_rate = sum(w.get('recycling_rate', 0) for w in waste_data) / len(waste_data)

            # Hesaplamalar
            carbon_data = self.calculate_carbon_footprint(waste_data)
            circular_data = self.calculate_circular_economy_index(waste_data)
            sdg12_data = self.calculate_sdg12_contribution(waste_data)

            return {
                'total_waste': round(total_waste, 2),
                'total_categories': len(categories),
                'average_recycling_rate': round(avg_recycling_rate, 2),
                'carbon_footprint': carbon_data.get('total_carbon_footprint', 0.0),
                'circular_economy_index': circular_data.get('circular_economy_index', 0.0),
                'sdg12_score': sdg12_data.get('sdg12_overall_score', 0.0),
                'summary_text': f"Toplam {total_waste} kg atık, {len(categories)} kategori, %{avg_recycling_rate:.1f} ortalama geri dönüşüm oranı"
            }

        except Exception as e:
            logging.error(f"[HATA] Atik rapor ozeti olusturulurken hata: {e}")
            return {}
