#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scope 3 İş Seyahatleri doğrulama betiği.
Bir örnek kayıt ekler ve toplam ayak izinde Scope 3'ü doğrular.
"""

import logging
from datetime import datetime

from carbon.carbon_calculator import CarbonCalculator
from carbon.carbon_manager import CarbonManager
from carbon.emission_factors import EmissionFactors

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    company_id = 1
    period = str(datetime.now().year)
    travel_type = 'flight_medium'
    distance_km = 1200

    manager = CarbonManager()
    calc = CarbonCalculator()
    ef = EmissionFactors()

    # Faktörü al ve co2e hesapla
    category_info = ef.SCOPE3_CATEGORIES.get('business_travel', {})
    factor = category_info.get('factors', {}).get(travel_type, 0.0)
    co2e = distance_km * factor

    # Kayıt ekle
    emission_id = manager.save_emission_record(
        company_id=company_id,
        period=period,
        scope='scope3',
        category='business_travel',
        fuel_type=travel_type,
        quantity=distance_km,
        unit='km',
        calculation_method='distance_based',
        data_quality='estimated',
        data_json=f'{{"travel_type": "{travel_type}", "distance_km": {distance_km}}}',
        notes='Doğrulama: orta menzil uçuş',
        emission_factor_source=category_info.get('source', 'DEFRA'),
        co2e_emission=co2e
    )

    if emission_id:
        logging.info(f"[OK] Scope3 iş seyahati eklendi. ID={emission_id}, co2e={co2e:.3f} tCO2e")
    else:
        logging.info("[ERR] Kayıt eklenemedi")
        return

    # Toplam ayak izi (Scope 3 dahil)
    summary = calc.calculate_total_footprint(company_id=company_id, period=period, include_scope3=True)
    logging.info(f"Scope1: {summary['scope1_total']:.3f} tCO2e")
    logging.info(f"Scope2: {summary['scope2_total']:.3f} tCO2e")
    logging.info(f"Scope3: {summary.get('scope3_total', 0):.3f} tCO2e")
    logging.info(f"Toplam : {summary['total_co2e']:.3f} tCO2e")


if __name__ == '__main__':
    main()
