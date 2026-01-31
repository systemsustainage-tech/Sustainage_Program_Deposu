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
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
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

    # SCOPE 2 - Elektrik (Şebeke) - Ülke Bazlı
    # 2024 IEA ve Enerji Bakanlığı verileri
    SCOPE2_ELECTRICITY = {
        'turkey': {
            'name': 'Türkiye Şebeke Elektriği',
            'unit': 'kWh',
            'factor': 0.442,  # kgCO2e/kWh (2023 ortalaması)
            'source': 'Enerji Bakanlığı / TEİAŞ'
        },
        'eu_mix': {
            'name': 'AB Ortalama',
            'unit': 'kWh',
            'factor': 0.255,  # kgCO2e/kWh
            'source': 'EEA'
        },
        'usa_mix': {
            'name': 'ABD Ortalama',
            'unit': 'kWh',
            'factor': 0.380,  # kgCO2e/kWh
            'source': 'EPA'
        },
        'china_mix': {
            'name': 'Çin Ortalama',
            'unit': 'kWh',
            'factor': 0.580,  # kgCO2e/kWh
            'source': 'IEA'
        },
        'renewable': {
            'name': 'Yenilenebilir (I-REC/YEK-G)',
            'unit': 'kWh',
            'factor': 0.0,
            'source': 'Sertifikalı'
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

    # SCOPE 3 - Diğer Dolaylı Emisyonlar (Kapsam 3)
    # GHG Protocol Corporate Value Chain (Scope 3) Standard
    SCOPE3_CATEGORIES = {
        # Kategori 1: Satın Alınan Ürün ve Hizmetler (Hammadde)
        'steel': {
            'category': '1. Satın Alınan Ürünler',
            'name': 'Çelik (Genel)',
            'unit': 'ton',
            'factor': 1.85,  # tCO2e/ton
            'source': 'World Steel Association'
        },
        'cement': {
            'category': '1. Satın Alınan Ürünler',
            'name': 'Çimento',
            'unit': 'ton',
            'factor': 0.90,  # tCO2e/ton
            'source': 'GCCA'
        },
        'paper': {
            'category': '1. Satın Alınan Ürünler',
            'name': 'Kağıt/Karton',
            'unit': 'ton',
            'factor': 0.92,  # tCO2e/ton
            'source': 'DEFRA'
        },
        'plastic_pet': {
            'category': '1. Satın Alınan Ürünler',
            'name': 'Plastik (PET)',
            'unit': 'ton',
            'factor': 2.16,  # tCO2e/ton
            'source': 'Plastics Europe'
        },
        # Eklenen: İthalat için Satın Alınan Mallar
        'purchased_goods': {
            'category': '1. Satın Alınan Ürünler',
            'name': 'Satın Alınan Mallar (Genel)',
            'unit': 'ton',
            'factor': 0.45,  # tCO2e/ton (Varsayılan)
            'source': 'EPA EEIO'
        },
        
        # Kategori 4 & 9: Nakliye (Upstream & Downstream)
        'road_freight': {
            'category': '4. Nakliye ve Dağıtım',
            'name': 'Karayolu Taşımacılığı (Kamyon/TIR)',
            'unit': 'tkm',  # ton-km
            'factor': 0.000085,  # tCO2e/tkm (85 g/tkm)
            'source': 'GLEC Framework'
        },
        'sea_freight': {
            'category': '4. Nakliye ve Dağıtım',
            'name': 'Denizyolu Taşımacılığı (Konteyner)',
            'unit': 'tkm',
            'factor': 0.000012,  # tCO2e/tkm (12 g/tkm)
            'source': 'GLEC Framework'
        },
        'air_freight': {
            'category': '4. Nakliye ve Dağıtım',
            'name': 'Havayolu Kargo (Uzun Mesafe)',
            'unit': 'tkm',
            'factor': 0.000602,  # tCO2e/tkm (602 g/tkm)
            'source': 'IATA / DEFRA'
        },
        'rail_freight': {
            'category': '4. Nakliye ve Dağıtım',
            'name': 'Demiryolu Taşımacılığı',
            'unit': 'tkm',
            'factor': 0.000022,  # tCO2e/tkm
            'source': 'DEFRA'
        },
        'transport': { # Genel Ulaşım/Nakliye
             'category': '4. Nakliye ve Dağıtım',
             'name': 'Nakliye (Genel)',
             'unit': 'tkm',
             'factor': 0.000062, # Ortalama
             'source': 'GLEC Framework'
        },

        # Kategori 6: İş Seyahatleri
        'air_travel_economy': {
            'category': '6. İş Seyahatleri',
            'name': 'Uçak (Ekonomi Sınıfı)',
            'unit': 'pkm',  # yolcu-km
            'factor': 0.000090,  # tCO2e/pkm (90 g/pkm)
            'source': 'ICAO'
        },
        'air_travel_business': {
            'category': '6. İş Seyahatleri',
            'name': 'Uçak (Business Sınıfı)',
            'unit': 'pkm',
            'factor': 0.000270,  # tCO2e/pkm
            'source': 'ICAO'
        },
        'car_rental': {
            'category': '6. İş Seyahatleri',
            'name': 'Kiralık Araç (Benzin)',
            'unit': 'km',
            'factor': 0.000170,  # tCO2e/km
            'source': 'DEFRA'
        },

        # Kategori 7: Personel Servisi
        'employee_commuting_bus': {
            'category': '7. Personel Servisi',
            'name': 'Personel Servisi (Otobüs)',
            'unit': 'pkm',
            'factor': 0.000028,  # tCO2e/pkm
            'source': 'DEFRA'
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

    def calculate_co2e(self, scope: str, category: str, fuel_type: str, quantity: float) -> Dict:
        """
        Verilen parametrelere göre CO2e hesapla
        """
        # Emisyon faktörünü bul
        factor_data = None
        
        if scope == 'scope1':
            if category == 'stationary':
                factor_data = self.SCOPE1_STATIONARY.get(fuel_type)
            elif category == 'mobile':
                factor_data = self.SCOPE1_MOBILE.get(fuel_type)
            elif category == 'fugitive':
                factor_data = self.SCOPE1_FUGITIVE.get(fuel_type)
                if factor_data:
                    # GWP hesabı: quantity * GWP / 1000 (kg -> tCO2e)
                    co2e = (quantity * factor_data['factor_gwp']) / 1000.0
                    return {
                        'co2': 0, 'ch4': 0, 'n2o': 0,
                        'co2e': co2e,
                        'unit': factor_data['unit'],
                        'source': factor_data['source']
                    }
        elif scope == 'scope2':
            if category == 'electricity':
                factor_data = self.SCOPE2_ELECTRICITY.get(fuel_type)
                if factor_data:
                    # Electricity: quantity (kWh) * factor (kgCO2e/kWh) / 1000 -> tCO2e
                    co2e = (quantity * factor_data['factor']) / 1000.0
                    return {
                        'co2': co2e, # Yaklaşık
                        'ch4': 0, 'n2o': 0,
                        'co2e': co2e,
                        'unit': factor_data['unit'],
                        'source': factor_data['source']
                    }
            elif category == 'heating':
                factor_data = self.SCOPE2_HEATING.get(fuel_type)
                if factor_data:
                    co2e = quantity * factor_data['factor']
                    return {
                        'co2': co2e, 'ch4': 0, 'n2o': 0,
                        'co2e': co2e,
                        'unit': factor_data['unit'],
                        'source': factor_data['source']
                    }
        elif scope == 'scope3':
            # Scope 3 Faktörleri
            factor_data = self.SCOPE3_CATEGORIES.get(fuel_type)
            if factor_data:
                # Genel çarpım: quantity * factor -> tCO2e
                # Faktörler zaten tCO2e cinsinden tanımlıysa direkt çarp
                co2e = quantity * factor_data['factor']
                return {
                    'co2': co2e, 
                    'ch4': 0, 'n2o': 0,
                    'co2e': co2e,
                    'unit': factor_data['unit'],
                    'source': factor_data['source']
                }

        if not factor_data:
            # Faktör bulunamadı
            # Özel faktör kontrolü (Veritabanı) - Henüz implemente edilmedi
            return {'co2': 0, 'ch4': 0, 'n2o': 0, 'co2e': 0, 'unit': 'unknown', 'source': 'unknown'}

        # Scope 1 Standart Hesaplama (Stationary/Mobile)
        # Faktörler tCO2/unit, tCH4/unit, tN2O/unit
        co2 = quantity * factor_data.get('factor_co2', 0)
        ch4 = quantity * factor_data.get('factor_ch4', 0)
        n2o = quantity * factor_data.get('factor_n2o', 0)
        
        # GWP (IPCC AR5): CO2=1, CH4=28, N2O=265
        co2e = co2 + (ch4 * 28) + (n2o * 265)
        
        return {
            'co2': co2,
            'ch4': ch4,
            'n2o': n2o,
            'co2e': co2e,
            'unit': factor_data['unit'],
            'source': factor_data['source']
        }

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
                          fuel_type: str, factor_data: Dict) -> Optional[int]:
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
                company_id,
                scope,
                category,
                fuel_type,
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

            factor_id = cursor.lastrowid
            conn.commit()
            return factor_id

        except Exception as e:
            logging.error(f"Özel faktör kaydetme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_custom_factor(self, company_id: int, scope: str,
                         category: str, fuel_type: str) -> Optional[Dict]:
        """Şirkete özel emisyon faktörünü getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT factor_co2, factor_ch4, factor_n2o, factor_co2e, unit, source
                FROM custom_emission_factors
                WHERE company_id = ? AND scope = ? AND category = ? AND fuel_type = ?
                  AND (valid_until IS NULL OR valid_until >= date('now'))
                ORDER BY created_at DESC
                LIMIT 1
            """, (company_id, scope, category, fuel_type))

            row = cursor.fetchone()
            if row:
                return {
                    'factor_co2': row[0],
                    'factor_ch4': row[1],
                    'factor_n2o': row[2],
                    'factor_co2e': row[3],
                    'unit': row[4],
                    'source': row[5]
                }
            return None

        except Exception as e:
            logging.error(f"Özel faktör getirme hatası: {e}")
            return None
        finally:
            conn.close()

    def list_all_factors(self, scope: str = None) -> Dict:
        """Tüm mevcut emisyon faktörlerini listele"""
        factors = {}

        if scope is None or scope == 'scope1':
            factors['scope1_stationary'] = self.SCOPE1_STATIONARY
            factors['scope1_mobile'] = self.SCOPE1_MOBILE
            factors['scope1_fugitive'] = self.SCOPE1_FUGITIVE
        
        if scope is None or scope == 'scope2':
            factors['scope2_electricity'] = self.SCOPE2_ELECTRICITY
            factors['scope2_heating'] = self.SCOPE2_HEATING
            
        if scope is None or scope == 'scope3':
            factors['scope3_categories'] = self.SCOPE3_CATEGORIES
            
        return factors
