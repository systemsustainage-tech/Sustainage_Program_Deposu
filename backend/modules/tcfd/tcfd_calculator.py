#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCFD CALCULATOR - Finansal Etki Hesaplamaları
- Risk bazlı finansal etki hesaplaması
- Senaryo bazlı finansal projeksiyon
- Karbon fiyat etkisi
- Enerji maliyeti değişimi
- Gelir ve maliyet etkileri
"""

import logging
from typing import Dict, List, Optional


class TCFDCalculator:
    """TCFD finansal etki hesaplamaları"""

    def __init__(self):
        """Hesaplayıcı başlatma"""
        # No initialization required for this stateless calculator
        pass

    # ========================================================================
    # KARBON FİYAT ETKİSİ
    # ========================================================================

    def calculate_carbon_price_impact(
        self,
        scope1_emissions: float,
        scope2_emissions: float,
        scope3_emissions: float,
        carbon_price: float,
        scope3_included: bool = False
    ) -> Dict[str, float]:
        """
        Karbon fiyatlandırmasının finansal etkisini hesapla
        
        Args:
            scope1_emissions: Scope 1 emisyonları (tonCO2e)
            scope2_emissions: Scope 2 emisyonları (tonCO2e)
            scope3_emissions: Scope 3 emisyonları (tonCO2e)
            carbon_price: Karbon fiyatı (USD/tonCO2e)
            scope3_included: Scope 3 dahil mi?
        
        Returns:
            Finansal etki dict (USD)
        """
        scope1_cost = scope1_emissions * carbon_price
        scope2_cost = scope2_emissions * carbon_price
        scope3_cost = scope3_emissions * carbon_price if scope3_included else 0

        total_cost = scope1_cost + scope2_cost + scope3_cost

        return {
            'scope1_cost': scope1_cost,
            'scope2_cost': scope2_cost,
            'scope3_cost': scope3_cost,
            'total_cost': total_cost,
            'cost_per_tco2e': carbon_price
        }

    def calculate_carbon_price_scenario_impact(
        self,
        emissions: Dict[str, float],
        carbon_prices: Dict[int, float],
        start_year: int = 2025,
        end_year: int = 2050
    ) -> Dict[int, Dict[str, float]]:
        """
        Senaryo bazlı karbon fiyat etkisi (yıllık)
        
        Args:
            emissions: {'scope1': X, 'scope2': Y, 'scope3': Z}
            carbon_prices: {year: price} dict
            start_year: Başlangıç yılı
            end_year: Bitiş yılı
        
        Returns:
            {year: financial_impact} dict
        """
        results = {}

        for year in range(start_year, end_year + 1):
            if year in carbon_prices:
                price = carbon_prices[year]
            else:
                # Lineer interpolasyon
                years = sorted(carbon_prices.keys())
                if year < years[0]:
                    price = carbon_prices[years[0]]
                elif year > years[-1]:
                    price = carbon_prices[years[-1]]
                else:
                    # İki yıl arasında
                    for i in range(len(years) - 1):
                        if years[i] <= year <= years[i+1]:
                            y1, y2 = years[i], years[i+1]
                            p1, p2 = carbon_prices[y1], carbon_prices[y2]
                            price = p1 + (p2 - p1) * (year - y1) / (y2 - y1)
                            break

            impact = self.calculate_carbon_price_impact(
                emissions.get('scope1', 0),
                emissions.get('scope2', 0),
                emissions.get('scope3', 0),
                price,
                scope3_included=True
            )

            results[year] = impact

        return results

    # ========================================================================
    # ENERJİ MALİYETİ ETKİSİ
    # ========================================================================

    def calculate_energy_cost_impact(
        self,
        current_energy_consumption: float,  # MWh
        current_energy_price: float,        # USD/MWh
        future_energy_price: float,         # USD/MWh
        renewable_transition_pct: float = 0, # %
        renewable_price_premium: float = 0  # % (negatif = indirim)
    ) -> Dict[str, float]:
        """
        Enerji maliyet değişimi etkisi
        
        Returns:
            Maliyet değişimi dict
        """
        # Mevcut maliyet
        current_cost = current_energy_consumption * current_energy_price

        # Gelecek maliyet
        fossil_consumption = current_energy_consumption * (1 - renewable_transition_pct / 100)
        renewable_consumption = current_energy_consumption * (renewable_transition_pct / 100)

        fossil_cost = fossil_consumption * future_energy_price
        renewable_price = future_energy_price * (1 + renewable_price_premium / 100)
        renewable_cost = renewable_consumption * renewable_price

        future_cost = fossil_cost + renewable_cost

        # Değişim
        cost_change = future_cost - current_cost
        cost_change_pct = (cost_change / current_cost * 100) if current_cost > 0 else 0

        return {
            'current_cost': current_cost,
            'future_cost': future_cost,
            'cost_change': cost_change,
            'cost_change_pct': cost_change_pct,
            'fossil_cost': fossil_cost,
            'renewable_cost': renewable_cost
        }

    # ========================================================================
    # GELİR ETKİSİ (FIRSATtheLAR)
    # ========================================================================

    def calculate_revenue_opportunity(
        self,
        current_revenue: float,
        low_carbon_product_revenue_pct: float,  # Düşük karbonlu ürün geliri %
        market_growth_rate: float,              # Pazar büyüme oranı %
        years: int = 5
    ) -> Dict:
        """
        Düşük karbonlu ürünlerden gelir fırsatı
        
        Returns:
            Gelir projeksiyonu
        """
        projections = {}

        low_carbon_revenue = current_revenue * (low_carbon_product_revenue_pct / 100)

        for year in range(1, years + 1):
            future_revenue = low_carbon_revenue * ((1 + market_growth_rate / 100) ** year)
            additional_revenue = future_revenue - low_carbon_revenue

            projections[year] = {
                'projected_revenue': future_revenue,
                'additional_revenue': additional_revenue,
                'cumulative_additional': sum(
                    projections[y]['additional_revenue'] for y in range(1, year + 1)
                )
            }

        return {
            'baseline_low_carbon_revenue': low_carbon_revenue,
            'projections': projections
        }

    # ========================================================================
    # YATIRIM MALİYETİ (CAPEX)
    # ========================================================================

    def calculate_transition_capex(
        self,
        emissions_reduction_target_pct: float,  # Azaltma hedefi %
        current_emissions: float,               # tonCO2e
        cost_per_ton_abatement: float,          # Azaltma maliyeti USD/tonCO2e
        implementation_years: int = 10          # Uygulama süresi (yıl)
    ) -> Dict:
        """
        Düşük karbon geçişi yatırım maliyeti
        
        Returns:
            CAPEX projeksiyonu
        """
        # Hedef azaltma miktarı
        target_reduction = current_emissions * (emissions_reduction_target_pct / 100)

        # Toplam yatırım gereksinimi
        total_capex = target_reduction * cost_per_ton_abatement

        # Yıllık dağılım (basit lineer)
        annual_capex = total_capex / implementation_years

        # Yıllara göre dağılım
        capex_schedule = {}
        cumulative = 0

        for year in range(1, implementation_years + 1):
            capex_schedule[year] = {
                'annual_capex': annual_capex,
                'cumulative_capex': cumulative + annual_capex,
                'emissions_reduced': (target_reduction / implementation_years) * year
            }
            cumulative += annual_capex

        return {
            'total_capex': total_capex,
            'annual_capex': annual_capex,
            'target_reduction_tco2e': target_reduction,
            'cost_per_ton': cost_per_ton_abatement,
            'schedule': capex_schedule
        }

    # ========================================================================
    # RİSK BAZLI FİNANSAL ETKİ
    # ========================================================================

    def calculate_risk_financial_impact(
        self,
        likelihood_score: int,      # 1-5
        impact_score: int,          # 1-5
        financial_impact_low: float,
        financial_impact_high: float,
        probability_adjustment: float = 1.0
    ) -> Dict:
        """
        Risk bazlı finansal etki (beklenen değer)
        
        Returns:
            Risk-adjusted finansal etki
        """
        # Risk skoru (1-25)
        risk_score = likelihood_score * impact_score

        # Olasılık (yaklaşık)
        likelihood_map = {
            1: 0.05,   # Very Low: %5
            2: 0.15,   # Low: %15
            3: 0.40,   # Medium: %40
            4: 0.70,   # High: %70
            5: 0.90    # Very High: %90
        }

        probability = likelihood_map.get(likelihood_score, 0.5) * probability_adjustment

        # Beklenen etki
        expected_impact_low = financial_impact_low * probability
        expected_impact_high = financial_impact_high * probability
        expected_impact_mid = (expected_impact_low + expected_impact_high) / 2

        return {
            'risk_score': risk_score,
            'probability': probability,
            'expected_impact_low': expected_impact_low,
            'expected_impact_high': expected_impact_high,
            'expected_impact_mid': expected_impact_mid,
            'max_impact': financial_impact_high
        }

    def aggregate_risk_impacts(self, risks: List[Dict]) -> Dict:
        """
        Birden fazla risk için toplam finansal etki
        
        Args:
            risks: Risk listesi (her biri calculate_risk_financial_impact çıktısı)
        
        Returns:
            Toplam etki
        """
        if not risks:
            return {
                'total_expected_low': 0,
                'total_expected_high': 0,
                'total_expected_mid': 0,
                'total_max_impact': 0,
                'risk_count': 0
            }

        total_expected_low = sum(r['expected_impact_low'] for r in risks)
        total_expected_high = sum(r['expected_impact_high'] for r in risks)
        total_expected_mid = sum(r['expected_impact_mid'] for r in risks)
        total_max_impact = sum(r['max_impact'] for r in risks)

        return {
            'total_expected_low': total_expected_low,
            'total_expected_high': total_expected_high,
            'total_expected_mid': total_expected_mid,
            'total_max_impact': total_max_impact,
            'risk_count': len(risks),
            'avg_expected_impact': total_expected_mid / len(risks) if risks else 0
        }

    # ========================================================================
    # SENARYO BAZLI TOPLAM ETKİ
    # ========================================================================

    def calculate_scenario_total_impact(
        self,
        scenario_assumptions: Dict,
        company_data: Dict,
        target_year: int = 2030
    ) -> Dict:
        """
        Senaryo için toplam finansal etki
        
        Args:
            scenario_assumptions: Senaryo varsayımları
            company_data: Şirket verileri
            target_year: Hedef yıl
        
        Returns:
            Toplam etki analizi
        """
        results = {}

        # 1. Karbon fiyat etkisi
        if 'carbon_price' in scenario_assumptions and 'emissions' in company_data:
            carbon_impact = self.calculate_carbon_price_impact(
                company_data['emissions'].get('scope1', 0),
                company_data['emissions'].get('scope2', 0),
                company_data['emissions'].get('scope3', 0),
                scenario_assumptions['carbon_price'],
                scope3_included=True
            )
            results['carbon_cost'] = carbon_impact['total_cost']
        else:
            results['carbon_cost'] = 0

        # 2. Enerji maliyet etkisi
        if 'energy_price' in scenario_assumptions and 'energy' in company_data:
            energy_impact = self.calculate_energy_cost_impact(
                company_data['energy'].get('consumption', 0),
                company_data['energy'].get('current_price', 0),
                scenario_assumptions['energy_price'],
                scenario_assumptions.get('renewable_pct', 0),
                scenario_assumptions.get('renewable_premium', 0)
            )
            results['energy_cost_change'] = energy_impact['cost_change']
        else:
            results['energy_cost_change'] = 0

        # 3. Gelir fırsatı
        if 'market_growth' in scenario_assumptions and 'revenue' in company_data:
            years_to_target = target_year - 2025  # Varsayılan başlangıç
            revenue_opp = self.calculate_revenue_opportunity(
                company_data['revenue'],
                company_data.get('low_carbon_revenue_pct', 10),
                scenario_assumptions['market_growth'],
                years=years_to_target
            )
            if years_to_target in revenue_opp['projections']:
                results['revenue_opportunity'] = revenue_opp['projections'][years_to_target]['additional_revenue']
            else:
                results['revenue_opportunity'] = 0
        else:
            results['revenue_opportunity'] = 0

        # Toplam net etki
        results['total_costs'] = results['carbon_cost'] + max(0, results['energy_cost_change'])
        results['total_opportunities'] = results['revenue_opportunity']
        results['net_impact'] = results['total_opportunities'] - results['total_costs']

        return results

    # ========================================================================
    # YARDIMCI FONKSİYONLAR
    # ========================================================================

    def npv(self, cash_flows: List[float], discount_rate: float) -> float:
        """
        Net Present Value (NPV) hesaplama
        
        Args:
            cash_flows: Yıllık nakit akışları (ilk eleman t=0)
            discount_rate: İskonto oranı (%)
        
        Returns:
            NPV
        """
        r = discount_rate / 100
        npv_value = 0

        for t, cf in enumerate(cash_flows):
            npv_value += cf / ((1 + r) ** t)

        return npv_value

    def irr(self, cash_flows: List[float], guess: float = 0.1) -> Optional[float]:
        """
        Internal Rate of Return (IRR) hesaplama (Newton-Raphson)
        
        Args:
            cash_flows: Yıllık nakit akışları
            guess: Başlangıç tahmini
        
        Returns:
            IRR (%) veya None
        """
        # Basit IRR hesaplaması (yaklaşık)
        # Tam implementasyon için scipy kullanılabilir

        max_iterations = 100
        tolerance = 0.0001

        r = guess

        for _ in range(max_iterations):
            npv_val = sum(cf / ((1 + r) ** t) for t, cf in enumerate(cash_flows))
            d_npv = sum(-t * cf / ((1 + r) ** (t + 1)) for t, cf in enumerate(cash_flows))

            if abs(npv_val) < tolerance:
                return r * 100  # % olarak döndür

            if d_npv == 0:
                return None

            r = r - npv_val / d_npv

            if r < -0.99:  # İnvalid
                return None

        return None


# Test
if __name__ == "__main__":
    logging.info(" TCFD Calculator Test")
    logging.info("="*60)

    calc = TCFDCalculator()

    # 1. Karbon fiyat etkisi
    logging.info("\n1️⃣ Karbon Fiyat Etkisi:")
    carbon_impact = calc.calculate_carbon_price_impact(
        scope1_emissions=10000,
        scope2_emissions=5000,
        scope3_emissions=20000,
        carbon_price=75,
        scope3_included=True
    )
    logging.info(f"   Toplam Maliyet: ${carbon_impact['total_cost']:,.0f}")
    logging.info(f"   Scope 1: ${carbon_impact['scope1_cost']:,.0f}")
    logging.info(f"   Scope 2: ${carbon_impact['scope2_cost']:,.0f}")
    logging.info(f"   Scope 3: ${carbon_impact['scope3_cost']:,.0f}")

    # 2. Geçiş CAPEX
    logging.info("\n2️⃣ Geçiş Yatırımı (CAPEX):")
    capex = calc.calculate_transition_capex(
        emissions_reduction_target_pct=50,
        current_emissions=15000,
        cost_per_ton_abatement=100,
        implementation_years=10
    )
    logging.info(f"   Toplam CAPEX: ${capex['total_capex']:,.0f}")
    logging.info(f"   Yıllık CAPEX: ${capex['annual_capex']:,.0f}")
    logging.info(f"   Hedef Azaltma: {capex['target_reduction_tco2e']:,.0f} tonCO2e")

    # 3. NPV
    logging.info("\n3️⃣ NPV Hesaplama:")
    cash_flows = [-1000000, 200000, 300000, 300000, 400000, 500000]
    npv_result = calc.npv(cash_flows, discount_rate=10)
    logging.info(f"   NPV (10%): ${npv_result:,.0f}")

    logging.info("\n" + "="*60)

