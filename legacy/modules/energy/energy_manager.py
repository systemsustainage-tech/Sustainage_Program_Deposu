#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enerji Yönetimi Modülü
Enerji tüketimi, verimlilik ve yenilenebilir enerji yönetimi
"""

import logging
import os
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime

from config.database import DB_PATH
# LanguageManager'i şimdilik pas geçiyorum veya mockluyorum, çünkü web app tarafında farklı olabilir
# Ama import hata vermemesi için basit bir wrapper veya doğrudan string kullanacağım.
try:
    from utils.language_manager import LanguageManager
except ImportError:
    class LanguageManager:
        def tr(self, key, default): return default


class EnergyManager:
    """Enerji tüketimi ve verimlilik yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.lm = LanguageManager()
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Enerji yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Enerji tüketimi
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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

            conn.commit()
            logging.info(f"[OK] {self.lm.tr('energy_module_tables_created', 'Enerji modülü tabloları başarıyla oluşturuldu')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('energy_module_table_error', 'Enerji modülü tablo oluşturma')}: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_energy_consumption(self, company_id: int, year: int, energy_type: str,
                             consumption_amount: float, unit: str, cost: float = None,
                             source: str = None, location: str = None, month: int = None,
                             invoice_date: str = None, due_date: str = None, supplier: str = None) -> bool:
        """Enerji tüketimi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO energy_consumption 
                (company_id, year, month, energy_type, consumption_amount, 
                 unit, cost, source, location, invoice_date, due_date, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, month, energy_type, consumption_amount,
                  unit, cost, source, location, invoice_date, due_date, supplier))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_consumption_add_error', 'Enerji tüketimi ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_renewable_energy(self, company_id: int, year: int, renewable_type: str,
                           capacity: float, capacity_unit: str, generation: float,
                           generation_unit: str, self_consumption: float = None,
                           grid_feed: float = None, cost: float = None) -> bool:
        """Yenilenebilir enerji ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO renewable_energy 
                (company_id, year, renewable_type, capacity, capacity_unit,
                 generation, generation_unit, self_consumption, grid_feed, cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, renewable_type, capacity, capacity_unit,
                  generation, generation_unit, self_consumption, grid_feed, cost))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('renewable_energy_add_error', 'Yenilenebilir enerji ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_energy_efficiency_project(self, company_id: int, project_name: str,
                                    project_type: str, start_date: str, end_date: str,
                                    investment_cost: float, energy_savings: float,
                                    savings_unit: str, cost_savings: float = None,
                                    payback_period: float = None, co2_reduction: float = None) -> bool:
        """Enerji verimliliği projesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO energy_efficiency_projects 
                (company_id, project_name, project_type, start_date, end_date,
                 investment_cost, energy_savings, savings_unit, cost_savings,
                 payback_period, co2_reduction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, project_name, project_type, start_date, end_date,
                  investment_cost, energy_savings, savings_unit, cost_savings,
                  payback_period, co2_reduction))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_efficiency_project_add_error', 'Enerji verimliliği projesi ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def set_energy_target(self, company_id: int, target_year: int, target_type: str,
                         baseline_year: int, baseline_consumption: float,
                         target_reduction_percent: float, renewable_target_percent: float = None) -> bool:
        """Enerji hedefi belirle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            target_consumption = baseline_consumption * (1 - target_reduction_percent / 100)

            cursor.execute("""
                INSERT OR REPLACE INTO energy_targets 
                (company_id, target_year, target_type, baseline_year, 
                 baseline_consumption, target_reduction_percent, target_consumption,
                 renewable_target_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, target_year, target_type, baseline_year,
                  baseline_consumption, target_reduction_percent, target_consumption,
                  renewable_target_percent))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_target_set_error', 'Enerji hedefi belirleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_energy_records(self, company_id: int, year: int) -> List[Dict]:
        """Enerji tüketim kayıtlarını getir (liste olarak)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, year, month, energy_type, consumption_amount, unit, cost, source
                FROM energy_consumption 
                WHERE company_id = ? AND year = ?
                ORDER BY month, energy_type
            """, (company_id, year))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'id': row[0],
                    'year': row[1],
                    'month': row[2],
                    'energy_type': row[3],
                    'consumption_amount': row[4],
                    'unit': row[5],
                    'cost': row[6],
                    'source': row[7]
                })
            return records
        except Exception as e:
            logging.error(f"Enerji kayitlari getirme hatasi: {e}")
            return []
        finally:
            conn.close()

    def get_energy_summary(self, company_id: int, year: int) -> Dict:
        """Enerji özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Toplam enerji tüketimi
            cursor.execute("""
                SELECT energy_type, SUM(consumption_amount), unit, SUM(cost)
                FROM energy_consumption 
                WHERE company_id = ? AND year = ?
                GROUP BY energy_type, unit
            """, (company_id, year))

            energy_consumption = {}
            total_cost = 0
            for row in cursor.fetchall():
                energy_type, amount, unit, cost = row
                energy_consumption[energy_type] = {
                    'amount': amount,
                    'unit': unit,
                    'cost': cost or 0
                }
                total_cost += cost or 0

            # Yenilenebilir enerji
            cursor.execute("""
                SELECT renewable_type, SUM(generation), generation_unit
                FROM renewable_energy 
                WHERE company_id = ? AND year = ?
                GROUP BY renewable_type, generation_unit
            """, (company_id, year))

            renewable_generation = {}
            for row in cursor.fetchall():
                renewable_type, generation, unit = row
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
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_summary_get_error', 'Enerji özeti getirme hatası')}: {e}")
            return {}
        finally:
            conn.close()

    def get_energy_targets(self, company_id: int) -> List[Dict]:
        """Enerji hedeflerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT target_year, target_type, baseline_year, baseline_consumption,
                       target_reduction_percent, target_consumption, renewable_target_percent, status
                FROM energy_targets 
                WHERE company_id = ? AND status = 'active'
                ORDER BY target_year
            """, (company_id,))

            targets = []
            for row in cursor.fetchall():
                targets.append({
                    'target_year': row[0],
                    'target_type': row[1],
                    'baseline_year': row[2],
                    'baseline_consumption': row[3],
                    'target_reduction_percent': row[4],
                    'target_consumption': row[5],
                    'renewable_target_percent': row[6],
                    'status': row[7]
                })

            return targets

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_targets_get_error', 'Enerji hedefleri getirme hatası')}: {e}")
            return []
        finally:
            conn.close()

    def get_energy_efficiency_projects(self, company_id: int) -> List[Dict]:
        """Enerji verimliliği projelerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT project_name, project_type, start_date, end_date,
                       investment_cost, energy_savings, savings_unit, cost_savings,
                       payback_period, co2_reduction, status
                FROM energy_efficiency_projects 
                WHERE company_id = ? AND status = 'active'
                ORDER BY start_date DESC
            """, (company_id,))

            projects = []
            for row in cursor.fetchall():
                projects.append({
                    'project_name': row[0],
                    'project_type': row[1],
                    'start_date': row[2],
                    'end_date': row[3],
                    'investment_cost': row[4],
                    'energy_savings': row[5],
                    'savings_unit': row[6],
                    'cost_savings': row[7],
                    'payback_period': row[8],
                    'co2_reduction': row[9],
                    'status': row[10]
                })

            return projects

        except Exception as e:
            logging.error(f"{self.lm.tr('energy_projects_get_error', 'Enerji projeleri getirme hatası')}: {e}")
            return []
        finally:
            conn.close()

    def calculate_energy_kpis(self, company_id: int, year: int) -> Dict:
        """Enerji KPI'larını hesapla"""
        summary = self.get_energy_summary(company_id, year)

        if not summary:
            return {}

        # Enerji yoğunluğu (kWh/çalışan veya kWh/m²)
        # Bu değerler şirket bilgilerinden alınmalı
        # Şimdilik basit varsayımlar veya veritabanından çekilecek değerler
        energy_intensity_per_employee = summary['total_consumption'] / 100  # Örnek: 100 çalışan
        energy_intensity_per_area = summary['total_consumption'] / 1000     # Örnek: 1000 m²

        return {
            'total_energy_consumption': summary['total_consumption'],
            'renewable_energy_ratio': summary['renewable_ratio'],
            'energy_cost': summary['total_cost'],
            'energy_intensity_per_employee': energy_intensity_per_employee,
            'energy_intensity_per_area': energy_intensity_per_area,
            'year': year,
            'company_id': company_id
        }
