#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KARBON YÖNETİCİ SINIFI
Karbon emisyon verilerinin yönetimi ve raporlama
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from .carbon_calculator import CarbonCalculator
from .emission_factors import EmissionFactors
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CarbonManager:
    """Karbon emisyon yönetimi ana sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.calculator = CarbonCalculator(db_path)
        self.emission_factors = EmissionFactors(db_path)
        self.create_tables()

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_tables(self) -> bool:
        """Karbon modülü tablolarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Emisyon kayıtları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_emissions (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,                -- 2024, 2024-Q1, etc.
                    scope TEXT NOT NULL,                 -- scope1, scope2, scope3
                    category TEXT NOT NULL,              -- stationary, mobile, fugitive, electricity, etc.
                    subcategory TEXT,                    -- Scope 3 için kategori numarası
                    fuel_type TEXT NOT NULL,             -- natural_gas, diesel, etc.
                    quantity REAL NOT NULL,              -- Miktar
                    unit TEXT NOT NULL,                  -- m3, litre, kWh, etc.
                    co2_emissions REAL,                  -- tCO2
                    ch4_emissions REAL,                  -- tCH4
                    n2o_emissions REAL,                  -- tN2O
                    co2e_emissions REAL NOT NULL,        -- Total tCO2e
                    emission_factor_source TEXT,         -- Faktör kaynağı
                    calculation_method TEXT,             -- Hesaplama metodu
                    data_quality TEXT DEFAULT 'measured', -- measured, estimated, default
                    source TEXT,                         -- Veri kaynağı
                    evidence_file TEXT,                  -- Kanıt dosyası
                    data_json TEXT,                      -- Ek veriler (JSON)
                    verified BOOLEAN DEFAULT 0,
                    verified_by TEXT,
                    verified_at TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 2. Karbon hedefleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_targets (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    target_name TEXT NOT NULL,
                    target_description TEXT,
                    scope_coverage TEXT NOT NULL,        -- scope1, scope1_2, scope1_2_3
                    baseline_year INTEGER NOT NULL,
                    baseline_co2e REAL NOT NULL,         -- Baz yıl emisyonu
                    target_year INTEGER NOT NULL,
                    target_co2e REAL NOT NULL,           -- Hedef emisyon
                    target_reduction_pct REAL,           -- Hedef azaltma %
                    target_type TEXT,                    -- absolute, intensity
                    intensity_metric TEXT,               -- revenue, employee, production
                    commitment_level TEXT,               -- committed, aspirational
                    sbti_approved BOOLEAN DEFAULT 0,     -- Science Based Target Initiative
                    status TEXT DEFAULT 'active',        -- active, achieved, missed, revised
                    progress_pct REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 3. Azaltma girişimleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_reduction_initiatives (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    initiative_name TEXT NOT NULL,
                    initiative_description TEXT,
                    initiative_type TEXT,                -- energy_efficiency, renewable, process_change, etc.
                    target_scope TEXT,                   -- scope1, scope2, scope3
                    start_date DATE,
                    end_date DATE,
                    investment_amount REAL,              -- Yatırım tutarı
                    expected_reduction_co2e REAL,        -- Beklenen azaltma (tCO2e/yıl)
                    actual_reduction_co2e REAL,          -- Gerçekleşen azaltma
                    status TEXT DEFAULT 'planned',       -- planned, ongoing, completed, cancelled
                    roi_years REAL,                      -- Return on Investment (yıl)
                    sdg_alignment TEXT,                  -- İlgili SDG'ler (JSON)
                    responsible_person TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 4. Emisyon raporları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_reports (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    report_period TEXT NOT NULL,
                    report_type TEXT,                    -- annual, quarterly, verification
                    scope1_total REAL,
                    scope2_total REAL,
                    scope3_total REAL,
                    total_co2e REAL NOT NULL,
                    boundary_description TEXT,           -- Organizational boundary
                    base_year INTEGER,
                    reporting_standard TEXT DEFAULT 'GHG Protocol',
                    verification_status TEXT,            -- unverified, third_party, internal
                    verifier_name TEXT,
                    verification_date DATE,
                    report_file_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 5. Özel emisyon faktörleri (EmissionFactors sınıfından)
            self.emission_factors.create_emission_factors_table()

            # İndeksler
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_carbon_emissions_company_period 
                ON carbon_emissions(company_id, period)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_carbon_emissions_scope 
                ON carbon_emissions(scope, category)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_carbon_targets_company 
                ON carbon_targets(company_id)
            """)

            conn.commit()
            logging.info("[OK] Karbon modulu tablolari basariyla olusturuldu")
            return True

        except Exception as e:
            logging.error(f"Karbon tabloları oluşturma hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==================== EMİSYON KAYITLARI (CRUD) ====================

    def add_emission(self, company_id: int, period: str, scope: str,
                    category: str, fuel_type: str, quantity: float,
                    unit: str, co2e_emission: float = None, notes: str = None, **kwargs) -> int:
        """Yeni emisyon kaydı ekle"""
        return self.save_emission_record(company_id, period, scope, category,
                                       fuel_type, quantity, unit, notes=notes, co2e_emission=co2e_emission, **kwargs)

    def save_emission_record(self, company_id: int, period: str, scope: str,
                           category: str, fuel_type: str, quantity: float,
                           unit: str, **kwargs) -> int:
        """Emisyon kaydı kaydet"""
        # CO2e hesapla (eğer kwargs'da yoksa)
        co2e_emission = kwargs.get('co2e_emission')
        if co2e_emission is None:
            try:
                calc_result = self.emission_factors.calculate_co2e(
                    scope=scope,
                    category=category,
                    fuel_type=fuel_type,
                    quantity=quantity
                )
                co2e_emission = calc_result['co2e']
            except Exception as e:
                logging.error(f"Emisyon hesaplama hatası: {e}")
                return None

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO carbon_emissions 
                (company_id, period, scope, category, subcategory, fuel_type, 
                 quantity, unit, co2_emissions, ch4_emissions, n2o_emissions, 
                 co2e_emissions, emission_factor_source, calculation_method,
                 data_quality, source, evidence_file, data_json, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                period,
                scope,
                category,
                kwargs.get('subcategory'),
                fuel_type,
                quantity,
                unit,
                kwargs.get('co2_emissions', 0),
                kwargs.get('ch4_emissions', 0),
                kwargs.get('n2o_emissions', 0),
                co2e_emission,
                kwargs.get('emission_factor_source', 'Standard'),
                kwargs.get('calculation_method', 'standard'),
                kwargs.get('data_quality', 'measured'),
                kwargs.get('source'),
                kwargs.get('evidence_file'),
                kwargs.get('data_json'),
                kwargs.get('notes', '')
            ))

            emission_id = cursor.lastrowid
            conn.commit()
            return emission_id

        except Exception as e:
            logging.error(f"Emisyon kaydı kaydetme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_emissions(self, company_id: int, period: str = None,
                     scope: str = None) -> List[Dict]:
        """Emisyon kayıtlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, period, scope, category, subcategory, fuel_type, 
                   quantity, unit, co2e_emissions, data_quality, verified, notes
            FROM carbon_emissions
            WHERE company_id = ?
        """
        params = [company_id]

        if period:
            query += " AND period = ?"
            params.append(period)

        if scope:
            query += " AND scope = ?"
            params.append(scope)

        query += " ORDER BY period DESC, scope, category"

        try:
            cursor.execute(query, params)

            emissions = []
            for row in cursor.fetchall():
                emissions.append({
                    'id': row[0],
                    'period': row[1],
                    'scope': row[2],
                    'category': row[3],
                    'subcategory': row[4],
                    'fuel_type': row[5],
                    'quantity': row[6],
                    'unit': row[7],
                    'co2e_emissions': row[8],
                    'data_quality': row[9],
                    'verified': bool(row[10]),
                    'notes': row[11]
                })

            return emissions

        except Exception as e:
            logging.error(f"Emisyon getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def update_emission_record(self, emission_id: int, **updates) -> bool:
        """Emisyon kaydını güncelle"""
        if not updates:
            return False

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Güncellenebilir alanlar
            allowed_fields = ['quantity', 'unit', 'co2e_emissions', 'data_quality',
                            'source', 'evidence_file', 'notes', 'verified']

            set_clause = []
            values = []

            for field, value in updates.items():
                if field in allowed_fields:
                    set_clause.append(f"{field} = ?")
                    values.append(value)

            if not set_clause:
                return False

            set_clause.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(emission_id)

            query = f"UPDATE carbon_emissions SET {', '.join(set_clause)} WHERE id = ?"
            cursor.execute(query, values)

            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logging.error(f"Emisyon güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_emission_record(self, emission_id: int) -> bool:
        """Emisyon kaydını sil"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM carbon_emissions WHERE id = ?", (emission_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Emisyon silme hatası: {e}")
            return False
        finally:
            conn.close()
