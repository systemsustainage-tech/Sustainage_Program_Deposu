#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enerji Yönetimi Modülü
Enerji tüketimi, verimlilik ve yenilenebilir enerji yönetimi
"""

import logging
import os
from typing import Dict, List, Optional

try:
    from backend.utils.language_manager import LanguageManager
    from backend.config.database import DB_PATH
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    from utils.language_manager import LanguageManager
    from config.database import DB_PATH
    from core.base_manager import BaseTenantManager


class EnergyManager(BaseTenantManager):
    """Enerji tüketimi ve verimlilik yönetimi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        self.lm = LanguageManager()
        final_db_path = db_path or DB_PATH
        if final_db_path and not os.path.isabs(final_db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            final_db_path = os.path.join(base_dir, final_db_path)
        
        super().__init__(final_db_path, company_id)
        self._init_db_tables()
        self._migrate_tables()

    def _init_db_tables(self) -> None:
        """Enerji yönetimi tablolarını oluştur"""
        try:
            # Enerji tüketimi
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS energy_consumption (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    energy_type TEXT NOT NULL,
                    consumption_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    cost REAL,
                    source TEXT,
                    location TEXT,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Yenilenebilir enerji
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS renewable_energy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    renewable_type TEXT NOT NULL,
                    capacity REAL,
                    capacity_unit TEXT,
                    generation REAL,
                    generation_unit TEXT,
                    self_consumption REAL,
                    grid_feed REAL,
                    cost REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Enerji verimliliği projeleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS energy_efficiency_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    investment_cost REAL,
                    energy_savings REAL,
                    savings_unit TEXT,
                    cost_savings REAL,
                    payback_period REAL,
                    co2_reduction REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Enerji hedefleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS energy_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_year INTEGER,
                    baseline_consumption REAL,
                    target_reduction_percent REAL,
                    target_consumption REAL,
                    renewable_target_percent REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Enerji performans göstergeleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS energy_kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    kpi_name TEXT NOT NULL,
                    kpi_value REAL NOT NULL,
                    kpi_unit TEXT NOT NULL,
                    benchmark_value REAL,
                    benchmark_source TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            logging.info(f"[OK] {self.lm.tr('energy_module_tables_created', 'Enerji modülü tabloları başarıyla oluşturuldu')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('energy_module_table_error', 'Enerji modülü tablo oluşturma')}: {e}")

    def _migrate_tables(self) -> None:
        """Tablo şemalarını güncelle"""
        try:
            # Mevcut tabloya yeni kolonları eklemeye çalış (Migration)
            columns = [row['name'] for row in self.execute_query("PRAGMA table_info(energy_consumption)")]
            
            if 'invoice_date' not in columns:
                self.execute_update("ALTER TABLE energy_consumption ADD COLUMN invoice_date TEXT")
            if 'due_date' not in columns:
                self.execute_update("ALTER TABLE energy_consumption ADD COLUMN due_date TEXT")
            if 'supplier' not in columns:
                self.execute_update("ALTER TABLE energy_consumption ADD COLUMN supplier TEXT")
        except Exception as e:
            logging.warning(f"Energy table migration warning: {e}")

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        cid = self._ensure_context(company_id)
        stats = {'total_consumption': 0, 'renewable_ratio': 0, 'total_cost': 0}

        try:
            # Total Consumption & Cost
            result = self.execute_query("SELECT SUM(consumption_amount) as total, SUM(cost) as cost FROM energy_consumption WHERE company_id = ?", (cid,))
            if result:
                stats['total_consumption'] = result[0]['total'] if result[0]['total'] else 0
                stats['total_cost'] = result[0]['cost'] if result[0]['cost'] else 0

            # Renewable Generation
            result_ren = self.execute_query("SELECT SUM(generation) as total FROM renewable_energy WHERE company_id = ?", (cid,))
            renewable_gen = result_ren[0]['total'] if result_ren and result_ren[0]['total'] else 0

            # Simple ratio calculation (assuming consumption includes renewable)
            if stats['total_consumption'] > 0:
                stats['renewable_ratio'] = (renewable_gen / stats['total_consumption']) * 100
            
            return stats
        except Exception as e:
            logging.error(f"Energy dashboard stats error: {e}")
            return stats

    def get_recent_records(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Son eklenen kayıtları getir"""
        cid = self._ensure_context(company_id)
        records = []

        try:
            rows = self.execute_query("""
                SELECT energy_type, consumption_amount, unit, cost, created_at, year, month
                FROM energy_consumption 
                WHERE company_id = ? 
                ORDER BY created_at DESC LIMIT ?
            """, (cid, limit))
            
            for row in rows:
                records.append({
                    'type': row['energy_type'],
                    'amount': row['consumption_amount'],
                    'unit': row['unit'],
                    'cost': row['cost'],
                    'date': row['created_at'],
                    'year': row['year'],
                    'month': row['month']
                })
            
            return records
        except Exception as e:
            logging.error(f"Energy recent records error: {e}")
            return []

    def add_energy_consumption(self, company_id: int, year: int, energy_type: str,
                             consumption_amount: float, unit: str, cost: float = None,
                             source: str = None, location: str = None, month: int = None,
                             invoice_date: str = None, due_date: str = None, supplier: str = None) -> bool:
        """Enerji tüketimi ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT INTO energy_consumption 
                (company_id, year, month, energy_type, consumption_amount, 
                 unit, cost, source, location, invoice_date, due_date, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, year, month, energy_type, consumption_amount,
                  unit, cost, source, location, invoice_date, due_date, supplier))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_consumption_add_error', 'Enerji tüketimi ekleme hatası')}: {e}")
            return False

    def add_renewable_energy(self, company_id: int, year: int, renewable_type: str,
                           capacity: float, capacity_unit: str, generation: float,
                           generation_unit: str, self_consumption: float = None,
                           grid_feed: float = None, cost: float = None) -> bool:
        """Yenilenebilir enerji ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT INTO renewable_energy 
                (company_id, year, renewable_type, capacity, capacity_unit,
                 generation, generation_unit, self_consumption, grid_feed, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, year, renewable_type, capacity, capacity_unit,
                  generation, generation_unit, self_consumption, grid_feed, cost))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('renewable_energy_add_error', 'Yenilenebilir enerji ekleme hatası')}: {e}")
            return False

    def add_energy_efficiency_project(self, company_id: int, project_name: str,
                                    project_type: str, start_date: str, end_date: str,
                                    investment_cost: float, energy_savings: float,
                                    savings_unit: str, cost_savings: float = None,
                                    payback_period: float = None, co2_reduction: float = None) -> bool:
        """Enerji verimliliği projesi ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT INTO energy_efficiency_projects 
                (company_id, project_name, project_type, start_date, end_date,
                 investment_cost, energy_savings, savings_unit, cost_savings,
                 payback_period, co2_reduction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, project_name, project_type, start_date, end_date,
                  investment_cost, energy_savings, savings_unit, cost_savings,
                  payback_period, co2_reduction))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_efficiency_project_add_error', 'Enerji verimliliği projesi ekleme hatası')}: {e}")
            return False

    def set_energy_target(self, company_id: int, target_year: int, target_type: str,
                         baseline_year: int, baseline_consumption: float,
                         target_reduction_percent: float, renewable_target_percent: float = None) -> bool:
        """Enerji hedefi belirle"""
        cid = self._ensure_context(company_id)

        try:
            target_consumption = baseline_consumption * (1 - target_reduction_percent / 100)

            self.execute_update("""
                INSERT OR REPLACE INTO energy_targets 
                (company_id, target_year, target_type, baseline_year, 
                 baseline_consumption, target_reduction_percent, target_consumption,
                 renewable_target_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, target_year, target_type, baseline_year,
                  baseline_consumption, target_reduction_percent, target_consumption,
                  renewable_target_percent))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_target_set_error', 'Enerji hedefi belirleme hatası')}: {e}")
            return False

    def get_energy_summary(self, company_id: int, year: int) -> Dict:
        """Enerji özeti getir"""
        cid = self._ensure_context(company_id)

        try:
            # Toplam enerji tüketimi
            rows = self.execute_query("""
                SELECT energy_type, SUM(consumption_amount) as total_amount, unit, SUM(cost) as total_cost
                FROM energy_consumption 
                WHERE company_id = ? AND year = ?
                GROUP BY energy_type, unit
            """, (cid, year))

            energy_consumption = {}
            total_cost = 0
            for row in rows:
                energy_type = row['energy_type']
                amount = row['total_amount']
                unit = row['unit']
                cost = row['total_cost']
                
                energy_consumption[energy_type] = {
                    'amount': amount,
                    'unit': unit,
                    'cost': cost or 0
                }
                total_cost += cost or 0

            # Yenilenebilir enerji
            rows_ren = self.execute_query("""
                SELECT renewable_type, SUM(generation) as total_gen, generation_unit
                FROM renewable_energy 
                WHERE company_id = ? AND year = ?
                GROUP BY renewable_type, generation_unit
            """, (cid, year))

            renewable_generation = {}
            for row in rows_ren:
                renewable_type = row['renewable_type']
                generation = row['total_gen']
                unit = row['generation_unit']
                
                renewable_generation[renewable_type] = {
                    'generation': generation,
                    'unit': unit
                }

            # Toplam yenilenebilir enerji
            total_renewable = sum(data['generation'] for data in renewable_generation.values())

            # Toplam enerji tüketimi (kWh cinsinden)
            total_consumption = 0
            for data in energy_consumption.values():
                if data['unit'] == 'kWh':
                    total_consumption += data['amount']
                elif data['unit'] == 'MWh':
                    total_consumption += data['amount'] * 1000
                elif data['unit'] == 'GWh':
                    total_consumption += data['amount'] * 1000000

            # Yenilenebilir enerji oranı
            renewable_ratio = (total_renewable / total_consumption * 100) if total_consumption > 0 else 0

            return {
                'energy_consumption': energy_consumption,
                'renewable_generation': renewable_generation,
                'total_consumption': total_consumption,
                'total_renewable': total_renewable,
                'renewable_ratio': renewable_ratio,
                'total_cost': total_cost,
                'year': year,
                'company_id': cid
            }

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_summary_get_error', 'Enerji özeti getirme hatası')}: {e}")
            return {}

    def get_energy_targets(self, company_id: int) -> List[Dict]:
        """Enerji hedeflerini getir"""
        cid = self._ensure_context(company_id)

        try:
            rows = self.execute_query("""
                SELECT target_year, target_type, baseline_year, baseline_consumption,
                       target_reduction_percent, target_consumption, renewable_target_percent, status
                FROM energy_targets 
                WHERE company_id = ? AND status = 'active'
                ORDER BY target_year
            """, (cid,))

            targets = []
            for row in rows:
                targets.append({
                    'target_year': row['target_year'],
                    'target_type': row['target_type'],
                    'baseline_year': row['baseline_year'],
                    'baseline_consumption': row['baseline_consumption'],
                    'target_reduction_percent': row['target_reduction_percent'],
                    'target_consumption': row['target_consumption'],
                    'renewable_target_percent': row['renewable_target_percent'],
                    'status': row['status']
                })

            return targets

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_targets_get_error', 'Enerji hedefleri getirme hatası')}: {e}")
            return []

    def get_energy_efficiency_projects(self, company_id: int) -> List[Dict]:
        """Enerji verimliliği projelerini getir"""
        cid = self._ensure_context(company_id)

        try:
            rows = self.execute_query("""
                SELECT project_name, project_type, start_date, end_date,
                       investment_cost, energy_savings, savings_unit, cost_savings,
                       payback_period, co2_reduction, status
                FROM energy_efficiency_projects 
                WHERE company_id = ? AND status = 'active'
                ORDER BY start_date DESC
            """, (cid,))

            projects = []
            for row in rows:
                projects.append({
                    'project_name': row['project_name'],
                    'project_type': row['project_type'],
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'investment_cost': row['investment_cost'],
                    'energy_savings': row['energy_savings'],
                    'savings_unit': row['savings_unit'],
                    'cost_savings': row['cost_savings'],
                    'payback_period': row['payback_period'],
                    'co2_reduction': row['co2_reduction'],
                    'status': row['status']
                })

            return projects

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_efficiency_projects_get_error', 'Enerji verimliliği projeleri getirme hatası')}: {e}")
            return []

    def calculate_energy_kpis(self, company_id: int, year: int) -> Dict:
        """Enerji KPI'larını hesapla"""
        summary = self.get_energy_summary(company_id, year)

        if not summary:
            return {}

        # Enerji yoğunluğu (kWh/çalışan veya kWh/m²)
        # Bu değerler şirket bilgilerinden alınmalı
        energy_intensity_per_employee = summary['total_consumption'] / 100  # Örnek: 100 çalışan
        energy_intensity_per_area = summary['total_consumption'] / 1000     # Örnek: 1000 m²

        return {
            'total_energy_consumption': summary['total_consumption'],
            'renewable_energy_ratio': summary['renewable_ratio'],
            'energy_cost': summary['total_cost'],
            'energy_intensity_per_employee': energy_intensity_per_employee,
            'energy_intensity_per_area': energy_intensity_per_area,
            'year': year,
            'company_id': summary['company_id']
        }
