#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Çevresel Modüller Test Script
Karbon, Enerji, Su ve Atık modüllerini test eder
"""

import logging
import os
import sys

# Configure logging before importing other modules
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

backend_dir = os.path.join(project_root, 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from modules.environmental import (CarbonCalculator, EnergyManager,
                                   WasteManager, WaterManager)


import sqlite3
from config.database import DB_PATH

def cleanup_tables() -> None:
    """Test tablolarını temizle"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    tables = [
        'carbon_emissions', 'carbon_summary',
        'energy_consumption', 'renewable_energy', 'energy_efficiency_projects', 'energy_targets', 'energy_kpis',
        'water_consumption', 'water_recycling', 'water_quality', 'water_efficiency_projects', 'water_targets',
        'waste_generation', 'waste_recycling', 'waste_reduction_projects', 'waste_targets', 'waste_categories'
    ]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
    conn.commit()
    conn.close()
    logging.info("[INFO] Tablolar temizlendi.")


def test_carbon() -> None:
    """Karbon modülü testi"""
    logging.info("\n" + "="*60)
    logging.info("1. KARBON AYAK IZI HESAPLAYICI")
    logging.info("="*60)
    
    calc = CarbonCalculator()
    
    # Scope 1
    fuel = calc.calculate_scope1_fuel('diesel', 1000)
    logging.info("\n[TEST] 1000 litre mazot")
    logging.info(f"  Emisyon: {fuel['co2e_ton']} ton CO2e")
    
    # Scope 2
    elec = calc.calculate_scope2_electricity(50000, renewable_percent=20)
    logging.info("\n[TEST] 50,000 kWh elektrik (%20 yenilenebilir)")
    logging.info(f"  Emisyon: {elec['co2e_ton']} ton CO2e")
    
    # Scope 3
    travel = calc.calculate_scope3_travel('flight_domestic', 800)
    logging.info("\n[TEST] 800 km ic hat ucus")
    logging.info(f"  Emisyon: {travel['co2e_ton']} ton CO2e")
    
    # Kaydet ve özet al
    calc.save_emission(1, fuel, '2024-01-01', '2024-12-31')
    calc.save_emission(1, elec, '2024-01-01', '2024-12-31')
    calc.save_emission(1, travel, '2024-01-01', '2024-12-31')
    
    summary = calc.get_company_summary(1, 2024)
    logging.info(f"\n[OZET] Toplam emisyon: {summary['total_ton']} ton CO2e")
    logging.info(f"  Scope 1: {summary['scope1_ton']} ton")
    logging.info(f"  Scope 2: {summary['scope2_ton']} ton")
    logging.info(f"  Scope 3: {summary['scope3_ton']} ton")
    logging.info("\n[OK] Karbon modulu testi BASARILI!")


def test_energy() -> None:
    """Enerji modülü testi"""
    logging.info("\n" + "="*60)
    logging.info("2. ENERJI YONETIMI")
    logging.info("="*60)
    
    energy = EnergyManager()
    
    # Konvansiyonel enerji
    energy.add_energy_consumption(1, 2024, 'Elektrik', 40000, 'kWh', 
                          source='Konvansiyonel', location='Merkez')
    logging.info("\n[TEST] 40,000 kWh konvansiyonel elektrik kaydedildi")
    
    # Yenilenebilir enerji
    energy.add_energy_consumption(1, 2024, 'Gunes', 10000, 'kWh',
                          source='Yenilenebilir', location='Panel')
    # Ayrıca yenilenebilir enerji üretimi olarak da ekle
    energy.add_renewable_energy(1, 2024, 'Gunes', 50, 'kW', 10000, 'kWh',
                                self_consumption=10000)
    logging.info("[TEST] 10,000 kWh yenilenebilir enerji kaydedildi")
    
    summary = energy.get_energy_summary(1, 2024)
    logging.info(f"\n[OZET] Toplam enerji: {summary['total_consumption']} kWh")
    logging.info(f"  Yenilenebilir: {summary['total_renewable']} kWh (%{summary['renewable_ratio']:.2f})")
    logging.info("\n[OK] Enerji modulu testi BASARILI!")


def test_water() -> None:
    """Su modülü testi"""
    logging.info("\n" + "="*60)
    logging.info("3. SU YONETIMI")
    logging.info("="*60)
    
    water = WaterManager()
    
    # Su tüketimi
    water.add_water_consumption(1, 2024, 'Sebekeden', 5000, 'm3',
                               source='Sebeke', location='Tesis')
    logging.info("\n[TEST] 5,000 m3 su tuketimi kaydedildi")

    # Su geri dönüşümü
    water.add_water_recycling(1, 2024, 'Arıtma', 500, 'm3',
                              treatment_method='Biyolojik')
    logging.info("[TEST] 500 m3 geri donusum kaydedildi")
    
    summary = water.get_water_summary(1, 2024)
    logging.info(f"\n[OZET] Toplam su: {summary['total_consumption']} m3")
    logging.info(f"  Geri donusum: {summary['total_recycled']} m3 (%{summary['recycling_ratio']:.2f})")
    logging.info("\n[OK] Su modulu testi BASARILI!")


def test_waste() -> None:
    """Atık modülü testi"""
    logging.info("\n" + "="*60)
    logging.info("4. ATIK YONETIMI")
    logging.info("="*60)
    
    waste = WasteManager()
    
    # Atık kayıtları
    waste.add_waste_generation(1, 2024, 'Kagit', 'Recyclable', 20, 'ton',
                              disposal_method='Recycling')
    logging.info("\n[TEST] 20 ton kagit atigi kaydedildi")
    
    waste.add_waste_recycling(1, 2024, 'Kagit', 15, 'ton',
                             recycling_method='Dis Kaynak')
    logging.info("[TEST] 15 ton kagit geri donusturuldu")
    
    waste.add_waste_generation(1, 2024, 'Pil', 'Hazardous', 2, 'ton',
                               hazardous_status='Hazardous')
    logging.info("[TEST] 2 ton tehlikeli atik (Pil) kaydedildi")
    
    summary = waste.get_waste_summary(1, 2024)
    logging.info(f"\n[OZET] Toplam atik: {summary['total_generation']} ton")
    logging.info(f"  Geri donusum: {summary['total_recycled']} ton (%{summary['recycling_ratio']:.2f})")
    logging.info("\n[OK] Atik modulu testi BASARILI!")


def main() -> None:
    """Ana test"""
    logging.info("\n" + "="*60)
    logging.info("    CEVRESEL MODULLER TEST ARACI")
    logging.info("="*60)
    
    try:
        cleanup_tables()
        test_carbon()
        test_energy()
        test_water()
        test_waste()
        
        logging.info("\n" + "="*60)
        logging.info("    TUM TESTLER BASARILI!")
        logging.info("="*60)
        logging.info("\nModuller hazir:")
        logging.info("  [OK] CarbonCalculator - Karbon ayak izi")
        logging.info("  [OK] EnergyManager - Enerji yonetimi")
        logging.info("  [OK] WaterManager - Su yonetimi")
        logging.info("  [OK] WasteManager - Atik yonetimi")
        logging.info("\n")
        
    except Exception as e:
        logging.error(f"\n[HATA] Test basarisiz: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

