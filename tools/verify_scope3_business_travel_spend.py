#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scope 3 İş Seyahatleri (harcamaya dayalı) doğrulama betiği.
Bir harcama bazlı kayıt ekler ve toplam ayak izinde Scope 3'ü doğrular.
"""

import logging
import json
from datetime import datetime

from carbon.carbon_calculator import CarbonCalculator
from carbon.carbon_manager import CarbonManager
from carbon.emission_factors import EmissionFactors

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    company_id = 1
    period = str(datetime.now().year)
    spend_usd = 1500

    manager = CarbonManager()
    calc = CarbonCalculator()
    ef = EmissionFactors()

    category_info = ef.SCOPE3_CATEGORIES.get('business_travel', {})
    sf = category_info.get('spend_factor_usd', 0.000200)
    co2e = spend_usd * sf

    emission_id = manager.save_emission_record(
        company_id=company_id,
        period=period,
        scope='scope3',
        category='business_travel',
        fuel_type='spend_usd',
        quantity=spend_usd,
        unit='USD',
        calculation_method='spend_based',
        data_quality='estimated',
        data_json=json.dumps({'spend_usd': spend_usd, 'notes': 'Doğrulama: harcama bazlı kayıt'}),
        notes='Doğrulama: EEIO tahmini',
        emission_factor_source=category_info.get('spend_source', 'EEIO'),
        co2e_emission=co2e
    )

    if emission_id:
        logging.info(f"[OK] Harcama bazlı iş seyahati eklendi. ID={emission_id}, co2e={co2e:.3f} tCO2e")
    else:
        logging.info("[ERR] Kayıt eklenemedi")
        return

    summary = calc.calculate_total_footprint(company_id=company_id, period=period, include_scope3=True)
    logging.info(f"Scope1: {summary['scope1_total']:.3f} tCO2e")
    logging.info(f"Scope2: {summary['scope2_total']:.3f} tCO2e")
    logging.info(f"Scope3: {summary.get('scope3_total', 0):.3f} tCO2e")
    logging.info(f"Toplam : {summary['total_co2e']:.3f} tCO2e")


if __name__ == '__main__':
    main()
