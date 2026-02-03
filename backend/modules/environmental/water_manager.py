#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Su Yönetimi Modülü
Su tüketimi, geri dönüşüm ve su verimliliği yönetimi
"""

import logging
import os
import sqlite3
from typing import Dict, List

try:
    from utils.language_manager import LanguageManager
    from config.database import DB_PATH
except ImportError:
    from backend.utils.language_manager import LanguageManager
    from backend.config.database import DB_PATH


class WaterManager:
    """Su tüketimi ve su yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.lm = LanguageManager()
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        return self.calculate_water_metrics(company_id)

    def get_recent_records(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Son eklenen kayıtları getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        records = []

        try:
            # Check table schema first to handle different versions
            cursor.execute("PRAGMA table_info(water_consumption)")
            columns = [info[1] for info in cursor.fetchall()]
            
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
            
            cursor.execute(query, (company_id, limit))
            
            for row in cursor.fetchall():
                records.append({
                    'type': row[0],
                    'amount': row[1],
                    'unit': row[2],
                    'source': row[3],
                    'date': row[4]
                })
            
            return records
        except Exception as e:
            logging.error(f"Water recent records error: {e}")
            return []
        finally:
            conn.close()

    def _init_db_tables(self) -> None:
        """Su yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Su tüketimi
            cursor.execute("""
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

            # Migration: Add missing columns if they don't exist
            cursor.execute("PRAGMA table_info(water_consumption)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'invoice_date' not in columns:
                cursor.execute("ALTER TABLE water_consumption ADD COLUMN invoice_date TEXT")
            if 'due_date' not in columns:
                cursor.execute("ALTER TABLE water_consumption ADD COLUMN due_date TEXT")
            if 'supplier' not in columns:
                cursor.execute("ALTER TABLE water_consumption ADD COLUMN supplier TEXT")

            # Su geri dönüşümü
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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

            conn.commit()
            logging.info(f"[OK] {self.lm.tr('water_module_tables_created', 'Su yönetimi modülü tabloları başarıyla oluşturuldu')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('water_module_table_error', 'Su yönetimi modülü tablo oluşturma')}: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_water_consumption(self, company_id: int, year: int, consumption_type: str,
                            consumption_amount: float, unit: str, cost: float = None,
                            source: str = None, location: str = None, month: int = None,
                            quality_parameters: str = None,
                            invoice_date: str = None, due_date: str = None, supplier: str = None) -> bool:
        """Su tüketimi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO water_consumption 
                (company_id, year, month, consumption_type, consumption_amount, 
                 unit, cost, source, location, quality_parameters,
                 invoice_date, due_date, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, month, consumption_type, consumption_amount,
                  unit, cost, source, location, quality_parameters,
                  invoice_date, due_date, supplier))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('water_consumption_add_error', 'Su tüketimi ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_water_recycling(self, company_id: int, year: int, recycling_type: str,
                          recycled_amount: float, unit: str, treatment_method: str = None,
                          reuse_purpose: str = None, cost_savings: float = None) -> bool:
        """Su geri dönüşümü ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO water_recycling 
                (company_id, year, recycling_type, recycled_amount, unit,
                 treatment_method, reuse_purpose, cost_savings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, recycling_type, recycled_amount, unit,
                  treatment_method, reuse_purpose, cost_savings))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('water_recycling_add_error', 'Su geri dönüşümü ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_water_records(self, company_id: int, year: str = None) -> List[Dict]:
        """Su kayıtlarını getir (Raporlama için)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        records = []

        try:
            query = """
                SELECT 'Tüketim' as type, consumption_type as category, consumption_amount, unit, 
                       cost, source, location, invoice_date, due_date, supplier, created_at
                FROM water_consumption 
                WHERE company_id = ?
            """
            params = [company_id]
            
            if year and year.isdigit():
                query += " AND year = ?"
                params.append(int(year))
                
            cursor.execute(query, params)
            for row in cursor.fetchall():
                records.append({
                    'type': row[0],
                    'category': row[1],
                    'amount': row[2],
                    'unit': row[3],
                    'cost': row[4],
                    'source': row[5],
                    'location': row[6],
                    'invoice_date': row[7],
                    'due_date': row[8],
                    'supplier': row[9],
                    'date': row[10]
                })

            # Geri dönüşüm kayıtları
            query_recycling = """
                SELECT 'Geri Dönüşüm' as type, recycling_type as category, recycled_amount, unit, 
                       cost_savings, treatment_method, reuse_purpose, created_at
                FROM water_recycling 
                WHERE company_id = ?
            """
            params_recycling = [company_id]
            
            if year and year.isdigit():
                query_recycling += " AND year = ?"
                params_recycling.append(int(year))
                
            cursor.execute(query_recycling, params_recycling)
            for row in cursor.fetchall():
                records.append({
                    'type': row[0],
                    'category': row[1],
                    'amount': row[2],
                    'unit': row[3],
                    'cost': row[4], # cost_savings mapped to cost field for consistency or handled separately
                    'source': row[5], # treatment_method
                    'location': row[6], # reuse_purpose
                    'date': row[7]
                })
                
            return records

        except Exception as e:
            logging.error(f"Su kayıtları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def calculate_water_metrics(self, company_id: int, year: int = None) -> Dict:
        """Su metriklerini hesapla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        metrics = {}

        try:
            # Toplam Tüketim
            query = "SELECT SUM(consumption_amount) FROM water_consumption WHERE company_id = ?"
            params = [company_id]
            if year:
                query += " AND year = ?"
                params.append(year)
            cursor.execute(query, params)
            metrics['total_consumption'] = cursor.fetchone()[0] or 0

            # Toplam Geri Dönüşüm
            query = "SELECT SUM(recycled_amount) FROM water_recycling WHERE company_id = ?"
            if year:
                query += " AND year = ?"
            cursor.execute(query, params)
            metrics['total_recycled'] = cursor.fetchone()[0] or 0
            
            # Geri Dönüşüm Oranı
            if metrics['total_consumption'] > 0:
                metrics['recycling_ratio'] = (metrics['total_recycled'] / metrics['total_consumption']) * 100
            else:
                metrics['recycling_ratio'] = 0

            return metrics

        except Exception as e:
            logging.error(f"Su metrikleri hesaplama hatası: {e}")
            return {}
        finally:
            conn.close()

    def add_water_quality(self, company_id: int, year: int, location: str,
                         parameter_name: str, parameter_value: float, unit: str,
                         standard_limit: float = None, month: int = None) -> bool:
        """Su kalitesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Uyumluluk durumunu belirle
            compliance_status = "Compliant"
            if standard_limit and parameter_value > standard_limit:
                compliance_status = "Non-compliant"

            cursor.execute("""
                INSERT INTO water_quality 
                (company_id, year, month, location, parameter_name, parameter_value,
                 unit, standard_limit, compliance_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, month, location, parameter_name, parameter_value,
                  unit, standard_limit, compliance_status))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('water_quality_add_error', 'Su kalitesi ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_water_efficiency_project(self, company_id: int, project_name: str,
                                   project_type: str, start_date: str, end_date: str,
                                   investment_cost: float, water_savings: float,
                                   savings_unit: str, cost_savings: float = None,
                                   payback_period: float = None) -> bool:
        """Su verimliliği projesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO water_efficiency_projects 
                (company_id, project_name, project_type, start_date, end_date,
                 investment_cost, water_savings, savings_unit, cost_savings,
                 payback_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, project_name, project_type, start_date, end_date,
                  investment_cost, water_savings, savings_unit, cost_savings,
                  payback_period))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('water_efficiency_project_add_error', 'Su verimliliği projesi ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

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
        year = int(period) if period and period.isdigit() else None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
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
            query = "SELECT consumption_type, SUM(consumption_amount) FROM water_consumption WHERE company_id = ?"
            params = [company_id]
            if year:
                query += " AND year = ?"
                params.append(year)
            
            query += " GROUP BY consumption_type"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            total = 0
            for c_type, amount in rows:
                amount = amount or 0
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
            recycling_metrics = self.calculate_water_metrics(company_id, year)
            metrics['efficiency_metrics']['average_recycling_rate'] = recycling_metrics.get('recycling_ratio', 0)
            
            return metrics
            
        except Exception as e:
            logging.error(f"Water footprint calculation error: {e}")
            return metrics
        finally:
            conn.close()

    def set_water_target(self, company_id: int, target_year: int, target_type: str,
                        baseline_year: int, baseline_consumption: float,
                        target_reduction_percent: float, recycling_target_percent: float = None) -> bool:
        """Su hedefi belirle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            target_consumption = baseline_consumption * (1 - target_reduction_percent / 100)

            cursor.execute("""
                INSERT OR REPLACE INTO water_targets 
                (company_id, target_year, target_type, baseline_year, 
                 baseline_consumption, target_reduction_percent, target_consumption,
                 recycling_target_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, target_year, target_type, baseline_year,
                  baseline_consumption, target_reduction_percent, target_consumption,
                  recycling_target_percent))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('water_target_set_error', 'Su hedefi belirleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_water_summary(self, company_id: int, year: int) -> Dict:
        """Su özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Toplam su tüketimi
            cursor.execute("""
                SELECT consumption_type, SUM(consumption_amount), unit, SUM(cost)
                FROM water_consumption 
                WHERE company_id = ? AND year = ?
                GROUP BY consumption_type, unit
            """, (company_id, year))

            water_consumption = {}
            total_cost = 0
            for row in cursor.fetchall():
                consumption_type, amount, unit, cost = row
                water_consumption[consumption_type] = {
                    'amount': amount,
                    'unit': unit,
                    'cost': cost or 0
                }
                total_cost += cost or 0

            # Su geri dönüşümü
            cursor.execute("""
                SELECT recycling_type, SUM(recycled_amount), unit, SUM(cost_savings)
                FROM water_recycling 
                WHERE company_id = ? AND year = ?
                GROUP BY recycling_type, unit
            """, (company_id, year))

            water_recycling = {}
            total_savings = 0
            for row in cursor.fetchall():
                recycling_type, amount, unit, savings = row
                water_recycling[recycling_type] = {
                    'amount': amount,
                    'unit': unit,
                    'savings': savings or 0
                }
                total_savings += savings or 0

            # Toplam su tüketimi (m³ cinsinden)
            total_consumption = 0
            for data in water_consumption.values():
                if data['unit'] == 'm³' or data['unit'] == 'm3':
                    total_consumption += data['amount']
                elif data['unit'] == 'L':
                    total_consumption += data['amount'] / 1000
                elif data['unit'] == 'kL':
                    total_consumption += data['amount']

            # Toplam geri dönüşüm (m³ cinsinden)
            total_recycled = 0
            for data in water_recycling.values():
                if data['unit'] == 'm³' or data['unit'] == 'm3':
                    total_recycled += data['amount']
                elif data['unit'] == 'L':
                    total_recycled += data['amount'] / 1000
                elif data['unit'] == 'kL':
                    total_recycled += data['amount']

            # Geri dönüşüm oranı
            recycling_ratio = (total_recycled / total_consumption * 100) if total_consumption > 0 else 0

            # Su kalitesi uyumluluk
            cursor.execute("""
                SELECT COUNT(*), SUM(CASE WHEN compliance_status = 'Compliant' THEN 1 ELSE 0 END)
                FROM water_quality 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))

            quality_result = cursor.fetchone()
            total_quality_tests = quality_result[0] or 0
            compliant_tests = quality_result[1] or 0
            quality_compliance_rate = (compliant_tests / total_quality_tests * 100) if total_quality_tests > 0 else 0

            return {
                'water_consumption': water_consumption,
                'water_recycling': water_recycling,
                'total_consumption': total_consumption,
                'total_recycled': total_recycled,
                'recycling_ratio': recycling_ratio,
                'total_cost': total_cost,
                'total_savings': total_savings,
                'quality_compliance_rate': quality_compliance_rate,
                'total_quality_tests': total_quality_tests,
                'year': year,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"{self.lm.tr('water_summary_get_error', 'Su özeti getirme hatası')}: {e}")
            return {}
        finally:
            conn.close()

    def get_water_targets(self, company_id: int) -> List[Dict]:
        """Su hedeflerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT target_year, target_type, baseline_year, baseline_consumption,
                       target_reduction_percent, target_consumption, recycling_target_percent, status
                FROM water_targets 
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
                    'recycling_target_percent': row[6],
                    'status': row[7]
                })

            return targets

        except Exception as e:
            logging.error(f"{self.lm.tr('water_targets_get_error', 'Su hedefleri getirme hatası')}: {e}")
            return []
        finally:
            conn.close()

    def get_water_quality_summary(self, company_id: int, year: int) -> Dict:
        """Su kalitesi özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT location, parameter_name, AVG(parameter_value), unit,
                       standard_limit, SUM(CASE WHEN compliance_status = 'Compliant' THEN 1 ELSE 0 END),
                       COUNT(*)
                FROM water_quality 
                WHERE company_id = ? AND year = ?
                GROUP BY location, parameter_name, unit, standard_limit
            """, (company_id, year))

            quality_summary = {}
            for row in cursor.fetchall():
                location, param_name, avg_value, unit, std_limit, compliant_count, total_count = row

                if location not in quality_summary:
                    quality_summary[location] = {}

                quality_summary[location][param_name] = {
                    'average_value': avg_value,
                    'unit': unit,
                    'standard_limit': std_limit,
                    'compliance_rate': (compliant_count / total_count * 100) if total_count > 0 else 0,
                    'total_tests': total_count,
                    'compliant_tests': compliant_count
                }

            return quality_summary

        except Exception as e:
            logging.error(f"{self.lm.tr('water_quality_summary_get_error', 'Su kalitesi özeti getirme hatası')}: {e}")
            return {}
        finally:
            conn.close()

    def calculate_water_kpis(self, company_id: int, year: int) -> Dict:
        """Su KPI'larını hesapla"""
        summary = self.get_water_summary(company_id, year)

        if not summary:
            return {}

        # Su yoğunluğu (m³/çalışan veya m³/üretim)
        water_intensity_per_employee = summary['total_consumption'] / 100  # Örnek: 100 çalışan
        water_intensity_per_production = summary['total_consumption'] / 1000  # Örnek: 1000 birim üretim

        return {
            'total_water_consumption': summary['total_consumption'],
            'water_recycling_ratio': summary['recycling_ratio'],
            'water_cost': summary['total_cost'],
            'water_savings': summary['total_savings'],
            'quality_compliance_rate': summary['quality_compliance_rate'],
            'water_intensity_per_employee': water_intensity_per_employee,
            'water_intensity_per_production': water_intensity_per_production,
            'year': year,
            'company_id': company_id
        }
