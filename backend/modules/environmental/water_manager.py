#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Su Yönetimi Modülü
Su tüketimi, geri dönüşüm ve su verimliliği yönetimi
"""

import logging
import os
from typing import Dict, List, Optional
from datetime import date

try:
    from utils.language_manager import LanguageManager
    from config.database import DB_PATH
    from core.base_manager import BaseTenantManager
except ImportError:
    from backend.utils.language_manager import LanguageManager
    from backend.config.database import DB_PATH
    from backend.core.base_manager import BaseTenantManager


class WaterManager(BaseTenantManager):
    """Su tüketimi ve su yönetimi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        self.lm = LanguageManager()
        final_db_path = db_path or DB_PATH
        if final_db_path and not os.path.isabs(final_db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            final_db_path = os.path.join(base_dir, final_db_path)
        
        super().__init__(final_db_path, company_id)
        self._init_db_tables()
        self._migrate_tables()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        return self.calculate_water_metrics(company_id)

    def get_recent_records(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Son eklenen kayıtları getir"""
        cid = self._ensure_context(company_id)
        records = []

        try:
            # Check table schema first to handle different versions
            columns = [row['name'] for row in self.execute_query("PRAGMA table_info(water_consumption)")]
            
            type_col = 'source_type' if 'source_type' in columns else 'consumption_type'
            source_col = 'supplier' if 'supplier' in columns else 'source'
            
            # If neither supplier nor source exists, select NULL
            if source_col not in columns:
                source_select = "NULL as source"
            else:
                source_select = source_col

            query = f"""
                SELECT {type_col}, consumption_amount, unit, {source_select}, created_at 
                FROM water_consumption 
                WHERE company_id = ? 
                ORDER BY created_at DESC LIMIT ?
            """
            
            rows = self.execute_query(query, (cid, limit), company_id=cid)
            
            for row in rows:
                records.append({
                    'type': row[type_col] if type_col in row else row['consumption_type'],
                    'amount': row['consumption_amount'],
                    'unit': row['unit'],
                    'source': row['source'] if 'source' in row else (row[source_col] if source_col in row else None),
                    'date': row['created_at']
                })
            
            return records
        except Exception as e:
            logging.error(f"Water recent records error: {e}")
            return []

    def _init_db_tables(self) -> None:
        """Su yönetimi tablolarını oluştur"""
        try:
            # Su tüketimi
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS water_consumption (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    consumption_type TEXT NOT NULL,
                    consumption_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    cost REAL,
                    source TEXT,
                    location TEXT,
                    quality_parameters TEXT,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Su geri dönüşümü
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS water_recycling (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    recycling_type TEXT NOT NULL,
                    recycled_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    treatment_method TEXT,
                    reuse_purpose TEXT,
                    cost_savings REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Su kalitesi
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS water_quality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    location TEXT NOT NULL,
                    parameter_name TEXT NOT NULL,
                    parameter_value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    standard_limit REAL,
                    compliance_status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Su verimliliği projeleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS water_efficiency_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    investment_cost REAL,
                    water_savings REAL,
                    savings_unit TEXT,
                    cost_savings REAL,
                    payback_period REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Su hedefleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS water_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_year INTEGER,
                    baseline_consumption REAL,
                    target_reduction_percent REAL,
                    target_consumption REAL,
                    recycling_target_percent REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            logging.info(f"[OK] {self.lm.tr('water_module_tables_created', 'Su yönetimi modülü tabloları başarıyla oluşturuldu')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('water_module_table_error', 'Su yönetimi modülü tablo oluşturma')}: {e}")

    def _migrate_tables(self) -> None:
        """Tablo şemalarını güncelle"""
        try:
            # Migration: Add missing columns if they don't exist
            columns = [row['name'] for row in self.execute_query("PRAGMA table_info(water_consumption)")]
            
            if 'invoice_date' not in columns:
                self.execute_update("ALTER TABLE water_consumption ADD COLUMN invoice_date TEXT")
            if 'due_date' not in columns:
                self.execute_update("ALTER TABLE water_consumption ADD COLUMN due_date TEXT")
            if 'supplier' not in columns:
                self.execute_update("ALTER TABLE water_consumption ADD COLUMN supplier TEXT")
        except Exception as e:
            logging.warning(f"Water table migration warning: {e}")

    def add_water_consumption(self, company_id: int, year: int, consumption_type: str,
                            consumption_amount: float, unit: str, cost: float = None,
                            source: str = None, location: str = None, month: int = None,
                            quality_parameters: str = None,
                            invoice_date: str = None, due_date: str = None, supplier: str = None) -> bool:
        """Su tüketimi ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT INTO water_consumption 
                (company_id, year, month, consumption_type, consumption_amount, 
                 unit, cost, source, location, quality_parameters,
                 invoice_date, due_date, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, year, month, consumption_type, consumption_amount,
                  unit, cost, source, location, quality_parameters,
                  invoice_date, due_date, supplier), company_id=cid)
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('water_consumption_add_error', 'Su tüketimi ekleme hatası')}: {e}")
            return False

    def add_water_recycling(self, company_id: int, year: int, recycling_type: str,
                          recycled_amount: float, unit: str, treatment_method: str = None,
                          reuse_purpose: str = None, cost_savings: float = None) -> bool:
        """Su geri dönüşümü ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT INTO water_recycling 
                (company_id, year, recycling_type, recycled_amount, unit,
                 treatment_method, reuse_purpose, cost_savings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, year, recycling_type, recycled_amount, unit,
                  treatment_method, reuse_purpose, cost_savings), company_id=cid)
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('water_recycling_add_error', 'Su geri dönüşümü ekleme hatası')}: {e}")
            return False

    def get_water_records(self, company_id: int, year: str = None) -> List[Dict]:
        """Su kayıtlarını getir (Raporlama için)"""
        cid = self._ensure_context(company_id)
        records = []

        try:
            query = """
                SELECT 'Tüketim' as type, consumption_type as category, consumption_amount, unit, 
                cost, source, location, invoice_date, due_date, supplier, created_at
                FROM water_consumption 
                WHERE company_id = ?
            """
            params = [cid]
            
            if year and str(year).isdigit():
                query += " AND year = ?"
                params.append(int(year))
                
            rows = self.execute_query(query, tuple(params), company_id=cid)
            for row in rows:
                records.append({
                    'type': row['type'],
                    'category': row['category'],
                    'amount': row['consumption_amount'],
                    'unit': row['unit'],
                    'cost': row['cost'],
                    'source': row['source'],
                    'location': row['location'],
                    'invoice_date': row['invoice_date'],
                    'due_date': row['due_date'],
                    'supplier': row['supplier'],
                    'date': row['created_at']
                })

            # Geri dönüşüm kayıtları
            query_recycling = """
                SELECT 'Geri Dönüşüm' as type, recycling_type as category, recycled_amount, unit, 
                cost_savings, treatment_method, reuse_purpose, created_at
                FROM water_recycling 
                WHERE company_id = ?
            """
            params_recycling = [cid]
            
            if year and str(year).isdigit():
                query_recycling += " AND year = ?"
                params_recycling.append(int(year))
                
            rows_recycling = self.execute_query(query_recycling, tuple(params_recycling), company_id=cid)
            for row in rows_recycling:
                records.append({
                    'type': row['type'],
                    'category': row['category'],
                    'amount': row['recycled_amount'],
                    'unit': row['unit'],
                    'cost': row['cost_savings'], # cost_savings mapped to cost field for consistency or handled separately
                    'source': row['treatment_method'], # treatment_method
                    'location': row['reuse_purpose'], # reuse_purpose
                    'date': row['created_at']
                })
                
            return records

        except Exception as e:
            logging.error(f"Su kayıtları getirme hatası: {e}")
            return []

    def calculate_water_metrics(self, company_id: int, year: int = None) -> Dict:
        """Su metriklerini hesapla"""
        cid = self._ensure_context(company_id)
        metrics = {}

        try:
            # Toplam Tüketim
            query = "SELECT SUM(consumption_amount) as total FROM water_consumption WHERE company_id = ?"
            params = [cid]
            if year:
                query += " AND year = ?"
                params.append(year)
            result = self.execute_query(query, tuple(params), company_id=cid)
            metrics['total_consumption'] = result[0]['total'] if result and result[0]['total'] else 0

            # Toplam Geri Dönüşüm
            query = "SELECT SUM(recycled_amount) as total FROM water_recycling WHERE company_id = ?"
            if year:
                query += " AND year = ?"
            result = self.execute_query(query, tuple(params), company_id=cid)
            metrics['total_recycled'] = result[0]['total'] if result and result[0]['total'] else 0
            
            # Geri Dönüşüm Oranı
            if metrics['total_consumption'] > 0:
                metrics['recycling_ratio'] = (metrics['total_recycled'] / metrics['total_consumption']) * 100
            else:
                metrics['recycling_ratio'] = 0

            return metrics

        except Exception as e:
            logging.error(f"Su metrikleri hesaplama hatası: {e}")
            return {}

    def add_water_quality(self, company_id: int, year: int, location: str,
                         parameter_name: str, parameter_value: float, unit: str,
                         standard_limit: float = None, month: int = None) -> bool:
        """Su kalitesi ekle"""
        cid = self._ensure_context(company_id)

        try:
            # Uyumluluk durumunu belirle
            compliance_status = "Compliant"
            if standard_limit and parameter_value > standard_limit:
                compliance_status = "Non-compliant"

            self.execute_update("""
                INSERT INTO water_quality 
                (company_id, year, month, location, parameter_name, parameter_value,
                 unit, standard_limit, compliance_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, year, month, location, parameter_name, parameter_value,
                  unit, standard_limit, compliance_status))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('water_quality_add_error', 'Su kalitesi ekleme hatası')}: {e}")
            return False

    def add_water_efficiency_project(self, company_id: int, project_name: str,
                                   project_type: str, start_date: str, end_date: str,
                                   investment_cost: float, water_savings: float,
                                   savings_unit: str, cost_savings: float = None,
                                   payback_period: float = None) -> bool:
        """Su verimliliği projesi ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT INTO water_efficiency_projects 
                (company_id, project_name, project_type, start_date, end_date,
                 investment_cost, water_savings, savings_unit, cost_savings,
                 payback_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, project_name, project_type, start_date, end_date,
                  investment_cost, water_savings, savings_unit, cost_savings,
                  payback_period))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('water_efficiency_project_add_error', 'Su verimliliği projesi ekleme hatası')}: {e}")
            return False

    # --- Compatibility Methods for GRI/SDG Reporting ---

    def get_water_consumption(self, company_id: int) -> List[Dict]:
        """GRI/SDG raporlama uyumluluğu için alias"""
        records = self.get_water_records(company_id)
        # Add 'period' field for compatibility
        for r in records:
             if 'date' in r and r['date']:
                 try:
                     r['period'] = str(r['date'])[:4]
                 except:
                     pass
        return records

    def calculate_water_footprint(self, company_id: int, period: str = None) -> Dict:
        """GRI 303 ve SDG 6 için su ayak izi hesaplama (Uyumluluk Modu)"""
        cid = self._ensure_context(company_id)
        year = int(period) if period and str(period).isdigit() else None
        
        metrics = {
            'total_water_footprint': 0,
            'total_blue_water': 0,
            'total_green_water': 0,
            'total_grey_water': 0,
            'efficiency_metrics': {
                'average_efficiency_ratio': 0,
                'average_recycling_rate': 0
            },
            'breakdown_by_source': {}
        }

        try:
            # Base query
            query = "SELECT consumption_type, SUM(consumption_amount) as total FROM water_consumption WHERE company_id = ?"
            params = [cid]
            if year:
                query += " AND year = ?"
                params.append(year)
            
            query += " GROUP BY consumption_type"
            
            rows = self.execute_query(query, tuple(params), company_id=cid)
            
            total = 0
            for row in rows:
                c_type = row['consumption_type']
                amount = row['total'] or 0
                total += amount
                
                # Simple categorization
                c_type_lower = c_type.lower()
                if 'rain' in c_type_lower or 'yeşil' in c_type_lower or 'green' in c_type_lower:
                    metrics['total_green_water'] += amount
                elif 'polluted' in c_type_lower or 'grey' in c_type_lower or 'gri' in c_type_lower or 'waste' in c_type_lower:
                    metrics['total_grey_water'] += amount
                else:
                    # Default to Blue for Mains, Ground, Surface
                    metrics['total_blue_water'] += amount
                    
                # Breakdown
                metrics['breakdown_by_source'][c_type] = {
                    'total': amount,
                    'blue_water': amount if 'rain' not in c_type_lower and 'grey' not in c_type_lower else 0,
                    'green_water': amount if 'rain' in c_type_lower else 0,
                    'grey_water': amount if 'grey' in c_type_lower else 0
                }

            metrics['total_water_footprint'] = total
            
            # Recycled
            recycling_metrics = self.calculate_water_metrics(cid, year)
            metrics['efficiency_metrics']['average_recycling_rate'] = recycling_metrics.get('recycling_ratio', 0)
            
            return metrics
            
        except Exception as e:
            logging.error(f"Water footprint calculation error: {e}")
            return metrics

    def set_water_target(self, company_id: int, target_year: int, target_type: str,
                        baseline_year: int, baseline_consumption: float,
                        target_reduction_percent: float, recycling_target_percent: float = None) -> bool:
        """Su hedefi belirle"""
        cid = self._ensure_context(company_id)
        
        try:
            target_consumption = baseline_consumption * (1 - target_reduction_percent / 100)
            
            self.execute_update("""
                INSERT INTO water_targets
                (company_id, target_year, target_type, baseline_year, baseline_consumption,
                target_reduction_percent, target_consumption, recycling_target_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, target_year, target_type, baseline_year, baseline_consumption,
                  target_reduction_percent, target_consumption, recycling_target_percent))
            return True
            
        except Exception as e:
            logging.error(f"Water target set error: {e}")
            return False
