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

from config.settings import get_db_path


class WaterFactors:
    """Su faktörleri yönetimi - ISO 14046 ve Water Footprint Network standartları"""

    def __init__(self, db_path: str = None) -> None:
        if db_path is None:
            try:
                self.db_path = get_db_path()
            except Exception:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                self.db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
        else:
            if not os.path.isabs(db_path):
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                db_path = os.path.join(base_dir, db_path)
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

    # ==================== SU KALİTE FAKTÖRLERİ ====================

    def get_water_quality_standards(self, parameter: str, water_use: str = 'general') -> Dict:
        """Su kalite standartları getir"""
        # WHO, EPA ve Türk standartları
        standards = {
            # İçme suyu standartları
            'drinking_water': {
                'ph': {'min': 6.5, 'max': 8.5, 'unit': 'pH'},
                'turbidity': {'max': 1.0, 'unit': 'NTU'},
                'tss': {'max': 10.0, 'unit': 'mg/L'},
                'tds': {'max': 1000.0, 'unit': 'mg/L'},
                'bod': {'max': 2.0, 'unit': 'mg/L'},
                'cod': {'max': 5.0, 'unit': 'mg/L'},
                'nitrogen': {'max': 10.0, 'unit': 'mg/L'},
                'phosphorus': {'max': 0.1, 'unit': 'mg/L'},
                'iron': {'max': 0.3, 'unit': 'mg/L'},
                'manganese': {'max': 0.1, 'unit': 'mg/L'},
                'chloride': {'max': 250.0, 'unit': 'mg/L'},
                'sulfate': {'max': 250.0, 'unit': 'mg/L'},
                'arsenic': {'max': 0.01, 'unit': 'mg/L'},
                'lead': {'max': 0.01, 'unit': 'mg/L'},
                'mercury': {'max': 0.001, 'unit': 'mg/L'},
                'cadmium': {'max': 0.003, 'unit': 'mg/L'},
                'chromium': {'max': 0.05, 'unit': 'mg/L'},
                'nickel': {'max': 0.02, 'unit': 'mg/L'},
                'copper': {'max': 2.0, 'unit': 'mg/L'},
                'zinc': {'max': 3.0, 'unit': 'mg/L'}
            },

            # Endüstriyel kullanım standartları
            'industrial_water': {
                'ph': {'min': 6.0, 'max': 9.0, 'unit': 'pH'},
                'turbidity': {'max': 5.0, 'unit': 'NTU'},
                'tss': {'max': 50.0, 'unit': 'mg/L'},
                'tds': {'max': 2000.0, 'unit': 'mg/L'},
                'bod': {'max': 30.0, 'unit': 'mg/L'},
                'cod': {'max': 100.0, 'unit': 'mg/L'},
                'nitrogen': {'max': 50.0, 'unit': 'mg/L'},
                'phosphorus': {'max': 1.0, 'unit': 'mg/L'}
            },

            # Tarımsal kullanım standartları
            'agricultural_water': {
                'ph': {'min': 6.0, 'max': 8.5, 'unit': 'pH'},
                'turbidity': {'max': 10.0, 'unit': 'NTU'},
                'tss': {'max': 100.0, 'unit': 'mg/L'},
                'tds': {'max': 2000.0, 'unit': 'mg/L'},
                'nitrogen': {'max': 30.0, 'unit': 'mg/L'},
                'phosphorus': {'max': 2.0, 'unit': 'mg/L'},
                'salinity': {'max': 2000.0, 'unit': 'mg/L'}
            },

            # Atık su deşarj standartları
            'wastewater_discharge': {
                'ph': {'min': 6.0, 'max': 9.0, 'unit': 'pH'},
                'tss': {'max': 30.0, 'unit': 'mg/L'},
                'bod': {'max': 20.0, 'unit': 'mg/L'},
                'cod': {'max': 100.0, 'unit': 'mg/L'},
                'nitrogen': {'max': 15.0, 'unit': 'mg/L'},
                'phosphorus': {'max': 1.0, 'unit': 'mg/L'},
                'oil_grease': {'max': 10.0, 'unit': 'mg/L'},
                'phenol': {'max': 0.1, 'unit': 'mg/L'}
            }
        }

        use_standards = standards.get(water_use, standards['industrial_water'])
        parameter_standard = use_standards.get(parameter.lower())

        if parameter_standard:
            return {
                'parameter': parameter,
                'water_use': water_use,
                'standard': parameter_standard,
                'compliance_threshold': parameter_standard.get('max', parameter_standard.get('min'))
            }

        return None

    # ==================== ÖZEL FAKTÖR YÖNETİMİ ====================

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

            query += " ORDER BY region DESC, created_at DESC LIMIT 1"

            cursor.execute(query, params)
            result = cursor.fetchone()

            return result[0] if result else None

        except Exception as e:
            logging.error(f"Ozel su faktoru getirme hatasi: {e}")
            return None
        finally:
            conn.close()

    def add_custom_factor(self, factor_type: str, water_source: str, factor_name: str,
                         factor_value: float, unit: str, reference: str = None,
                         region: str = None, validity_start: str = None,
                         validity_end: str = None, notes: str = None) -> int:
        """Özel su faktörü ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO custom_water_factors 
                (factor_type, water_source, factor_name, factor_value, unit, reference,
                 region, validity_start, validity_end, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                factor_type, water_source, factor_name, factor_value, unit, reference,
                region, validity_start, validity_end, notes or ''
            ))

            factor_id = cursor.lastrowid
            conn.commit()
            return factor_id

        except Exception as e:
            logging.error(f"Ozel su faktoru ekleme hatasi: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_all_custom_factors(self, factor_type: str = None) -> List[Dict]:
        """Tüm özel su faktörlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """
                SELECT id, factor_type, water_source, factor_name, factor_value, unit,
                       reference, region, validity_start, validity_end, is_active, notes, created_at
                FROM custom_water_factors
            """
            params = []

            if factor_type:
                query += " WHERE factor_type = ?"
                params.append(factor_type)

            query += " ORDER BY factor_type, factor_name, created_at DESC"

            cursor.execute(query, params)

            factors = []
            for row in cursor.fetchall():
                factors.append({
                    'id': row[0],
                    'factor_type': row[1],
                    'water_source': row[2],
                    'factor_name': row[3],
                    'factor_value': row[4],
                    'unit': row[5],
                    'reference': row[6],
                    'region': row[7],
                    'validity_start': row[8],
                    'validity_end': row[9],
                    'is_active': bool(row[10]),
                    'notes': row[11],
                    'created_at': row[12]
                })

            return factors

        except Exception as e:
            logging.error(f"Ozel su faktorleri getirme hatasi: {e}")
            return []
        finally:
            conn.close()

    def update_custom_factor(self, factor_id: int, **updates) -> bool:
        """Özel su faktörünü güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            allowed_fields = ['factor_value', 'unit', 'reference', 'region',
                            'validity_start', 'validity_end', 'is_active', 'notes']

            update_fields = []
            values = []

            for field, value in updates.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = ?")
                    values.append(value)

            if not update_fields:
                return False

            values.append(factor_id)

            query = f"""
                UPDATE custom_water_factors 
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """

            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logging.error(f"Ozel su faktoru guncelleme hatasi: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_custom_factor(self, factor_id: int) -> bool:
        """Özel su faktörünü sil"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM custom_water_factors WHERE id = ?", (factor_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Ozel su faktoru silme hatasi: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==================== SU VERİMLİLİĞİ FAKTÖRLERİ ====================

    def get_efficiency_benchmarks(self, industry_type: str, process_type: str = None) -> Dict:
        """Su verimliliği kıyaslama değerleri getir"""
        # Endüstri bazlı su verimliliği kıyaslama değerleri
        benchmarks = {
            'textile': {
                'dyeing': {'water_intensity': 150, 'unit': 'L/kg'},
                'finishing': {'water_intensity': 50, 'unit': 'L/kg'},
                'washing': {'water_intensity': 100, 'unit': 'L/kg'}
            },
            'food': {
                'processing': {'water_intensity': 5, 'unit': 'L/kg'},
                'cleaning': {'water_intensity': 10, 'unit': 'L/kg'},
                'cooling': {'water_intensity': 2, 'unit': 'L/kg'}
            },
            'chemical': {
                'production': {'water_intensity': 50, 'unit': 'L/kg'},
                'cooling': {'water_intensity': 10, 'unit': 'L/kg'},
                'cleaning': {'water_intensity': 20, 'unit': 'L/kg'}
            },
            'metal': {
                'processing': {'water_intensity': 10, 'unit': 'L/kg'},
                'cooling': {'water_intensity': 5, 'unit': 'L/kg'},
                'cleaning': {'water_intensity': 3, 'unit': 'L/kg'}
            },
            'paper': {
                'production': {'water_intensity': 50, 'unit': 'L/kg'},
                'pulping': {'water_intensity': 100, 'unit': 'L/kg'},
                'bleaching': {'water_intensity': 30, 'unit': 'L/kg'}
            }
        }

        industry_benchmark = benchmarks.get(industry_type.lower(), {})

        if process_type:
            process_benchmark = industry_benchmark.get(process_type.lower())
            if process_benchmark:
                return {
                    'industry': industry_type,
                    'process': process_type,
                    'benchmark': process_benchmark,
                    'category': 'process_specific'
                }

        # Endüstri geneli ortalama
        if industry_benchmark:
            avg_intensity = sum(b['water_intensity'] for b in industry_benchmark.values()) / len(industry_benchmark)
            return {
                'industry': industry_type,
                'process': 'average',
                'benchmark': {'water_intensity': avg_intensity, 'unit': 'L/kg'},
                'category': 'industry_average'
            }

        return {
            'industry': industry_type,
            'process': process_type or 'general',
            'benchmark': {'water_intensity': 10, 'unit': 'L/kg'},
            'category': 'default'
        }

    def get_recycling_potential(self, water_type: str, treatment_level: str) -> Dict:
        """Geri dönüşüm potansiyeli getir"""
        # Su türü ve arıtma seviyesine göre geri dönüşüm potansiyeli
        recycling_potentials = {
            'cooling_water': {
                'basic_treatment': {'reuse_rate': 0.8, 'quality_level': 'industrial'},
                'advanced_treatment': {'reuse_rate': 0.95, 'quality_level': 'process'},
                'ultra_treatment': {'reuse_rate': 0.99, 'quality_level': 'potable'}
            },
            'process_water': {
                'basic_treatment': {'reuse_rate': 0.6, 'quality_level': 'non_contact'},
                'advanced_treatment': {'reuse_rate': 0.85, 'quality_level': 'industrial'},
                'ultra_treatment': {'reuse_rate': 0.95, 'quality_level': 'process'}
            },
            'wastewater': {
                'basic_treatment': {'reuse_rate': 0.4, 'quality_level': 'irrigation'},
                'advanced_treatment': {'reuse_rate': 0.7, 'quality_level': 'industrial'},
                'ultra_treatment': {'reuse_rate': 0.9, 'quality_level': 'process'}
            },
            'rainwater': {
                'basic_treatment': {'reuse_rate': 0.9, 'quality_level': 'non_contact'},
                'advanced_treatment': {'reuse_rate': 0.95, 'quality_level': 'industrial'},
                'ultra_treatment': {'reuse_rate': 0.98, 'quality_level': 'potable'}
            }
        }

        water_type_potential = recycling_potentials.get(water_type.lower(), {})
        treatment_potential = water_type_potential.get(treatment_level.lower())

        if treatment_potential:
            return {
                'water_type': water_type,
                'treatment_level': treatment_level,
                'potential': treatment_potential,
                'feasibility': 'high' if treatment_potential['reuse_rate'] > 0.7 else 'medium'
            }

        return {
            'water_type': water_type,
            'treatment_level': treatment_level,
            'potential': {'reuse_rate': 0.5, 'quality_level': 'unknown'},
            'feasibility': 'low'
        }
