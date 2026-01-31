#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KARBON OFFSET MODÜLmü KULLANIM ÖRNEKLERİ
Mevcut CarbonManager ile entegre çalışma örnekleri
"""

import logging
from carbon_manager import CarbonManager
from offset_calculator import OffsetCalculator
from offset_manager import OffsetManager
from config.icons import Icons

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def demo_scenario_1_first_offset():
    """Senaryo 1: İlk Offset Satın Alma"""
    logging.info("\n" + "="*60)
    logging.info("SENARYO 1: İLK OFFSET SATIN ALMA")
    logging.info("="*60)

    # 1. Mevcut emisyonu öğren
    carbon_mgr = CarbonManager()
    offset_mgr = OffsetManager()
    calc = OffsetCalculator()

    company_id = 1
    period = "2024"

    # Brüt emisyon
    try:
        stats = carbon_mgr.get_dashboard_stats(company_id)
        total_emissions = stats['current_total_co2e']
    except Exception:
        total_emissions = 1000.0  # Varsayılan

    logging.info(f"\n{Icons.REPORT} Brüt Emisyon: {total_emissions:.2f} tCO2e")

    # 2. Offset ihtiyacını hesapla
    requirement = calc.calculate_offset_requirement(
        gross_emissions=total_emissions,
        target_reduction_pct=30  # %30 hedef
    )

    logging.info(f"\n{Icons.TARGET} Hedef: %{requirement['target_reduction_pct']} azaltma")
    logging.info(f"{Icons.TREE} Gerekli Offset: {requirement['required_offset_tco2e']:.2f} tCO2e")

    logging.info(f"\n{Icons.MONEY_BAG} Maliyet Tahminleri:")
    for scenario, data in requirement['cost_estimates'].items():
        logging.info(f"  {scenario.upper():12s}: ${data['total_cost_usd']:8,.2f} (${data['unit_price_usd']}/tCO2e)")

    # 3. Örnek proje ekle
    logging.info(f"\n{Icons.ADD} Offset Projesi Ekleniyor...")

    project_data = {
        'project_name': 'Amazon Rainforest Protection',
        'project_type': 'FORESTRY',
        'standard': 'VCS',
        'registry_id': 'VCS-1234',
        'location_country': 'Brazil',
        'vintage_year': 2023,
        'unit_price_usd': 15.00,
        'supplier_name': 'EcoOffset Ltd.',
        'verification_status': 'verified',
        'co_benefits': '["SDG 13", "SDG 15", "Biodiversity"]'
    }

    project_id = offset_mgr.add_offset_project(project_data)
    logging.info(f"{Icons.SUCCESS} Proje eklendi (ID: {project_id})")

    # 4. Offset satın al
    logging.info(f"\n{Icons.SHOPPING_CART} Offset Satın Alınıyor...")

    quantity = requirement['required_offset_tco2e']
    unit_price = 15.00

    transaction_data = {
        'company_id': company_id,
        'project_id': project_id,
        'period': period,
        'quantity_tco2e': quantity,
        'unit_price_usd': unit_price,
        'allocated_scope': 'scope1_2',
        'purpose': 'voluntary',
        'retirement_status': 'retired'
    }

    trans_id = offset_mgr.purchase_offset(transaction_data)

    logging.info(f"{Icons.SUCCESS} Offset satın alındı (ID: {trans_id})")
    logging.info(f"   Miktar: {quantity:.2f} tCO2e")
    logging.info(f"   Birim Fiyat: ${unit_price}/tCO2e")
    logging.info(f"   Toplam Maliyet: ${quantity * unit_price:,.2f}")

    # 5. Net emisyonu kontrol et
    logging.info(f"\n{Icons.CHART_UP} Net Emisyon Raporu:")

    net_data = offset_mgr.get_net_emissions(company_id, period)

    if net_data:
        logging.info(f"   Brüt Emisyon: {net_data['total_gross']:.2f} tCO2e")
        logging.info(f"   (-) Offset: {net_data['total_offset']:.2f} tCO2e")
        logging.info(f"   (=) Net Emisyon: {net_data['total_net']:.2f} tCO2e")
        logging.info(f"   Offset Kapsaması: %{net_data['offset_percentage']:.1f}")
        logging.info(f"   Karbon Nötr: {f'{Icons.SUCCESS} EVET' if net_data['carbon_neutral'] else f'{Icons.FAIL} Hayır'}")
    else:
        logging.info(f"   {Icons.WARNING} Net emisyon verisi bulunamadı")


def demo_scenario_2_budget_optimization():
    """Senaryo 2: Bütçe Optimizasyonu"""
    logging.info("\n" + "="*60)
    logging.info("SENARYO 2: BÜTÇE OPTİMİZASYONU")
    logging.info("="*60)

    calc = OffsetCalculator()

    # Parametreler
    available_budget = 10000  # $10,000
    gross_emissions = 1000    # 1,000 tCO2e

    logging.info(f"\n{Icons.BRIEFCASE} Mevcut Bütçe: ${available_budget:,.2f}")
    logging.info(f"{Icons.REPORT} Brüt Emisyon: {gross_emissions:,.2f} tCO2e")

    # Optimizasyon
    budget_opt = calc.optimize_budget(
        available_budget_usd=available_budget,
        gross_emissions=gross_emissions,
        price_range=(5, 50)
    )

    logging.info(f"\n{Icons.SEARCH} Offset Senaryoları:")
    for scenario, data in budget_opt['offset_scenarios'].items():
        logging.info(f"\n  {scenario.upper()}:")
        logging.info(f"    Miktar: {data['quantity_tco2e']:.2f} tCO2e")
        logging.info(f"    Kapsama: %{data['coverage_pct']:.1f}")
        logging.info(f"    Birim Fiyat: ${data['unit_price']}/tCO2e")

    logging.info(f"\n{Icons.TARGET} Sonuç:")
    logging.info(f"   Karbon Nötr Ulaşılabilir mi? {f'{Icons.SUCCESS} EVET' if budget_opt['carbon_neutral_achievable'] else f'{Icons.FAIL} Hayır'}")

    if not budget_opt['carbon_neutral_achievable']:
        logging.info(f"   Ek Bütçe Gereksinimi: ${budget_opt['additional_budget_needed_usd']:,.2f}")


def demo_scenario_3_multi_year_planning():
    """Senaryo 3: Çok Yıllı Offset Planlama"""
    logging.info(Icons.TREE * 30)
    logging.info(f"{Icons.TREE} SENARYO 3: GEÇMİŞ DÖNEM DENKLEŞTİRME {Icons.TREE}")
    logging.info(Icons.TREE * 30)

    calc = OffsetCalculator()

    # Geçmiş emisyon verileri
    annual_emissions = [
        {'year': 2020, 'emissions': 1200},
        {'year': 2021, 'emissions': 1150},
        {'year': 2022, 'emissions': 1100},
        {'year': 2023, 'emissions': 1050},
        {'year': 2024, 'emissions': 1000}
    ]

    target_year = 2030
    annual_budget = 15000  # $15,000/yıl

    logging.info(f"\n{Icons.CALENDAR} Geçmiş Emisyonlar:")
    for item in annual_emissions:
        logging.info(f"   {item['year']}: {item['emissions']:,.0f} tCO2e")

    logging.info(f"\n{Icons.TARGET} Hedef: {target_year} Net Sıfır")
    logging.info(f"{Icons.MONEY_BAG} Yıllık Bütçe: ${annual_budget:,.2f}")

    # Plan oluştur
    plan = calc.plan_multi_year_offset(
        annual_emissions=annual_emissions,
        target_year=target_year,
        annual_budget_usd=annual_budget
    )

    logging.info(f"\n{Icons.REPORT} Plan Özeti:")
    logging.info(f"   Kalan Süre: {plan['years_to_target']} yıl")
    logging.info(f"   Tahmini Toplam Emisyon: {plan['estimated_total_emissions_tco2e']:,.2f} tCO2e")
    logging.info(f"   Yıllık Offset Kapasitesi: {plan['annual_offset_capacity_tco2e']:,.2f} tCO2e")
    logging.info(f"   Toplam Offset Kapasitesi: {plan['total_offset_capacity_tco2e']:,.2f} tCO2e")
    logging.info(f"   Kapsama Oranı: %{plan['coverage_pct']:.1f}")
    logging.info(f"   Offset Eksikliği: {plan['offset_gap_tco2e']:,.2f} tCO2e")

    logging.info(f"\n{Icons.LIGHTBULB} Öneri:")
    logging.info(f"   {plan['recommendation']}")


def demo_scenario_4_roi_analysis():
    """Senaryo 4: ROI Analizi"""
    logging.info("\n" + "="*60)
    logging.info("SENARYO 4: OFFSET YATIRIMI ROI ANALİZİ")
    logging.info("="*60)

    calc = OffsetCalculator()

    # Offset maliyeti
    offset_cost = 12500  # $12,500

    # Faydalar
    avoided_tax = 8000          # Kaçınılan karbon vergisi
    brand_value = 5000          # Marka değeri artışı
    green_finance = 3000        # Yeşil finansman faydası

    logging.info(f"\n{Icons.MONEY_WITH_WINGS} Maliyet:")
    logging.info(f"   Offset Satın Alma: ${offset_cost:,.2f}")

    logging.info(f"\n{Icons.MONEY_BAG} Faydalar:")
    logging.info(f"   Kaçınılan Karbon Vergisi: ${avoided_tax:,.2f}")
    logging.info(f"   Marka Değeri Artışı: ${brand_value:,.2f}")
    logging.info(f"   Yeşil Finansman: ${green_finance:,.2f}")

    # ROI hesapla
    roi = calc.calculate_offset_roi(
        offset_cost_usd=offset_cost,
        avoided_carbon_tax_usd=avoided_tax,
        brand_value_increase_usd=brand_value,
        green_financing_benefit_usd=green_finance
    )

    logging.info(f"\n{Icons.CHART_UP} ROI Analizi:")
    logging.info(f"   Toplam Fayda: ${roi['total_benefits_usd']:,.2f}")
    logging.info(f"   Net Fayda: ${roi['net_benefit_usd']:,.2f}")
    logging.info(f"   ROI: %{roi['roi_pct']:.1f}")
    logging.info(f"   Geri Ödeme Süresi: {roi['payback_years']} yıl")
    logging.info(f"   Finansal Uygun mu? {f'{Icons.SUCCESS} EVET' if roi['financially_viable'] else f'{Icons.FAIL} Hayır'}")


def demo_scenario_5_scope_allocation():
    """Senaryo 5: Scope Bazlı Offset Dağıtımı"""
    logging.info("\n" + "="*60)
    logging.info("SENARYO 5: SCOPE BAZLI OFFSET DAĞITIMI")
    logging.info("="*60)

    calc = OffsetCalculator()

    # Parametreler
    total_budget = 15000
    scope_emissions = {
        'scope1': 500,   # Doğrudan (kontrol edilebilir)
        'scope2': 300,   # Dolaylı enerji (değiştirilebilir)
        'scope3': 1000   # Değer zinciri (zor azaltılır)
    }

    # Öncelikler (yüksek değer = yüksek öncelik)
    priorities = {
        'scope1': 1.5,  # Öncelik: Yüksek
        'scope2': 1.5,  # Öncelik: Yüksek
        'scope3': 0.7   # Öncelik: Orta
    }

    logging.info(f"\n{Icons.MONEY_BAG} Toplam Bütçe: ${total_budget:,.2f}")
    logging.info(f"{Icons.REPORT} Scope Emisyonları:")
    for scope, emissions in scope_emissions.items():
        logging.info(f"   {scope.upper():8s}: {emissions:,.0f} tCO2e (Öncelik: {priorities[scope]})")

    # Optimizasyon
    allocation = calc.optimize_scope_allocation(
        total_offset_budget=total_budget,
        scope_emissions=scope_emissions,
        scope_priorities=priorities
    )

    logging.info(f"\n{Icons.TARGET} Önerilen Dağıtım:")
    for scope, data in allocation['allocation'].items():
        logging.info(f"\n  {scope.upper()}:")
        logging.info(f"    Bütçe: ${data['budget_allocated_usd']:,.2f}")
        logging.info(f"    Offset: {data['offset_quantity_tco2e']:.2f} tCO2e")
        logging.info(f"    Kapsama: %{data['coverage_pct']:.1f}")

    logging.info(f"\n{Icons.LIGHTBULB} Öneri: {allocation['recommendation']}")


def demo_statistics():
    """Offset İstatistikleri"""
    logging.info("\n" + "="*60)
    logging.info("OFFSET İSTATİSTİKLERİ")
    logging.info("="*60)

    offset_mgr = OffsetManager()
    company_id = 1

    stats = offset_mgr.get_offset_statistics(company_id)

    logging.info(f"\n{Icons.REPORT} Genel İstatistikler:")
    logging.info(f"   Toplam İşlem: {stats.get('transaction_count', 0)}")
    logging.info(f"   Toplam Offset: {stats.get('total_offset_tco2e', 0):,.2f} tCO2e")
    logging.info(f"   Toplam Maliyet: ${stats.get('total_cost_usd', 0):,.2f}")
    logging.info(f"   Ortalama Birim Fiyat: ${stats.get('avg_unit_price', 0):.2f}/tCO2e")
    logging.info(f"   Min Fiyat: ${stats.get('min_unit_price', 0):.2f}/tCO2e")
    logging.info(f"   Max Fiyat: ${stats.get('max_unit_price', 0):.2f}/tCO2e")

    if stats.get('project_breakdown'):
        logging.info(f"\n{Icons.EVERGREEN_TREE} Proje Tiplerine Göre Dağılım:")
        for project in stats['project_breakdown']:
            print(f"   {project['project_type']:15s}: "
                  f"{project['total_tco2e']:8,.2f} tCO2e "
                  f"(${project['total_cost']:,.2f})")


if __name__ == "__main__":
    logging.info("\n")
    logging.info(Icons.TREE * 30)
    logging.info("KARBON OFFSET MODÜLÜ - DEMO SENARYOLAR")
    logging.info(Icons.TREE * 30)

    try:
        # Senaryo 1: İlk offset
        demo_scenario_1_first_offset()

        # Senaryo 2: Bütçe optimizasyonu
        demo_scenario_2_budget_optimization()

        # Senaryo 3: Çok yıllı plan
        demo_scenario_3_multi_year_planning()

        # Senaryo 4: ROI
        demo_scenario_4_roi_analysis()

        # Senaryo 5: Scope dağıtımı
        demo_scenario_5_scope_allocation()

        # İstatistikler
        demo_statistics()

        logging.info("\n" + "="*60)
        logging.info(f"{Icons.SUCCESS} TÜM SENARYOLAR TAMAMLANDI!")
        logging.info("="*60)
        logging.info(f"\n{Icons.LIGHTBULB} Daha fazla bilgi için: carbon/OFFSET_MODULE_README.md")
        logging.info("\n")

    except Exception as e:
        logging.error(f"\n{Icons.FAIL} HATA: {e}")
        import traceback
        traceback.print_exc()

