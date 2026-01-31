#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Karbon Ayak İzi Hesaplayıcı
GHG Protocol standartlarına göre Scope 1, 2 ve 3 emisyonlarını hesaplar
"""

import logging
import os
import sqlite3
from typing import Dict, List

from utils.language_manager import LanguageManager
from config.database import DB_PATH


class CarbonCalculator:
    """
    Karbon emisyon hesaplama motoru
    
    Kapsam 1 (Scope 1): Doğrudan emisyonlar
    - Şirket araçları (yakıt)
    - Kazan ve fırınlar (doğalgaz, kömür)
    - Kaçak emisyonlar (soğutucu gazlar)
    
    Kapsam 2 (Scope 2): Dolaylı enerji emisyonları
    - Satın alınan elektrik
    - Satın alınan ısıtma/soğutma
    
    Kapsam 3 (Scope 3): Diğer dolaylı emisyonlar
    - İş seyahatleri
    - Çalışan işe geliş-gidiş
    - Tedarik zinciri
    - Nakliye
    """

    # Emisyon faktörleri (kg CO2e/birim)
    EMISSION_FACTORS = {
        # SCOPE 1 - Yakıtlar
        'gasoline': 2.31,      # kg CO2e/litre (benzin)
        'diesel': 2.68,        # kg CO2e/litre (mazot)
        'natural_gas': 2.02,   # kg CO2e/m³ (doğalgaz)
        'lpg': 1.51,           # kg CO2e/litre (LPG)
        'coal': 2419.0,        # kg CO2e/ton (kömür)

        # Soğutucu gazlar (kg CO2e/kg)
        'r410a': 2088.0,       # R-410A
        'r134a': 1430.0,       # R-134a
        'r404a': 3922.0,       # R-404A

        # SCOPE 2 - Elektrik (Türkiye grid average)
        'electricity': 0.434,  # kg CO2e/kWh
        'steam': 0.185,        # kg CO2e/kWh (buhar)

        # SCOPE 3 - Ulaşım
        'flight_domestic': 0.255,      # kg CO2e/km
        'flight_international': 0.195,  # kg CO2e/km
        'train': 0.041,                 # kg CO2e/km
        'bus': 0.089,                   # kg CO2e/km
        'car_commute': 0.192,           # kg CO2e/km

        # SCOPE 3 - Nakliye
        'truck': 0.062,        # kg CO2e/ton-km
        'ship': 0.016,         # kg CO2e/ton-km
        'rail_freight': 0.022, # kg CO2e/ton-km
    }

    def __init__(self, db_path: str = None) -> None:
        """
        Hesaplayıcıyı başlat
        
        Args:
            db_path: Veritabanı yolu
        """
        self.lm = LanguageManager()
        self.db_path = db_path or DB_PATH
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Karbon verileri için tabloları oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Karbon emisyon kayıtları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    scope INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    emission_factor REAL,
                    co2e_kg REAL NOT NULL,
                    period_start TEXT,
                    period_end TEXT,
                    description TEXT,
                    source TEXT,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Karbon özeti
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    scope1_total REAL DEFAULT 0,
                    scope2_total REAL DEFAULT 0,
                    scope3_total REAL DEFAULT 0,
                    total_emissions REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, year)
                )
            """)

            conn.commit()
            logging.info(f"[OK] {self.lm.tr('carbon_emission_tables_ready', 'Karbon emisyon tabloları hazır')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('table_creation_error', 'Tablo oluşturma')}: {e}")
            conn.rollback()
        finally:
            conn.close()

    def calculate_scope1_fuel(self, fuel_type: str, amount: float, unit: str = 'litre') -> Dict:
        """
        Scope 1: Yakıt yanması emisyonları
        
        Args:
            fuel_type: Yakıt tipi (gasoline, diesel, natural_gas, lpg, coal)
            amount: Miktar
            unit: Birim (litre, m3, ton)
        
        Returns:
            Dict: {co2e_kg, emission_factor, details}
        """
        if fuel_type not in self.EMISSION_FACTORS:
            raise ValueError(f"{self.lm.tr('unknown_fuel_type', 'Bilinmeyen yakıt tipi')}: {fuel_type}")

        factor = self.EMISSION_FACTORS[fuel_type]
        co2e_kg = amount * factor
        
        category = self.lm.tr('stationary_combustion', 'Sabit Yanma') if fuel_type in ['natural_gas', 'coal'] else self.lm.tr('mobile_combustion', 'Mobil Yanma')

        return {
            'co2e_kg': round(co2e_kg, 2),
            'co2e_ton': round(co2e_kg / 1000, 3),
            'emission_factor': factor,
            'amount': amount,
            'unit': unit,
            'fuel_type': fuel_type,
            'scope': 1,
            'category': category
        }

    def calculate_scope1_refrigerant(self, refrigerant_type: str, amount_kg: float) -> Dict:
        """
        Scope 1: Soğutucu gaz kaçakları
        
        Args:
            refrigerant_type: Gaz tipi (r410a, r134a, r404a)
            amount_kg: Kaçak miktar (kg)
        
        Returns:
            Dict: Emisyon hesabı
        """
        if refrigerant_type not in self.EMISSION_FACTORS:
            raise ValueError(f"{self.lm.tr('unknown_refrigerant', 'Bilinmeyen soğutucu gaz')}: {refrigerant_type}")

        factor = self.EMISSION_FACTORS[refrigerant_type]
        co2e_kg = amount_kg * factor

        return {
            'co2e_kg': round(co2e_kg, 2),
            'co2e_ton': round(co2e_kg / 1000, 3),
            'emission_factor': factor,
            'amount': amount_kg,
            'unit': 'kg',
            'refrigerant_type': refrigerant_type,
            'scope': 1,
            'category': self.lm.tr('fugitive_emissions', 'Kaçak Emisyonlar')
        }

    def calculate_scope2_electricity(self, kwh: float, renewable_percent: float = 0) -> Dict:
        """
        Scope 2: Elektrik tüketimi
        
        Args:
            kwh: Elektrik tüketimi (kWh)
            renewable_percent: Yenilenebilir enerji oranı (0-100)
        
        Returns:
            Dict: Emisyon hesabı
        """
        # Yenilenebilir enerji emisyon faktörü sıfır
        grid_kwh = kwh * (1 - renewable_percent / 100)

        factor = self.EMISSION_FACTORS['electricity']
        co2e_kg = grid_kwh * factor

        return {
            'co2e_kg': round(co2e_kg, 2),
            'co2e_ton': round(co2e_kg / 1000, 3),
            'emission_factor': factor,
            'amount': kwh,
            'grid_kwh': round(grid_kwh, 2),
            'renewable_kwh': round(kwh * renewable_percent / 100, 2),
            'renewable_percent': renewable_percent,
            'unit': 'kWh',
            'scope': 2,
            'category': self.lm.tr('purchased_electricity', 'Satın Alınan Elektrik')
        }

    def calculate_scope3_travel(self, travel_type: str, distance_km: float) -> Dict:
        """
        Scope 3: İş seyahatleri ve çalışan ulaşımı
        
        Args:
            travel_type: Ulaşım tipi (flight_domestic, flight_international, train, bus, car_commute)
            distance_km: Mesafe (km)
        
        Returns:
            Dict: Emisyon hesabı
        """
        if travel_type not in self.EMISSION_FACTORS:
            raise ValueError(f"{self.lm.tr('unknown_transport_type', 'Bilinmeyen ulaşım tipi')}: {travel_type}")

        factor = self.EMISSION_FACTORS[travel_type]
        co2e_kg = distance_km * factor
        
        category = self.lm.tr('business_travel', 'İş Seyahatleri') if 'flight' in travel_type else self.lm.tr('employee_commuting', 'Çalışan İşe Geliş-Gidiş')

        return {
            'co2e_kg': round(co2e_kg, 2),
            'co2e_ton': round(co2e_kg / 1000, 3),
            'emission_factor': factor,
            'amount': distance_km,
            'unit': 'km',
            'travel_type': travel_type,
            'scope': 3,
            'category': category
        }

    def calculate_scope3_logistics(self, transport_type: str, weight_ton: float, distance_km: float) -> Dict:
        """
        Scope 3: Lojistik ve nakliye
        
        Args:
            transport_type: Taşıma tipi (truck, ship, rail_freight)
            weight_ton: Ağırlık (ton)
            distance_km: Mesafe (km)
        
        Returns:
            Dict: Emisyon hesabı
        """
        if transport_type not in self.EMISSION_FACTORS:
            raise ValueError(f"{self.lm.tr('unknown_transport_type', 'Bilinmeyen taşıma tipi')}: {transport_type}")

        factor = self.EMISSION_FACTORS[transport_type]
        ton_km = weight_ton * distance_km
        co2e_kg = ton_km * factor

        return {
            'co2e_kg': round(co2e_kg, 2),
            'co2e_ton': round(co2e_kg / 1000, 3),
            'emission_factor': factor,
            'weight_ton': weight_ton,
            'distance_km': distance_km,
            'ton_km': ton_km,
            'transport_type': transport_type,
            'scope': 3,
            'category': self.lm.tr('logistics_and_transport', 'Lojistik ve Nakliye')
        }

    def save_emission(self, company_id: int, emission_data: Dict, period_start: str = None,
                     period_end: str = None, description: str = None, created_by: int = None) -> int:
        """
        Emisyon kaydını veritabanına kaydet
        
        Args:
            company_id: Firma ID
            emission_data: calculate_* fonksiyonlarından dönen veri
            period_start: Dönem başlangıcı (YYYY-MM-DD)
            period_end: Dönem sonu (YYYY-MM-DD)
            description: Açıklama
            created_by: Kaydı oluşturan kullanıcı ID
        
        Returns:
            int: Kayıt ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO carbon_emissions (
                    company_id, scope, category, subcategory, amount, unit,
                    emission_factor, co2e_kg, period_start, period_end,
                    description, created_by
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                emission_data['scope'],
                emission_data['category'],
                emission_data.get('fuel_type') or emission_data.get('travel_type') or
                emission_data.get('transport_type') or emission_data.get('refrigerant_type'),
                emission_data['amount'],
                emission_data['unit'],
                emission_data['emission_factor'],
                emission_data['co2e_kg'],
                period_start,
                period_end,
                description,
                created_by
            ))

            conn.commit()
            emission_id = cursor.lastrowid

            logging.info(f"[OK] {self.lm.tr('emission_record_added', 'Emisyon kaydı eklendi')}: {emission_id}")

            # Özeti güncelle
            if period_start:
                year = int(period_start.split('-')[0])
                self._update_summary(company_id, year)

            return emission_id

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('emission_record_error', 'Emisyon kayıt hatası')}: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def _update_summary(self, company_id: int, year: int) -> None:
        """Yıllık karbon özetini güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Scope bazında toplamları hesapla
            cursor.execute("""
                SELECT 
                    scope,
                    SUM(co2e_kg)
                FROM carbon_emissions
                WHERE company_id = ?
                AND strftime('%Y', period_start) = ?
                GROUP BY scope
            """, (company_id, str(year)))

            scope_totals = {row[0]: row[1] for row in cursor.fetchall()}

            scope1 = scope_totals.get(1, 0)
            scope2 = scope_totals.get(2, 0)
            scope3 = scope_totals.get(3, 0)
            total = scope1 + scope2 + scope3

            # Özeti güncelle veya oluştur
            cursor.execute("""
                INSERT INTO carbon_summary (
                    company_id, year, scope1_total, scope2_total, scope3_total, total_emissions
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id, year) DO UPDATE SET
                    scope1_total = excluded.scope1_total,
                    scope2_total = excluded.scope2_total,
                    scope3_total = excluded.scope3_total,
                    total_emissions = excluded.total_emissions,
                    updated_at = CURRENT_TIMESTAMP
            """, (company_id, year, scope1, scope2, scope3, total))

            conn.commit()

        except Exception as e:
            logging.error(f"[HATA] Ozet guncelleme: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_company_summary(self, company_id: int, year: int = None) -> Dict:
        """
        Firma karbon özeti
        
        Args:
            company_id: Firma ID
            year: Yıl (None ise tüm yıllar)
        
        Returns:
            Dict: Özet veriler
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if year:
                cursor.execute("""
                    SELECT scope1_total, scope2_total, scope3_total, total_emissions
                    FROM carbon_summary
                    WHERE company_id = ? AND year = ?
                """, (company_id, year))
            else:
                cursor.execute("""
                    SELECT 
                        SUM(scope1_total), SUM(scope2_total), 
                        SUM(scope3_total), SUM(total_emissions)
                    FROM carbon_summary
                    WHERE company_id = ?
                """, (company_id,))

            row = cursor.fetchone()

            if not row or not row[0]:
                return {
                    'scope1_kg': 0, 'scope1_ton': 0,
                    'scope2_kg': 0, 'scope2_ton': 0,
                    'scope3_kg': 0, 'scope3_ton': 0,
                    'total_kg': 0, 'total_ton': 0,
                    'year': year
                }

            return {
                'scope1_kg': round(row[0] or 0, 2),
                'scope1_ton': round((row[0] or 0) / 1000, 3),
                'scope2_kg': round(row[1] or 0, 2),
                'scope2_ton': round((row[1] or 0) / 1000, 3),
                'scope3_kg': round(row[2] or 0, 2),
                'scope3_ton': round((row[2] or 0) / 1000, 3),
                'total_kg': round(row[3] or 0, 2),
                'total_ton': round((row[3] or 0) / 1000, 3),
                'year': year
            }

        except Exception as e:
            logging.error(f"[HATA] Ozet alma: {e}")
            return {}
        finally:
            conn.close()

    def get_category_breakdown(self, company_id: int, year: int, scope: int = None) -> List[Dict]:
        """
        Kategori bazında emisyon dağılımı
        
        Args:
            company_id: Firma ID
            year: Yıl
            scope: Scope filtresi (None ise tüm scope'lar)
        
        Returns:
            List[Dict]: Kategori bazında veriler
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if scope:
                cursor.execute("""
                    SELECT 
                        category,
                        SUM(co2e_kg) as total_kg,
                        COUNT(*) as count
                    FROM carbon_emissions
                    WHERE company_id = ? 
                    AND strftime('%Y', period_start) = ?
                    AND scope = ?
                    GROUP BY category
                    ORDER BY total_kg DESC
                """, (company_id, str(year), scope))
            else:
                cursor.execute("""
                    SELECT 
                        category,
                        SUM(co2e_kg) as total_kg,
                        COUNT(*) as count
                    FROM carbon_emissions
                    WHERE company_id = ? 
                    AND strftime('%Y', period_start) = ?
                    GROUP BY category
                    ORDER BY total_kg DESC
                """, (company_id, str(year)))

            results = []
            for row in cursor.fetchall():
                results.append({
                    'category': row[0],
                    'co2e_kg': round(row[1], 2),
                    'co2e_ton': round(row[1] / 1000, 3),
                    'count': row[2]
                })

            return results

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('category_breakdown_error', 'Kategori dağılımı')}: {e}")
            return []
        finally:
            conn.close()

