#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KARBON OFFSET HESAPLAMA MOTORU
Net emisyon, offset ihtiyacı ve KPI hesaplamaları
"""

import logging
from datetime import datetime
from typing import Dict, List, Tuple
from config.icons import Icons

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class OffsetCalculator:
    """Offset ve net emisyon hesaplama sınıfı"""

    def __init__(self) -> None:
        pass

    # ==================== NET EMİSYON HESAPLAMA ====================

    def calculate_net_emissions(self, gross_emissions: Dict,
                                offsets: Dict) -> Dict:
        """
        Net emisyon hesapla
        
        Args:
            gross_emissions: {'scope1': 100, 'scope2': 50, 'scope3': 200}
            offsets: {'scope1': 30, 'scope2': 20, 'scope3': 0}
        
        Returns:
            Net emisyon detayları
        """
        scope1_gross = gross_emissions.get('scope1', 0)
        scope2_gross = gross_emissions.get('scope2', 0)
        scope3_gross = gross_emissions.get('scope3', 0)
        total_gross = scope1_gross + scope2_gross + scope3_gross

        scope1_offset = offsets.get('scope1', 0)
        scope2_offset = offsets.get('scope2', 0)
        scope3_offset = offsets.get('scope3', 0)
        total_offset = scope1_offset + scope2_offset + scope3_offset

        # Net = Gross - Offset (min 0)
        scope1_net = max(0, scope1_gross - scope1_offset)
        scope2_net = max(0, scope2_gross - scope2_offset)
        scope3_net = max(0, scope3_gross - scope3_offset)
        total_net = scope1_net + scope2_net + scope3_net

        # KPI'lar
        offset_percentage = (total_offset / total_gross * 100) if total_gross > 0 else 0
        carbon_neutral = (total_net <= 0.01)  # Tolerans
        reduction_vs_gross = ((total_gross - total_net) / total_gross * 100) if total_gross > 0 else 0

        return {
            'gross': {
                'scope1': round(scope1_gross, 2),
                'scope2': round(scope2_gross, 2),
                'scope3': round(scope3_gross, 2),
                'total': round(total_gross, 2)
            },
            'offsets': {
                'scope1': round(scope1_offset, 2),
                'scope2': round(scope2_offset, 2),
                'scope3': round(scope3_offset, 2),
                'total': round(total_offset, 2)
            },
            'net': {
                'scope1': round(scope1_net, 2),
                'scope2': round(scope2_net, 2),
                'scope3': round(scope3_net, 2),
                'total': round(total_net, 2)
            },
            'kpis': {
                'offset_percentage': round(offset_percentage, 2),
                'carbon_neutral': carbon_neutral,
                'reduction_vs_gross_pct': round(reduction_vs_gross, 2),
                'remaining_emissions': round(total_net, 2)
            }
        }

    # ==================== OFFSET İHTİYACI ====================

    def calculate_offset_requirement(self, gross_emissions: float,
                                     target_reduction_pct: float = 100) -> Dict:
        """
        Hedefe ulaşmak için gereken offset miktarını hesapla
        
        Args:
            gross_emissions: Brüt emisyon (tCO2e)
            target_reduction_pct: Hedef azaltma yüzdesi (100 = Karbon Nötr)
        
        Returns:
            Offset ihtiyacı ve maliyet tahminleri
        """
        target_reduction = gross_emissions * (target_reduction_pct / 100)
        required_offset = max(0, target_reduction)

        # Maliyet tahminleri (farklı fiyat senaryoları)
        price_scenarios = {
            'low': 5,      # $5/tCO2e (düşük kalite)
            'medium': 15,  # $15/tCO2e (orta kalite)
            'high': 30,    # $30/tCO2e (yüksek kalite - Gold Standard)
            'premium': 50  # $50/tCO2e (premium projeler)
        }

        cost_estimates = {}
        for scenario, price in price_scenarios.items():
            cost_estimates[scenario] = {
                'unit_price_usd': price,
                'total_cost_usd': round(required_offset * price, 2),
                'total_cost_try': round(required_offset * price * 32, 2)  # TRY tahmini
            }

        return {
            'gross_emissions_tco2e': round(gross_emissions, 2),
            'target_reduction_pct': target_reduction_pct,
            'required_offset_tco2e': round(required_offset, 2),
            'cost_estimates': cost_estimates,
            'carbon_neutral_achievable': (target_reduction_pct == 100)
        }

    # ==================== BÜTÇE OPTİMİZASYONU ====================

    def optimize_budget(self, available_budget_usd: float,
                       gross_emissions: float,
                       price_range: Tuple[float, float] = (5, 50)) -> Dict:
        """
        Bütçe ile ne kadar offset alınabilir hesapla
        
        Args:
            available_budget_usd: Mevcut bütçe ($)
            gross_emissions: Brüt emisyon (tCO2e)
            price_range: (min_price, max_price) $/tCO2e
        
        Returns:
            Bütçe optimizasyon analizi
        """
        min_price, max_price = price_range
        avg_price = (min_price + max_price) / 2

        # Farklı fiyatlarda alınabilecek offsetler
        max_offset_qty = available_budget_usd / min_price  # En ucuz senaryo
        min_offset_qty = available_budget_usd / max_price  # En pahalı senaryo
        avg_offset_qty = available_budget_usd / avg_price  # Ortalama senaryo

        # Coverage yüzdeleri
        max_coverage_pct = (max_offset_qty / gross_emissions * 100) if gross_emissions > 0 else 0
        min_coverage_pct = (min_offset_qty / gross_emissions * 100) if gross_emissions > 0 else 0
        avg_coverage_pct = (avg_offset_qty / gross_emissions * 100) if gross_emissions > 0 else 0

        # Karbon nötr için gereken ek bütçe
        if avg_coverage_pct < 100:
            additional_budget_needed = (gross_emissions - avg_offset_qty) * avg_price
        else:
            additional_budget_needed = 0

        return {
            'available_budget_usd': available_budget_usd,
            'gross_emissions_tco2e': round(gross_emissions, 2),
            'price_range': {'min': min_price, 'max': max_price, 'avg': avg_price},
            'offset_scenarios': {
                'best_case': {  # En ucuz fiyat
                    'quantity_tco2e': round(max_offset_qty, 2),
                    'coverage_pct': round(max_coverage_pct, 2),
                    'unit_price': min_price
                },
                'worst_case': {  # En pahalı fiyat
                    'quantity_tco2e': round(min_offset_qty, 2),
                    'coverage_pct': round(min_coverage_pct, 2),
                    'unit_price': max_price
                },
                'average_case': {  # Ortalama fiyat
                    'quantity_tco2e': round(avg_offset_qty, 2),
                    'coverage_pct': round(avg_coverage_pct, 2),
                    'unit_price': avg_price
                }
            },
            'carbon_neutral_achievable': (avg_coverage_pct >= 100),
            'additional_budget_needed_usd': round(additional_budget_needed, 2)
        }

    # ==================== YIL BAZLI OFFSET PLANLAMA ====================

    def plan_multi_year_offset(self, annual_emissions: List[Dict],
                              target_year: int,
                              annual_budget_usd: float) -> Dict:
        """
        Çok yıllı offset planlaması
        
        Args:
            annual_emissions: [{'year': 2024, 'emissions': 1000}, ...]
            target_year: Karbon nötr hedef yılı
            annual_budget_usd: Yıllık bütçe
        
        Returns:
            Yıl bazlı offset planı
        """
        if not annual_emissions:
            return {}

        current_year = datetime.now().year
        years_to_target = target_year - current_year

        if years_to_target <= 0:
            return {'error': 'Hedef yıl geçmiş'}

        # Toplam emisyon tahmini
        total_emissions = sum(e.get('emissions', 0) for e in annual_emissions)
        avg_annual_emissions = total_emissions / len(annual_emissions)

        # Tahmin edilen toplam emisyon (hedef yıla kadar)
        estimated_total_emissions = avg_annual_emissions * years_to_target

        # Yıllık offset kapasitesi (ortalama $15/tCO2e)
        annual_offset_capacity = annual_budget_usd / 15
        total_offset_capacity = annual_offset_capacity * years_to_target

        # Kapsama analizi
        coverage_pct = (total_offset_capacity / estimated_total_emissions * 100) if estimated_total_emissions > 0 else 0

        # Eksik/fazla
        offset_gap = estimated_total_emissions - total_offset_capacity

        return {
            'target_year': target_year,
            'years_to_target': years_to_target,
            'estimated_total_emissions_tco2e': round(estimated_total_emissions, 2),
            'annual_budget_usd': annual_budget_usd,
            'total_budget_usd': annual_budget_usd * years_to_target,
            'annual_offset_capacity_tco2e': round(annual_offset_capacity, 2),
            'total_offset_capacity_tco2e': round(total_offset_capacity, 2),
            'coverage_pct': round(coverage_pct, 2),
            'offset_gap_tco2e': round(offset_gap, 2),
            'carbon_neutral_achievable': (coverage_pct >= 95),  # %95+ tolerance
            'recommendation': self._get_recommendation(coverage_pct, offset_gap)
        }

    def _get_recommendation(self, coverage_pct: float, offset_gap: float) -> str:
        """Plan önerisi oluştur"""
        if coverage_pct >= 100:
            return f"{Icons.SUCCESS} Mevcut bütçe ile karbon nötr hedefine ulaşılabilir!"
        elif coverage_pct >= 75:
            surplus = abs(offset_gap)
            return f"{Icons.WARNING} Hedefe ulaşmak için {surplus:.0f} tCO2e ek offset gerekli (bütçe artışı önerilir)"
        elif coverage_pct >= 50:
            return f"{Icons.FAIL} Bütçe yetersiz. Öncelik: İç azaltma projelerine odaklanın!"
        else:
            return "🚫 Bütçe çok düşük. Offset yerine azaltma yatırımları yapılmalı."

    # ==================== ROI HESAPLAMA ====================

    def calculate_offset_roi(self, offset_cost_usd: float,
                            avoided_carbon_tax_usd: float,
                            brand_value_increase_usd: float = 0,
                            green_financing_benefit_usd: float = 0) -> Dict:
        """
        Offset yatırımının ROI'sini hesapla
        
        Args:
            offset_cost_usd: Offset maliyeti
            avoided_carbon_tax_usd: Kaçınılan karbon vergisi
            brand_value_increase_usd: Marka değeri artışı (tahmin)
            green_financing_benefit_usd: Yeşil finansman faydası
        
        Returns:
            ROI analizi
        """
        total_benefits = (avoided_carbon_tax_usd +
                         brand_value_increase_usd +
                         green_financing_benefit_usd)

        net_benefit = total_benefits - offset_cost_usd
        roi_pct = (net_benefit / offset_cost_usd * 100) if offset_cost_usd > 0 else 0
        payback_years = (offset_cost_usd / total_benefits) if total_benefits > 0 else float('inf')

        return {
            'offset_cost_usd': round(offset_cost_usd, 2),
            'total_benefits_usd': round(total_benefits, 2),
            'benefit_breakdown': {
                'avoided_carbon_tax': round(avoided_carbon_tax_usd, 2),
                'brand_value_increase': round(brand_value_increase_usd, 2),
                'green_financing_benefit': round(green_financing_benefit_usd, 2)
            },
            'net_benefit_usd': round(net_benefit, 2),
            'roi_pct': round(roi_pct, 2),
            'payback_years': round(payback_years, 2) if payback_years != float('inf') else 'N/A',
            'financially_viable': (roi_pct > 0)
        }

    # ==================== SCOPE OPTİMİZASYONU ====================

    def optimize_scope_allocation(self, total_offset_budget: float,
                                  scope_emissions: Dict,
                                  scope_priorities: Dict = None) -> Dict:
        """
        Bütçeyi scope'lara optimal dağıt
        
        Args:
            total_offset_budget: Toplam offset bütçesi ($)
            scope_emissions: {'scope1': 100, 'scope2': 50, 'scope3': 200}
            scope_priorities: {'scope1': 1.0, 'scope2': 1.5, 'scope3': 0.5}
                             (Yüksek değer = yüksek öncelik)
        
        Returns:
            Scope'lara dağıtım önerisi
        """
        if scope_priorities is None:
            # Default: Scope 1 ve 2'ye öncelik (kontrol edilebilir)
            scope_priorities = {'scope1': 1.5, 'scope2': 1.5, 'scope3': 0.7}

        # Ağırlıklı emisyon
        weighted_emissions = {}
        total_weighted = 0

        for scope, emissions in scope_emissions.items():
            priority = scope_priorities.get(scope, 1.0)
            weighted = emissions * priority
            weighted_emissions[scope] = weighted
            total_weighted += weighted

        # Bütçeyi dağıt (ağırlıklı oranlara göre)
        allocation = {}
        for scope, weighted in weighted_emissions.items():
            ratio = weighted / total_weighted if total_weighted > 0 else 0
            budget_allocated = total_offset_budget * ratio

            # $15/tCO2e ortalama fiyat
            offset_quantity = budget_allocated / 15
            coverage_pct = (offset_quantity / scope_emissions[scope] * 100) if scope_emissions[scope] > 0 else 0

            allocation[scope] = {
                'emissions_tco2e': round(scope_emissions[scope], 2),
                'priority': scope_priorities.get(scope, 1.0),
                'budget_allocated_usd': round(budget_allocated, 2),
                'offset_quantity_tco2e': round(offset_quantity, 2),
                'coverage_pct': round(coverage_pct, 2)
            }

        return {
            'total_offset_budget_usd': total_offset_budget,
            'allocation': allocation,
            'recommendation': 'Öncelik sırası: Scope 1 > Scope 2 > Scope 3'
        }


if __name__ == "__main__":
    # Test
    calc = OffsetCalculator()

    # Test 1: Net emisyon
    result = calc.calculate_net_emissions(
        gross_emissions={'scope1': 100, 'scope2': 50, 'scope3': 200},
        offsets={'scope1': 30, 'scope2': 20, 'scope3': 0}
    )
    logging.info("Net Emisyon:", result)

    # Test 2: Offset ihtiyacı
    requirement = calc.calculate_offset_requirement(
        gross_emissions=350,
        target_reduction_pct=100
    )
    logging.info("\nOffset İhtiyacı:", requirement)

    # Test 3: Bütçe optimizasyonu
    budget_opt = calc.optimize_budget(
        available_budget_usd=5000,
        gross_emissions=350
    )
    logging.info("\nBütçe Optimizasyonu:", budget_opt)

