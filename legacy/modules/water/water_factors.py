#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SU FAKTÖRLERİ SINIFI
Su ayak izi hesaplama faktörleri ve katsayıları
"""

import logging
import os
import sqlite3
from typing import Dict, List, Optional

class WaterFactors:
    """Su faktörleri yönetimi - ISO 14046 ve Water Footprint Network standartları"""

    def __init__(self, db_path: str = None) -> None:
        if db_path is None:
            # Default to sustainage.db in project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, 'sustainage.db')
        
        self.db_path = db_path
        self.create_water_factors_table()

    def create_water_factors_table(self) -> None:
        """Özel su faktörleri tablosu oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_water_factors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    factor_type TEXT NOT NULL,              -- blue_water, green_water, grey_water
                    water_source TEXT NOT NULL,             -- groundwater, surface_water, etc.
                    factor_name TEXT NOT NULL,
                    factor_value REAL NOT NULL,
                    unit TEXT NOT NULL,                     -- m3/m3, m3/kg, etc.
                    reference TEXT,                         -- Kaynak/standart
                    region TEXT,                            -- Bölgesel faktörler
                    validity_start DATE,
                    validity_end DATE,
                    is_active INTEGER DEFAULT 1,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logging.info("[OK] Ozel su faktorleri tablosu olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Su faktorleri tablosu olusturulamadi: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_custom_factor(self, factor_type: str, factor_name: str, region: str = None) -> Optional[float]:
        """Özel su faktörü getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """
                SELECT factor_value FROM custom_water_factors 
                WHERE factor_type = ? AND factor_name = ? AND is_active = 1
            """
            params = [factor_type, factor_name]
            
            if region:
                query += " AND (region = ? OR region IS NULL)"
                params.append(region)
            
            query += " ORDER BY region DESC LIMIT 1"
            
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            
            return result[0] if result else None
            
        except Exception as e:
            logging.error(f"Ozel faktor getirme hatasi: {e}")
            return None
        finally:
            conn.close()

    # ==================== MAVİ SU FAKTÖRLERİ ====================

    def get_blue_water_factor(self, water_source: str, region: str = None) -> float:
        """Mavi su faktörü getir"""
        # Varsayılan mavi su faktörleri (genellikle 1:1)
        default_factors = {
            'groundwater': 1.0,
            'surface_water': 1.0,
            'municipal_water': 1.0,
            'well_water': 1.0,
            'spring_water': 1.0,
            'lake_water': 1.0,
            'river_water': 1.0,
            'reservoir_water': 1.0,
            'desalinated_water': 1.2,  # Desalinasyon enerji yoğun
            'recycled_water': 0.3,     # Geri dönüştürülmüş su
            'treated_wastewater': 0.5  # Arıtılmış atık su
        }

        # Özel faktör kontrolü
        custom_factor = self.get_custom_factor('blue_water', water_source, region)
        if custom_factor is not None:
            return custom_factor

        return default_factors.get(water_source, 1.0)

    def get_green_water_factor(self, water_source: str, region: str = None) -> float:
        """Yeşil su faktörü getir"""
        # Varsayılan yeşil su faktörleri
        default_factors = {
            'rainwater': 1.0,
            'precipitation': 1.0,
            'soil_moisture': 0.8,
            'crop_water': 0.9,
            'natural_vegetation': 0.7,
            'forest_water': 0.6,
            'wetland_water': 0.5
        }

        # Özel faktör kontrolü
        custom_factor = self.get_custom_factor('green_water', water_source, region)
        if custom_factor is not None:
            return custom_factor

        return default_factors.get(water_source, 1.0)

    def get_grey_water_factor(self, pollutant: str, region: str = None) -> float:
        """Gri su faktörü getir"""
        # Varsayılan gri su faktörleri (seyreltme faktörleri)
        default_factors = {
            'bod': 1.0,        # Biyolojik Oksijen İhtiyacı
            'cod': 1.0,        # Kimyasal Oksijen İhtiyacı
            'tss': 1.0,        # Toplam Askıda Katı Madde
            'nitrogen': 1.0,   # Azot
            'phosphorus': 1.0, # Fosfor
            'heavy_metals': 1.0,
            'pesticides': 1.0,
            'organic_compounds': 1.0,
            'salinity': 1.0,   # Tuzluluk
            'ph': 1.0
        }

        # Özel faktör kontrolü
        custom_factor = self.get_custom_factor('grey_water', pollutant, region)
        if custom_factor is not None:
            return custom_factor

        return default_factors.get(pollutant.lower(), 1.0)

    # ==================== SU YOĞUNLUĞU FAKTÖRLERİ ====================

    def get_water_intensity_factor(self, product_type: str, region: str = None) -> Dict:
        """Ürün bazlı su yoğunluğu faktörü getir"""
        # Varsayılan su yoğunluğu faktörleri (m³/ton)
        default_factors = {
            # Gıda ürünleri
            'wheat': 1.8,
            'rice': 2.5,
            'corn': 1.2,
            'soybean': 2.1,
            'sugar_cane': 0.2,
            'beef': 15.4,
            'pork': 5.9,
            'chicken': 4.3,
            'milk': 1.0,
            'eggs': 3.3,

            # Endüstriyel ürünler
            'steel': 15.0,
            'aluminum': 10.0,
            'cement': 0.5,
            'paper': 50.0,
            'cotton': 10.0,
            'textile': 200.0,
            'chemicals': 100.0,
            'pharmaceuticals': 1000.0,

            # Enerji
            'coal_power': 2.0,
            'gas_power': 0.7,
            'nuclear_power': 2.5,
            'hydropower': 0.1,
            'solar_power': 0.1,
            'wind_power': 0.05,

            # Hizmetler
            'office_building': 0.1,    # m³/m²/yıl
            'retail_store': 0.2,
            'hospital': 0.8,
            'school': 0.3,
            'hotel': 0.5
        }

        factor_value = default_factors.get(product_type.lower(), 1.0)

        # Bölgesel düzeltme faktörleri
        regional_correction = self.get_regional_correction_factor(region)
        corrected_factor = factor_value * regional_correction

        return {
            'product_type': product_type,
            'base_factor': factor_value,
            'regional_correction': regional_correction,
            'corrected_factor': corrected_factor,
            'unit': 'm3/ton',
            'region': region
        }

    def get_regional_correction_factor(self, region: str) -> float:
        """Bölgesel düzeltme faktörü getir"""
        # Bölgesel su kıtlığı ve iklim faktörleri
        regional_factors = {
            'turkey': 1.0,
            'mediterranean': 1.2,    # Su kıtlığı
            'arid': 1.5,            # Çöl iklimi
            'tropical': 0.8,        # Bol yağış
            'temperate': 1.0,       # Ilıman iklim
            'europe': 1.1,
            'asia': 1.2,
            'africa': 1.4,
            'america': 1.0,
            'oceania': 0.9
        }

        return regional_factors.get(region.lower() if region else 'global', 1.0)
