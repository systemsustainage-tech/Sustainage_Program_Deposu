#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detaylı Enerji Yöneticisi
Enerji yoğunluğu, yenilenebilir enerji oranı ve detaylı enerji analizi
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Union

try:
    from utils.language_manager import LanguageManager
except ImportError:
    from backend.utils.language_manager import LanguageManager

from backend.core.base_manager import BaseTenantManager

class DetailedEnergyManager(BaseTenantManager):
    """Detaylı enerji yönetimi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        self.lm = LanguageManager()
        final_db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        super().__init__(final_db_path, company_id)
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        try:
            # Enerji tüketim kayıtları
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS energy_consumption_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    facility_id INTEGER,
                    facility_name TEXT,
                    energy_type TEXT NOT NULL,
                    energy_source TEXT,
                    consumption_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    measurement_date TEXT NOT NULL,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    billing_period_start TEXT,
                    billing_period_end TEXT,
                    cost REAL,
                    currency TEXT DEFAULT 'TRY',
                    emission_factor REAL,
                    co2_emissions REAL,
                    energy_intensity REAL,
                    production_volume REAL,
                    production_unit TEXT,
                    data_source TEXT,
                    notes TEXT,
                    recorded_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Enerji kaynakları
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS energy_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    source_name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    energy_type TEXT NOT NULL,
                    capacity REAL,
                    capacity_unit TEXT,
                    efficiency REAL,
                    emission_factor REAL,
                    is_active INTEGER DEFAULT 1,
                    installation_date TEXT,
                    decommission_date TEXT,
                    location TEXT,
                    supplier TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Enerji verimliliği projeleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS energy_efficiency_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    description TEXT,
                    facility_id INTEGER,
                    facility_name TEXT,
                    start_date TEXT,
                    completion_date TEXT,
                    investment_cost REAL,
                    currency TEXT DEFAULT 'TRY',
                    annual_savings REAL,
                    annual_cost_savings REAL,
                    payback_period REAL,
                    co2_reduction REAL,
                    status TEXT DEFAULT 'planned',
                    responsible_person TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Enerji performans göstergeleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS energy_kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    kpi_name TEXT NOT NULL,
                    kpi_type TEXT NOT NULL,
                    calculation_method TEXT,
                    target_value REAL,
                    baseline_value REAL,
                    current_value REAL,
                    unit TEXT NOT NULL,
                    measurement_period TEXT,
                    last_updated TEXT,
                    trend TEXT,
                    benchmark_value REAL,
                    benchmark_source TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Enerji raporları
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS energy_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    report_name TEXT NOT NULL,
                    report_period TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    total_consumption REAL,
                    total_cost REAL,
                    total_emissions REAL,
                    renewable_ratio REAL,
                    energy_intensity REAL,
                    efficiency_score REAL,
                    key_findings TEXT,
                    recommendations TEXT,
                    generated_by INTEGER,
                    generated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migration logic for existing tables
            self._migrate_tables()

            logging.info(f"[OK] {self.lm.tr('detailed_energy_tables_ready', 'Detaylı enerji tabloları hazır')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('table_creation_error', 'Tablo oluşturma hatası')}: {e}")

    def _migrate_tables(self):
        """Mevcut tablolara eksik kolonları ekle"""
        migrations = [
            ('energy_consumption_records', 'invoice_date', 'TEXT'),
            ('energy_consumption_records', 'due_date', 'TEXT'),
            ('energy_consumption_records', 'supplier', 'TEXT')
        ]
        
        for table, col, col_type in migrations:
            try:
                self.execute_update(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
            except Exception:
                pass

    def record_energy_consumption(self, company_id: Optional[int] = None, facility_id: int = None, facility_name: str = "",
                                energy_type: str = "electricity", energy_source: str = "grid",
                                consumption_amount: float = 0, unit: str = "kWh", measurement_date: str = None,
                                billing_period_start: str = None, billing_period_end: str = None,
                                cost: float = None, emission_factor: float = None, production_volume: float = None,
                                production_unit: str = "", data_source: str = "meter_reading",
                                notes: str = "", recorded_by: int = None,
                                invoice_date: str = None, due_date: str = None, supplier: str = None) -> int:
        """Enerji tüketim kaydı oluştur"""
        try:
            cid = self._ensure_context(company_id)
            
            if measurement_date is None:
                measurement_date = datetime.now().strftime('%Y-%m-%d')

            # CO2 emisyonlarını hesapla
            co2_emissions = consumption_amount * emission_factor if emission_factor else None

            # Enerji yoğunluğunu hesapla
            energy_intensity = consumption_amount / production_volume if production_volume and production_volume > 0 else None

            data = {
                'facility_id': facility_id,
                'facility_name': facility_name,
                'energy_type': energy_type,
                'energy_source': energy_source,
                'consumption_amount': consumption_amount,
                'unit': unit,
                'measurement_date': measurement_date,
                'billing_period_start': billing_period_start,
                'billing_period_end': billing_period_end,
                'cost': cost,
                'emission_factor': emission_factor,
                'co2_emissions': co2_emissions,
                'energy_intensity': energy_intensity,
                'production_volume': production_volume,
                'production_unit': production_unit,
                'data_source': data_source,
                'notes': notes,
                'recorded_by': recorded_by,
                'invoice_date': invoice_date,
                'due_date': due_date,
                'supplier': supplier
            }
            
            return self.insert('energy_consumption_records', data, company_id=cid)

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('energy_record_creation_error', 'Enerji kaydı oluşturma hatası')}: {e}")
            raise

    def add_energy_source(self, company_id: Optional[int] = None, source_name: str = "", source_type: str = "",
                         energy_type: str = "", capacity: float = None, capacity_unit: str = "kW",
                         efficiency: float = None, emission_factor: float = None,
                         installation_date: str = None, location: str = "", supplier: str = "",
                         notes: str = "") -> int:
        """Enerji kaynağı ekle"""
        try:
            cid = self._ensure_context(company_id)
            
            data = {
                'source_name': source_name,
                'source_type': source_type,
                'energy_type': energy_type,
                'capacity': capacity,
                'capacity_unit': capacity_unit,
                'efficiency': efficiency,
                'emission_factor': emission_factor,
                'installation_date': installation_date,
                'location': location,
                'supplier': supplier,
                'notes': notes
            }
            
            return self.insert('energy_sources', data, company_id=cid)

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('energy_source_add_error', 'Enerji kaynağı ekleme hatası')}: {e}")
            raise

    def create_efficiency_project(self, company_id: Optional[int] = None, project_name: str = "", project_type: str = "",
                                description: str = "", facility_id: int = None, facility_name: str = "",
                                start_date: str = None, completion_date: str = None, investment_cost: float = None,
                                annual_savings: float = None, annual_cost_savings: float = None,
                                payback_period: float = None, co2_reduction: float = None,
                                responsible_person: str = "", notes: str = "") -> int:
        """Enerji verimliliği projesi oluştur"""
        try:
            cid = self._ensure_context(company_id)
            
            data = {
                'project_name': project_name,
                'project_type': project_type,
                'description': description,
                'facility_id': facility_id,
                'facility_name': facility_name,
                'start_date': start_date,
                'completion_date': completion_date,
                'investment_cost': investment_cost,
                'annual_savings': annual_savings,
                'annual_cost_savings': annual_cost_savings,
                'payback_period': payback_period,
                'co2_reduction': co2_reduction,
                'responsible_person': responsible_person,
                'notes': notes
            }
            
            return self.insert('energy_efficiency_projects', data, company_id=cid)

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('project_creation_error', 'Proje oluşturma hatası')}: {e}")
            raise

    def calculate_energy_metrics(self, company_id: Optional[int] = None, period: str = None) -> Dict:
        """Enerji metriklerini hesapla"""
        try:
            cid = self._ensure_context(company_id)
            
            # Dönem filtresi
            where_clauses = ["company_id = ?"]
            params = [cid]

            if period:
                if len(period) == 7:  # YYYY-MM
                    where_clauses.append("strftime('%Y-%m', measurement_date) = ?")
                    params.append(period)
                elif len(period) == 4:  # YYYY
                    where_clauses.append("strftime('%Y', measurement_date) = ?")
                    params.append(period)
            
            where_str = " AND ".join(where_clauses)
            
            query = f"""
                SELECT 
                    SUM(consumption_amount) as total_consumption,
                    SUM(cost) as total_cost,
                    SUM(co2_emissions) as total_emissions,
                    COUNT(*) as record_count
                FROM energy_consumption_records
                WHERE {where_str}
            """
            
            results = self.execute_query(query, tuple(params))
            row = results[0] if results else None
            
            if row:
                return {
                    'total_consumption': row['total_consumption'] or 0,
                    'total_cost': row['total_cost'] or 0,
                    'total_emissions': row['total_emissions'] or 0,
                    'record_count': row['record_count'] or 0
                }
            return {'total_consumption': 0, 'total_cost': 0, 'total_emissions': 0, 'record_count': 0}

        except Exception as e:
            logging.error(f"Metric calculation error: {e}")
            return {}
