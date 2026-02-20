#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATIK FAKTÖRLERİ YÖNETİCİSİ
Atık hesaplamaları için faktörler ve katsayılar
"""

import logging
from typing import Dict


class WasteFactors:
    """Atık Faktörleri Yöneticisi"""

    def __init__(self) -> None:
        # Karbon emisyon faktörleri (kg CO2e/kg atık)
        self.carbon_emission_factors = {
            # Organik atık faktörleri
            'organic_composting': 0.15,      # Kompostlama
            'organic_landfill': 0.45,        # Depolama
            'organic_incineration': 0.35,    # Yakma
            'organic_biogas': -0.20,         # Biyogaz (negatif = azaltma)
            'organic_anaerobic_digestion': -0.25,  # Anaerobik çürütme

            # Plastik atık faktörleri
            'plastic_recycling': -0.80,      # Geri dönüşüm (negatif = azaltma)
            'plastic_landfill': 0.15,        # Depolama
            'plastic_incineration': 0.25,    # Yakma
            'plastic_pyrolysis': -0.60,      # Piroliz (negatif = azaltma)

            # Metal atık faktörleri
            'metal_recycling': -1.50,        # Geri dönüşüm (negatif = azaltma)
            'metal_landfill': 0.05,          # Depolama
            'metal_smelting': -1.20,         # Eritme (negatif = azaltma)

            # Kağıt atık faktörleri
            'paper_recycling': -0.60,        # Geri dönüşüm (negatif = azaltma)
            'paper_landfill': 0.20,          # Depolama
            'paper_incineration': 0.30,      # Yakma
            'paper_composting': 0.10,        # Kompostlama

            # Cam atık faktörleri
            'glass_recycling': -0.40,        # Geri dönüşüm (negatif = azaltma)
            'glass_landfill': 0.05,          # Depolama
            'glass_melting': -0.35,          # Eritme (negatif = azaltma)

            # Elektronik atık faktörleri
            'ewaste_recycling': -2.00,       # Geri dönüşüm (negatif = azaltma)
            'ewaste_landfill': 0.80,         # Depolama
            'ewaste_refurbishment': -1.80,   # Yenileme (negatif = azaltma)

            # Tehlikeli atık faktörleri
            'hazardous_treatment': 0.60,     # Özel işlem
            'hazardous_landfill': 1.20,      # Özel depolama
            'hazardous_incineration': 0.80,  # Özel yakma
            'hazardous_recycling': -0.40,    # Özel geri dönüşüm

            # İnşaat atık faktörleri
            'construction_recycling': -0.30, # Geri dönüşüm (negatif = azaltma)
            'construction_landfill': 0.10,   # Depolama
            'construction_reuse': -0.50,     # Yeniden kullanım

            # Tekstil atık faktörleri
            'textile_recycling': -0.70,      # Geri dönüşüm (negatif = azaltma)
            'textile_landfill': 0.25,        # Depolama
            'textile_incineration': 0.30,    # Yakma
            'textile_reuse': -0.60,          # Yeniden kullanım

            # Tıbbi atık faktörleri
            'medical_autoclave': 0.40,       # Otoklav
            'medical_incineration': 0.70,    # Yakma
            'medical_landfill': 1.50,        # Özel depolama

            # Genel atık faktörleri
            'general_landfill': 0.30,        # Genel depolama
            'general_incineration': 0.35,    # Genel yakma
            'general_recycling': -0.50,      # Genel geri dönüşüm
        }

        # Atık azaltma potansiyeli (0-100%)
        self.reduction_potential = {
            'Organik': 85,           # Yüksek azaltma potansiyeli
            'Geri Dönüşüm': 75,      # Orta-yüksek azaltma potansiyeli
            'Tehlikeli': 35,         # Düşük azaltma potansiyeli
            'İnşaat': 65,            # Orta-yüksek azaltma potansiyeli
            'Tekstil': 55,           # Orta azaltma potansiyeli
            'Tıbbi': 25,             # Düşük azaltma potansiyeli
            'Genel': 45,             # Düşük-orta azaltma potansiyeli
            'Elektronik': 70,        # Orta-yüksek azaltma potansiyeli
        }

        # Geri dönüşüm maliyeti (TL/kg)
        self.recycling_costs = {
            'Organik': 0.50,         # Kompostlama maliyeti
            'Geri Dönüşüm': 1.20,    # Geri dönüşüm maliyeti
            'Tehlikeli': 5.00,       # Özel işlem maliyeti
            'İnşaat': 0.80,          # İnşaat geri dönüşüm maliyeti
            'Tekstil': 2.50,         # Tekstil geri dönüşüm maliyeti
            'Tıbbi': 8.00,           # Tıbbi atık işlem maliyeti
            'Genel': 1.50,           # Genel atık işlem maliyeti
            'Elektronik': 3.50,      # Elektronik atık işlem maliyeti
        }

        # Bertaraf maliyeti (TL/kg)
        self.disposal_costs = {
            'Organik': 0.30,         # Kompostlama/Depolama
            'Geri Dönüşüm': 0.80,    # Depolama
            'Tehlikeli': 8.00,       # Özel işlem
            'İnşaat': 0.50,          # Depolama
            'Tekstil': 1.50,         # Depolama/Yakma
            'Tıbbi': 12.00,          # Özel işlem
            'Genel': 1.00,           # Depolama
            'Elektronik': 4.00,      # Özel işlem
        }

        # Geri dönüşüm gelirleri (TL/kg)
        self.recycling_revenues = {
            'Organik': 0.20,         # Kompost satışı
            'Geri Dönüşüm': 0.50,    # Geri dönüşüm geliri
            'Tehlikeli': 0.00,       # Genellikle gelir yok
            'İnşaat': 0.30,          # Geri dönüşüm geliri
            'Tekstil': 0.80,         # Tekstil geri dönüşüm geliri
            'Tıbbi': 0.00,           # Genellikle gelir yok
            'Genel': 0.40,           # Genel geri dönüşüm geliri
            'Elektronik': 2.00,      # Değerli metal geri kazanımı
        }

        # Su tüketimi faktörleri (L/kg)
        self.water_consumption_factors = {
            'Organik': 0.50,         # Kompostlama su tüketimi
            'Geri Dönüşüm': 2.00,    # Geri dönüşüm su tüketimi
            'Tehlikeli': 5.00,       # Özel işlem su tüketimi
            'İnşaat': 1.00,          # İnşaat geri dönüşüm su tüketimi
            'Tekstil': 8.00,         # Tekstil işlem su tüketimi
            'Tıbbi': 10.00,          # Tıbbi atık işlem su tüketimi
            'Genel': 1.50,           # Genel işlem su tüketimi
            'Elektronik': 3.00,      # Elektronik işlem su tüketimi
        }

        # Enerji tüketimi faktörleri (kWh/kg)
        self.energy_consumption_factors = {
            'Organik': 0.10,         # Kompostlama enerji tüketimi
            'Geri Dönüşüm': 0.50,    # Geri dönüşüm enerji tüketimi
            'Tehlikeli': 2.00,       # Özel işlem enerji tüketimi
            'İnşaat': 0.30,          # İnşaat geri dönüşüm enerji tüketimi
            'Tekstil': 1.50,         # Tekstil işlem enerji tüketimi
            'Tıbbi': 3.00,           # Tıbbi atık işlem enerji tüketimi
            'Genel': 0.80,           # Genel işlem enerji tüketimi
            'Elektronik': 1.20,      # Elektronik işlem enerji tüketimi
        }

        # Atık türü özellikleri
        self.waste_characteristics = {
            'ORGANIC-001': {
                'name': 'Organik Mutfak Atığı',
                'category': 'Organik',
                'hazard_level': 'Non-hazardous',
                'recycling_potential': 'High',
                'biodegradability': 95,
                'moisture_content': 70,
                'calorific_value': 2.5,  # MJ/kg
                'ph_level': 6.5
            },
            'RECYCLE-001': {
                'name': 'Kağıt ve Karton',
                'category': 'Geri Dönüşüm',
                'hazard_level': 'Non-hazardous',
                'recycling_potential': 'High',
                'biodegradability': 90,
                'moisture_content': 10,
                'calorific_value': 15.0,  # MJ/kg
                'ph_level': 7.0
            },
            'RECYCLE-002': {
                'name': 'Plastik',
                'category': 'Geri Dönüşüm',
                'hazard_level': 'Non-hazardous',
                'recycling_potential': 'Medium',
                'biodegradability': 5,
                'moisture_content': 2,
                'calorific_value': 35.0,  # MJ/kg
                'ph_level': 7.0
            },
            'HAZARD-001': {
                'name': 'Kimyasal Atık',
                'category': 'Tehlikeli',
                'hazard_level': 'Hazardous',
                'recycling_potential': 'Low',
                'biodegradability': 0,
                'moisture_content': 5,
                'calorific_value': 20.0,  # MJ/kg
                'ph_level': 3.0
            }
        }

        # Bölgesel faktörler (Türkiye için)
        self.regional_factors = {
            'istanbul': {
                'landfill_cost_multiplier': 1.2,
                'transportation_cost': 0.50,  # TL/kg/km
                'recycling_facility_density': 0.8,
                'waste_separation_rate': 0.3
            },
            'ankara': {
                'landfill_cost_multiplier': 1.0,
                'transportation_cost': 0.40,
                'recycling_facility_density': 0.6,
                'waste_separation_rate': 0.25
            },
            'izmir': {
                'landfill_cost_multiplier': 1.1,
                'transportation_cost': 0.45,
                'recycling_facility_density': 0.7,
                'waste_separation_rate': 0.35
            },
            'default': {
                'landfill_cost_multiplier': 0.8,
                'transportation_cost': 0.30,
                'recycling_facility_density': 0.4,
                'waste_separation_rate': 0.15
            }
        }

    def get_carbon_factor(self, category: str, disposal_method: str) -> float:
        """Karbon emisyon faktörünü getir"""
        factor_key = f"{category.lower()}_{disposal_method.lower()}"
        return self.carbon_emission_factors.get(factor_key, 0.30)  # Varsayılan

    def get_reduction_potential(self, category: str) -> float:
        """Azaltma potansiyelini getir"""
        return self.reduction_potential.get(category, 40.0)  # Varsayılan %40

    def get_recycling_cost(self, category: str) -> float:
        """Geri dönüşüm maliyetini getir"""
        return self.recycling_costs.get(category, 1.50)  # Varsayılan

    def get_disposal_cost(self, category: str) -> float:
        """Bertaraf maliyetini getir"""
        return self.disposal_costs.get(category, 1.00)  # Varsayılan

    def get_recycling_revenue(self, category: str) -> float:
        """Geri dönüşüm gelirini getir"""
        return self.recycling_revenues.get(category, 0.40)  # Varsayılan

    def get_water_consumption(self, category: str) -> float:
        """Su tüketim faktörünü getir"""
        return self.water_consumption_factors.get(category, 1.50)  # Varsayılan

    def get_energy_consumption(self, category: str) -> float:
        """Enerji tüketim faktörünü getir"""
        return self.energy_consumption_factors.get(category, 0.80)  # Varsayılan

    def get_waste_characteristics(self, waste_code: str) -> Dict:
        """Atık türü özelliklerini getir"""
        return self.waste_characteristics.get(waste_code, {
            'name': 'Bilinmeyen Atık',
            'category': 'Genel',
            'hazard_level': 'Non-hazardous',
            'recycling_potential': 'Medium',
            'biodegradability': 50,
            'moisture_content': 30,
            'calorific_value': 10.0,
            'ph_level': 7.0
        })

    def get_regional_factor(self, region: str, factor_type: str) -> float:
        """Bölgesel faktörü getir"""
        region_data = self.regional_factors.get(region.lower(), self.regional_factors['default'])
        return region_data.get(factor_type, 1.0)

    def calculate_environmental_impact(self, waste_data: Dict) -> Dict:
        """Çevresel etki hesapla"""
        try:
            category = waste_data.get('waste_category', 'Genel')
            quantity = waste_data.get('quantity', 0)
            disposal_method = waste_data.get('disposal_method', 'landfill')

            # Karbon emisyonu
            carbon_factor = self.get_carbon_factor(category, disposal_method)
            carbon_emission = quantity * carbon_factor

            # Su tüketimi
            water_factor = self.get_water_consumption(category)
            water_consumption = quantity * water_factor

            # Enerji tüketimi
            energy_factor = self.get_energy_consumption(category)
            energy_consumption = quantity * energy_factor

            # Çevresel etki skoru (0-100, düşük = iyi)
            impact_score = min(100, (carbon_emission * 10 + water_consumption * 0.1 + energy_consumption * 2))

            return {
                'carbon_emission': round(carbon_emission, 2),
                'water_consumption': round(water_consumption, 2),
                'energy_consumption': round(energy_consumption, 2),
                'environmental_impact_score': round(impact_score, 2),
                'unit': {
                    'carbon': 'kg CO2e',
                    'water': 'L',
                    'energy': 'kWh'
                }
            }

        except Exception as e:
            logging.error(f"[HATA] Cevresel etki hesaplanirken hata: {e}")
            return {}

    def calculate_economic_impact(self, waste_data: Dict) -> Dict:
        """Ekonomik etki hesapla"""
        try:
            category = waste_data.get('waste_category', 'Genel')
            quantity = waste_data.get('quantity', 0)
            waste_data.get('disposal_method', 'landfill')
            recycling_rate = waste_data.get('recycling_rate', 0) / 100

            # Geri dönüşüm maliyeti
            recycling_cost = quantity * recycling_rate * self.get_recycling_cost(category)

            # Bertaraf maliyeti (geri dönüşüm dışı)
            disposal_cost = quantity * (1 - recycling_rate) * self.get_disposal_cost(category)

            # Geri dönüşüm geliri
            recycling_revenue = quantity * recycling_rate * self.get_recycling_revenue(category)

            # Net maliyet
            net_cost = recycling_cost + disposal_cost - recycling_revenue

            return {
                'recycling_cost': round(recycling_cost, 2),
                'disposal_cost': round(disposal_cost, 2),
                'recycling_revenue': round(recycling_revenue, 2),
                'net_cost': round(net_cost, 2),
                'cost_per_kg': round(net_cost / quantity, 2) if quantity > 0 else 0,
                'unit': 'TL'
            }

        except Exception as e:
            logging.error(f"[HATA] Ekonomik etki hesaplanirken hata: {e}")
            return {}

    def get_optimal_disposal_method(self, waste_data: Dict) -> Dict:
        """Optimal bertaraf yöntemini öner"""
        try:
            category = waste_data.get('waste_category', 'Genel')
            waste_data.get('quantity', 0)

            # Mevcut bertaraf yöntemleri
            disposal_methods = ['landfill', 'recycling', 'incineration', 'composting']

            best_method = 'landfill'
            best_score = float('inf')
            method_scores = {}

            for method in disposal_methods:
                # Çevresel etki
                env_impact = self.calculate_environmental_impact({
                    **waste_data,
                    'disposal_method': method
                })

                # Ekonomik etki
                econ_impact = self.calculate_economic_impact({
                    **waste_data,
                    'disposal_method': method
                })

                # Skor hesaplama (düşük = iyi)
                score = (env_impact.get('environmental_impact_score', 50) * 0.6 +
                        econ_impact.get('cost_per_kg', 1.0) * 10 * 0.4)

                method_scores[method] = {
                    'score': round(score, 2),
                    'environmental_impact': env_impact.get('environmental_impact_score', 50),
                    'cost_per_kg': econ_impact.get('cost_per_kg', 1.0),
                    'carbon_emission': env_impact.get('carbon_emission', 0),
                    'net_cost': econ_impact.get('net_cost', 0)
                }

                if score < best_score:
                    best_score = score
                    best_method = method

            return {
                'recommended_method': best_method,
                'method_scores': method_scores,
                'recommendation_reason': self._get_recommendation_reason(best_method, category)
            }

        except Exception as e:
            logging.error(f"[HATA] Optimal bertaraf yontemi hesaplanirken hata: {e}")
            return {}

    def _get_recommendation_reason(self, method: str, category: str) -> str:
        """Öneri gerekçesini getir"""
        reasons = {
            'recycling': f"{category} kategorisi için geri dönüşüm en çevre dostu ve ekonomik seçenektir.",
            'composting': f"{category} kategorisi için kompostlama organik atıklar için ideal bertaraf yöntemidir.",
            'incineration': f"{category} kategorisi için yakma enerji geri kazanımı sağlar ancak daha yüksek maliyetlidir.",
            'landfill': f"{category} kategorisi için depolama en ucuz seçenek ancak çevresel etkisi yüksektir."
        }
        return reasons.get(method, "Önerilen bertaraf yöntemi için uygun seçenek bulunamadı.")
