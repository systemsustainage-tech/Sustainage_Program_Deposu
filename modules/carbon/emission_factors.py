#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMİSYON FAKTÖRLERİ VERİTABANI
GHG Protocol ve IPCC standartlarına uygun emisyon faktörleri
"""

import logging
import os
import sqlite3
from typing import Dict, Optional
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EmissionFactors:
    """Emisyon faktörleri yönetimi - tCO2e hesaplamaları için"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    # SCOPE 1 - Sabit Yakma Faktörleri (tCO2e/unit)
    SCOPE1_STATIONARY = {
        'natural_gas': {
            'name': 'Doğalgaz',
            'unit': 'm3',
            'factor_co2': 0.00202,  # tCO2/m3
            'factor_ch4': 0.000001,  # tCH4/m3
            'factor_n2o': 0.0000001,  # tN2O/m3
            'source': 'IPCC 2006'
        },
        'diesel': {
            'name': 'Dizel',
            'unit': 'litre',
            'factor_co2': 0.00268,  # tCO2/litre
            'factor_ch4': 0.000003,
            'factor_n2o': 0.0000002,
            'source': 'GHG Protocol'
        },
        'fuel_oil': {
            'name': 'Fuel Oil',
            'unit': 'litre',
            'factor_co2': 0.00317,  # tCO2/litre
            'factor_ch4': 0.000003,
            'factor_n2o': 0.0000002,
            'source': 'GHG Protocol'
        },
        'lpg': {
            'name': 'LPG',
            'unit': 'kg',
            'factor_co2': 0.00303,  # tCO2/kg
            'factor_ch4': 0.000001,
            'factor_n2o': 0.0000001,
            'source': 'GHG Protocol'
        },
        'coal': {
            'name': 'Kömür',
            'unit': 'ton',
            'factor_co2': 2.42,  # tCO2/ton
            'factor_ch4': 0.003,
            'factor_n2o': 0.0015,
            'source': 'IPCC 2006'
        }
    }

    # SCOPE 1 - Mobil Yakma Faktörleri
    SCOPE1_MOBILE = {
        'gasoline': {
            'name': 'Benzin',
            'unit': 'litre',
            'factor_co2': 0.00231,  # tCO2/litre
            'factor_ch4': 0.000010,
            'factor_n2o': 0.0000005,
            'source': 'GHG Protocol'
        },
        'diesel_vehicle': {
            'name': 'Dizel (Araç)',
            'unit': 'litre',
            'factor_co2': 0.00268,
            'factor_ch4': 0.000003,
            'factor_n2o': 0.0000005,
            'source': 'GHG Protocol'
        }
    }

    # SCOPE 1 - Kaçak Emisyonlar (Refrigerants)
    SCOPE1_FUGITIVE = {
        'r134a': {
            'name': 'R-134a (HFC)',
            'unit': 'kg',
            'factor_gwp': 1430,  # Global Warming Potential (CO2e)
            'source': 'IPCC AR5'
        },
        'r404a': {
            'name': 'R-404A (HFC)',
            'unit': 'kg',
            'factor_gwp': 3922,
            'source': 'IPCC AR5'
        },
        'r410a': {
            'name': 'R-410A (HFC)',
            'unit': 'kg',
            'factor_gwp': 2088,
            'source': 'IPCC AR5'
        }
    }

    # SCOPE 2 - Elektrik Faktörleri (ülke bazlı)
    SCOPE2_ELECTRICITY = {
        'turkey': {
            'name': 'Türkiye Elektrik Şebekesi',
            'unit': 'kWh',
            'factor': 0.000475,  # tCO2/kWh (2023 grid average)
            'source': 'TEİAŞ 2023'
        },
        'eu_average': {
            'name': 'AB Ortalama',
            'unit': 'kWh',
            'factor': 0.000295,
            'source': 'IEA 2023'
        },
        'usa_average': {
            'name': 'ABD Ortalama',
            'unit': 'kWh',
            'factor': 0.000417,
            'source': 'EPA 2023'
        },
        'renewable': {
            'name': 'Yenilenebilir Enerji',
            'unit': 'kWh',
            'factor': 0.00001,  # Neredeyse sıfır
            'source': 'GHG Protocol'
        }
    }

    # SCOPE 2 - Isıtma/Soğutma
    SCOPE2_HEATING = {
        'district_heating': {
            'name': 'Bölgesel Isınma',
            'unit': 'MWh',
            'factor': 0.215,  # tCO2/MWh
            'source': 'GHG Protocol'
        },
        'steam': {
            'name': 'Buhar',
            'unit': 'ton',
            'factor': 0.078,  # tCO2/ton
            'source': 'GHG Protocol'
        }
    }

    # SCOPE 3 - Kategori Faktörleri
    SCOPE3_CATEGORIES = {
        # Kategori 1: Satın Alınan Mallar
        'purchased_goods': {
            'name': 'Satın Alınan Mallar ve Hizmetler',
            'calculation_method': 'spend_based',  # veya supplier_specific
            'default_factor': 0.45,  # tCO2e/$1000 spend
            'source': 'EPA EEIO'
        },
        # Kategori 2: Sermaye Malları
        'capital_goods': {
            'name': 'Sermaye Malları',
            'calculation_method': 'spend_based',
            'default_factor': 0.38,
            'source': 'EPA EEIO'
        },
        # Kategori 3: Yakıt ve Enerji
        'fuel_energy': {
            'name': 'Yakıt ve Enerji ile İlgili Aktiviteler',
            'calculation_method': 'average_data',
            'default_factor': 0.12,  # kWh başına upstream emissions
            'source': 'GHG Protocol'
        },
        # Kategori 4: Upstream Taşıma
        'upstream_transport': {
            'name': 'Upstream Taşıma ve Dağıtım',
            'calculation_method': 'distance_based',
            'default_factor': 0.062,  # tCO2e/ton-km (kamyon)
            'source': 'GLEC Framework'
        },
        # Kategori 5: Atık
        'waste': {
            'name': 'Operasyonlarda Oluşan Atık',
            'calculation_method': 'waste_type',
            'factors': {
                'landfill': 0.57,  # tCO2e/ton
                'incineration': 0.03,
                'recycling': 0.01,
                'composting': 0.02
            },
            'source': 'EPA WARM'
        },
        # Kategori 6: İş Seyahatleri
        'business_travel': {
            'name': 'İş Seyahatleri',
            'calculation_method': 'distance_based',
            'factors': {
                'flight_short': 0.000258,  # tCO2e/pkm (<500km)
                'flight_medium': 0.000187,  # (500-3700km)
                'flight_long': 0.000152,    # (>3700km)
                'car': 0.000192,            # tCO2e/km
                'train': 0.000041           # tCO2e/pkm
            },
            'source': 'DEFRA 2023',
            'spend_factor_usd': 0.000200,  # tCO2e/USD (EEIO approx.)
            'spend_unit': 'USD',
            'spend_source': 'EPA EEIO (tahmini)'
        },
        # Kategori 7: Çalışan Ulaşımı
        'employee_commuting': {
            'name': 'Çalışan İşe Gidiş-Geliş',
            'calculation_method': 'distance_based',
            'factors': {
                'car_gasoline': 0.000192,
                'car_diesel': 0.000171,
                'bus': 0.000089,
                'metro': 0.000041,
                'walking_cycling': 0.0
            },
            'source': 'DEFRA 2023'
        },
        # Kategori 9: Downstream Taşıma
        'downstream_transport': {
            'name': 'Downstream Taşıma ve Dağıtım',
            'calculation_method': 'distance_based',
            'default_factor': 0.062,
            'source': 'GLEC Framework'
        },
        # Kategori 11: Satılan Ürünlerin Kullanımı
        'use_of_sold_products': {
            'name': 'Satılan Ürünlerin Kullanımı',
            'calculation_method': 'product_specific',
            'default_factor': 0.0,  # Ürüne özel hesaplanmalı
            'source': 'GHG Protocol'
        },
        # Kategori 12: Satılan Ürünlerin Ömür Sonu
        'end_of_life': {
            'name': 'Satılan Ürünlerin Ömür Sonu İşleme',
            'calculation_method': 'waste_type',
            'default_factor': 0.35,
            'source': 'EPA WARM'
        }
    }

    def get_emission_factor(self, scope: str, category: str, fuel_type: str) -> Optional[Dict]:
        """
        Belirli bir emisyon faktörünü getir
        
        Args:
            scope: 'scope1', 'scope2', 'scope3'
            category: 'stationary', 'mobile', 'fugitive', 'electricity', etc.
            fuel_type: 'natural_gas', 'diesel', etc.
        
        Returns:
            Dict with factor information or None
        """
        if scope == 'scope1':
            if category == 'stationary':
                return self.SCOPE1_STATIONARY.get(fuel_type)
            elif category == 'mobile':
                return self.SCOPE1_MOBILE.get(fuel_type)
            elif category == 'fugitive':
                return self.SCOPE1_FUGITIVE.get(fuel_type)
        elif scope == 'scope2':
            if category == 'electricity':
                return self.SCOPE2_ELECTRICITY.get(fuel_type)
            elif category == 'heating':
                return self.SCOPE2_HEATING.get(fuel_type)
        elif scope == 'scope3':
            return self.SCOPE3_CATEGORIES.get(fuel_type)

        return None

    def calculate_co2e(self, scope: str, category: str, fuel_type: str,
                      quantity: float) -> Dict:
        """
        CO2 eşdeğer emisyon hesapla
        
        Args:
            scope: Scope türü
            category: Kategori
            fuel_type: Yakıt/kaynak türü
            quantity: Miktar
        
        Returns:
            {
                'co2': float,
                'ch4': float,
                'n2o': float,
                'co2e': float,  # Total CO2 equivalent
                'unit': str
            }
        """
        factor_data = self.get_emission_factor(scope, category, fuel_type)

        if not factor_data:
            raise ValueError(f"Emisyon faktörü bulunamadı: {scope}/{category}/{fuel_type}")

        result = {
            'co2': 0.0,
            'ch4': 0.0,
            'n2o': 0.0,
            'co2e': 0.0,
            'unit': factor_data.get('unit', ''),
            'source': factor_data.get('source', '')
        }

        # Scope 1 ve 2 için ayrıntılı hesaplama
        if scope in ['scope1', 'scope2']:
            if 'factor_co2' in factor_data:
                result['co2'] = quantity * factor_data['factor_co2']
            if 'factor_ch4' in factor_data:
                result['ch4'] = quantity * factor_data['factor_ch4']
            if 'factor_n2o' in factor_data:
                result['n2o'] = quantity * factor_data['factor_n2o']

            # GWP faktörleri (IPCC AR5)
            # CO2 = 1, CH4 = 25, N2O = 298
            result['co2e'] = result['co2'] + (result['ch4'] * 25) + (result['n2o'] * 298)

        # Fugitive emissions için (direkt GWP)
        elif scope == 'scope1' and category == 'fugitive':
            if 'factor_gwp' in factor_data:
                result['co2e'] = quantity * factor_data['factor_gwp'] / 1000  # kg -> ton

        # Scope 2 elektrik için basit faktör
        elif scope == 'scope2' and 'factor' in factor_data:
            result['co2e'] = quantity * factor_data['factor']

        # Scope 3 için basit faktör
        elif scope == 'scope3':
            if 'default_factor' in factor_data:
                result['co2e'] = quantity * factor_data['default_factor']
            elif 'factors' in factor_data:
                # Alt kategoriler var, default olarak ilkini kullan
                first_factor = list(factor_data['factors'].values())[0]
                result['co2e'] = quantity * first_factor

        return result

    def create_emission_factors_table(self) -> bool:
        """Özel emisyon faktörleri için veritabanı tablosu oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_emission_factors (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER,
                    scope TEXT NOT NULL,             -- scope1, scope2, scope3
                    category TEXT NOT NULL,          -- stationary, mobile, etc.
                    fuel_type TEXT NOT NULL,
                    factor_co2 REAL,
                    factor_ch4 REAL,
                    factor_n2o REAL,
                    factor_co2e REAL,
                    unit TEXT,
                    source TEXT,
                    valid_from DATE,
                    valid_until DATE,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            conn.commit()
            logging.info("[OK] Ozel emisyon faktorleri tablosu olusturuldu")
            return True

        except Exception as e:
            logging.info(f"Emisyon faktörleri tablosu oluşturulamadı: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def save_custom_factor(self, company_id: int, scope: str, category: str,
                          fuel_type: str, factor_data: Dict) -> int:
        """Özel emisyon faktörü kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO custom_emission_factors 
                (company_id, scope, category, fuel_type, factor_co2, factor_ch4, 
                 factor_n2o, factor_co2e, unit, source, valid_from, valid_until, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, scope, category, fuel_type,
                factor_data.get('factor_co2'),
                factor_data.get('factor_ch4'),
                factor_data.get('factor_n2o'),
                factor_data.get('factor_co2e'),
                factor_data.get('unit'),
                factor_data.get('source'),
                factor_data.get('valid_from'),
                factor_data.get('valid_until'),
                factor_data.get('notes')
            ))
            
            last_id = cursor.lastrowid
            conn.commit()
            return last_id
        except Exception as e:
            logging.error(f"Özel faktör kaydetme hatası: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()
