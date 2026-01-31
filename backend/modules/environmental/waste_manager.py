#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atık Yönetimi Modülü
Atık türleri, geri dönüşüm ve atık azaltma yönetimi
"""

import logging
import os
import sqlite3
from typing import Dict, List

from utils.language_manager import LanguageManager
from config.database import DB_PATH


class WasteManager:
    """Atık yönetimi ve geri dönüşüm"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.lm = LanguageManager()
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        return self.calculate_waste_metrics(company_id)

    def get_recent_records(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Son eklenen kayıtları getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        records = []

        try:
            # Check schema to handle column name differences
            cursor.execute("PRAGMA table_info(waste_generation)")
            columns = [info[1] for info in cursor.fetchall()]
            
            amount_col = 'amount' if 'amount' in columns else 'waste_amount'
            
            query = f"""
                SELECT waste_type, {amount_col}, unit, disposal_method, created_at 
                FROM waste_generation 
                WHERE company_id = ? 
                ORDER BY created_at DESC LIMIT ?
            """
            
            cursor.execute(query, (company_id, limit))
            
            for row in cursor.fetchall():
                records.append({
                    'type': row[0],
                    'amount': row[1],
                    'unit': row[2],
                    'method': row[3],
                    'date': row[4]
                })
            
            return records
        except Exception as e:
            logging.error(f"Waste recent records error: {e}")
            return []
        finally:
            conn.close()

    def get_waste_records(self, company_id: int, year: str = None) -> List[Dict]:
        """Atık kayıtlarını getir (Raporlama için)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        records = []

        try:
            # Check schema
            cursor.execute("PRAGMA table_info(waste_generation)")
            columns = [info[1] for info in cursor.fetchall()]
            
            amount_col = 'amount' if 'amount' in columns else 'waste_amount'
            category_col = 'waste_category' if 'waste_category' in columns else 'waste_type' # Fallback to type if category missing
            
            # Construct dynamic query based on available columns
            select_parts = [
                "'Atık Üretimi' as type",
                f"{category_col} as category",
                f"{amount_col} as amount",
                "unit",
                "disposal_method",
                "created_at"
            ]
            
            if 'disposal_cost' in columns: select_parts.append("disposal_cost")
            else: select_parts.append("0 as disposal_cost")
            
            if 'location' in columns: select_parts.append("location")
            else: select_parts.append("NULL as location")
            
            if 'invoice_date' in columns: select_parts.append("invoice_date")
            else: select_parts.append("NULL as invoice_date")
            
            if 'due_date' in columns: select_parts.append("due_date")
            else: select_parts.append("NULL as due_date")
            
            if 'supplier' in columns: select_parts.append("supplier")
            else: select_parts.append("NULL as supplier")
            
            query = f"SELECT {', '.join(select_parts)} FROM waste_generation WHERE company_id = ?"
            params = [company_id]
            
            if year and year.isdigit() and 'year' in columns:
                query += " AND year = ?"
                params.append(int(year))
                
            cursor.execute(query, params)
            for row in cursor.fetchall():
                records.append({
                    'type': row[0],
                    'category': row[1],
                    'amount': row[2],
                    'unit': row[3],
                    'method': row[4],
                    'date': row[5],
                    'cost': row[6],
                    'location': row[7],
                    'invoice_date': row[8],
                    'due_date': row[9],
                    'supplier': row[10]
                })

            # Geri dönüşüm kayıtları (if table exists)
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='waste_recycling'")
                if cursor.fetchone():
                    # Similar logic for recycling table... keeping it simple for now as it might not be populated
                    pass
            except:
                pass
                
            return records

        except Exception as e:
            logging.error(f"Atık kayıtları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def calculate_waste_metrics(self, company_id: int, year: int = None) -> Dict:
        """Atık metriklerini hesapla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        metrics = {}

        try:
            # Check schema
            cursor.execute("PRAGMA table_info(waste_generation)")
            columns = [info[1] for info in cursor.fetchall()]
            amount_col = 'amount' if 'amount' in columns else 'waste_amount'

            # Toplam Atık
            query = f"SELECT SUM({amount_col}) FROM waste_generation WHERE company_id = ?"
            params = [company_id]
            if year and 'year' in columns:
                query += " AND year = ?"
                params.append(year)
            cursor.execute(query, params)
            metrics['total_waste'] = cursor.fetchone()[0] or 0

            # Toplam Geri Dönüşüm - Check if table exists first
            metrics['total_recycled'] = 0
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='waste_recycling'")
            if cursor.fetchone():
                query = "SELECT SUM(recycled_amount) FROM waste_recycling WHERE company_id = ?"
                cursor.execute(query, [company_id]) # Recycled amount likely correct in that table or needs check
                metrics['total_recycled'] = cursor.fetchone()[0] or 0
            
            # Geri Dönüşüm Oranı
            if metrics['total_waste'] > 0:
                metrics['recycling_ratio'] = (metrics['total_recycled'] / metrics['total_waste']) * 100
            else:
                metrics['recycling_ratio'] = 0

            return metrics

        except Exception as e:
            logging.error(f"Atık metrikleri hesaplama hatası: {e}")
            return {'total_waste': 0, 'total_recycled': 0, 'recycling_ratio': 0}
        finally:
            conn.close()

    def _init_db_tables(self):
        """Atık yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Atık üretimi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_generation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    waste_type TEXT NOT NULL,
                    waste_category TEXT NOT NULL,
                    waste_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    disposal_method TEXT,
                    disposal_cost REAL,
                    location TEXT,
                    hazardous_status TEXT,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            # Migration: Check for new columns and add if missing
            cursor.execute("PRAGMA table_info(waste_generation)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'invoice_date' not in columns:
                try:
                    cursor.execute("ALTER TABLE waste_generation ADD COLUMN invoice_date TEXT")
                    logging.info("Added invoice_date column to waste_generation")
                except Exception as e:
                    logging.error(f"Migration error (invoice_date): {e}")
                    
            if 'due_date' not in columns:
                try:
                    cursor.execute("ALTER TABLE waste_generation ADD COLUMN due_date TEXT")
                    logging.info("Added due_date column to waste_generation")
                except Exception as e:
                    logging.error(f"Migration error (due_date): {e}")

            if 'supplier' not in columns:
                try:
                    cursor.execute("ALTER TABLE waste_generation ADD COLUMN supplier TEXT")
                    logging.info("Added supplier column to waste_generation")
                except Exception as e:
                    logging.error(f"Migration error (supplier): {e}")

            # Atık geri dönüşümü
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_recycling (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    waste_type TEXT NOT NULL,
                    recycled_amount REAL NOT NULL,
                    unit TEXT NOT NULL,
                    recycling_method TEXT,
                    recycling_rate REAL,
                    revenue REAL,
                    location TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Atık azaltma projeleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_reduction_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    investment_cost REAL,
                    waste_reduction REAL,
                    reduction_unit TEXT,
                    cost_savings REAL,
                    payback_period REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Atık hedefleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_year INTEGER,
                    baseline_generation REAL,
                    target_reduction_percent REAL,
                    target_generation REAL,
                    recycling_target_percent REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Atık türleri ve kategorileri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    waste_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    hazardous TEXT,
                    recycling_potential TEXT,
                    disposal_method TEXT,
                    environmental_impact TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Varsayılan atık kategorilerini ekle
            self._add_default_waste_categories(cursor)

            conn.commit()
            logging.info(f"[OK] {self.lm.tr('waste_module_tables_created', 'Atık yönetimi modülü tabloları başarıyla oluşturuldu')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('waste_module_table_error', 'Atık yönetimi modülü tablo oluşturma')}: {e}")
            conn.rollback()
        finally:
            conn.close()

    def _add_default_waste_categories(self, cursor) -> None:
        """Varsayılan atık kategorilerini ekle"""
        categories = [
            # Organik atıklar
            (self.lm.tr('organic_waste', 'Organik Atık'), self.lm.tr('organic', 'Organik'), 'Non-hazardous', 'High', self.lm.tr('compost', 'Kompost'), 'Low'),
            (self.lm.tr('food_waste', 'Gıda Atığı'), self.lm.tr('organic', 'Organik'), 'Non-hazardous', 'High', self.lm.tr('compost', 'Kompost'), 'Low'),

            # Kağıt ve karton
            (self.lm.tr('paper', 'Kağıt'), self.lm.tr('recyclable', 'Geri Dönüştürülebilir'), 'Non-hazardous', 'Very High', self.lm.tr('recycling', 'Recycling'), 'Low'),
            (self.lm.tr('cardboard', 'Karton'), self.lm.tr('recyclable', 'Geri Dönüştürülebilir'), 'Non-hazardous', 'Very High', self.lm.tr('recycling', 'Recycling'), 'Low'),

            # Plastik
            (self.lm.tr('plastic', 'Plastik'), self.lm.tr('recyclable', 'Geri Dönüştürülebilir'), 'Non-hazardous', 'Medium', self.lm.tr('recycling', 'Recycling'), 'High'),
            ('PET', self.lm.tr('recyclable', 'Geri Dönüştürülebilir'), 'Non-hazardous', 'High', self.lm.tr('recycling', 'Recycling'), 'High'),

            # Metal
            (self.lm.tr('metal', 'Metal'), self.lm.tr('recyclable', 'Geri Dönüştürülebilir'), 'Non-hazardous', 'Very High', self.lm.tr('recycling', 'Recycling'), 'Medium'),
            (self.lm.tr('aluminum', 'Alüminyum'), self.lm.tr('recyclable', 'Geri Dönüştürülebilir'), 'Non-hazardous', 'Very High', self.lm.tr('recycling', 'Recycling'), 'Medium'),

            # Cam
            (self.lm.tr('glass', 'Cam'), self.lm.tr('recyclable', 'Geri Dönüştürülebilir'), 'Non-hazardous', 'Very High', self.lm.tr('recycling', 'Recycling'), 'Low'),

            # Tehlikeli atıklar
            (self.lm.tr('electronic_waste', 'Elektronik Atık'), self.lm.tr('hazardous', 'Tehlikeli'), 'Hazardous', 'Medium', self.lm.tr('special_treatment', 'Special Treatment'), 'High'),
            (self.lm.tr('chemical_waste', 'Kimyasal Atık'), self.lm.tr('hazardous', 'Tehlikeli'), 'Hazardous', 'Low', self.lm.tr('special_treatment', 'Special Treatment'), 'Very High'),
            (self.lm.tr('paint_waste', 'Boya Atığı'), self.lm.tr('hazardous', 'Tehlikeli'), 'Hazardous', 'Low', self.lm.tr('special_treatment', 'Special Treatment'), 'High'),

            # İnşaat atıkları
            (self.lm.tr('construction_waste', 'İnşaat Atığı'), self.lm.tr('inert', 'İnert'), 'Non-hazardous', 'Low', self.lm.tr('landfill', 'Landfill'), 'Medium'),
            (self.lm.tr('concrete', 'Beton'), self.lm.tr('inert', 'İnert'), 'Non-hazardous', 'Medium', self.lm.tr('recycling', 'Recycling'), 'Low'),
        ]

        for waste_type, category, hazardous, recycling_potential, disposal_method, environmental_impact in categories:
            cursor.execute("""
                INSERT OR IGNORE INTO waste_categories 
                (waste_type, category, hazardous, recycling_potential, disposal_method, environmental_impact)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (waste_type, category, hazardous, recycling_potential, disposal_method, environmental_impact))

    def add_waste_generation(self, company_id: int, year: int, waste_type: str,
                           waste_category: str, waste_amount: float, unit: str,
                           disposal_method: str = None, disposal_cost: float = None,
                           location: str = None, hazardous_status: str = None, month: int = None,
                           invoice_date: str = None, due_date: str = None, supplier: str = None) -> bool:
        """Atık üretimi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO waste_generation 
                (company_id, year, month, waste_type, waste_category, waste_amount,
                 unit, disposal_method, disposal_cost, location, hazardous_status,
                 invoice_date, due_date, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, month, waste_type, waste_category, waste_amount,
                  unit, disposal_method, disposal_cost, location, hazardous_status,
                  invoice_date, due_date, supplier))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('waste_generation_add_error', 'Atık üretimi ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_waste_recycling(self, company_id: int, year: int, waste_type: str,
                          recycled_amount: float, unit: str, recycling_method: str = None,
                          recycling_rate: float = None, revenue: float = None,
                          location: str = None, month: int = None) -> bool:
        """Atık geri dönüşümü ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO waste_recycling 
                (company_id, year, month, waste_type, recycled_amount, unit,
                 recycling_method, recycling_rate, revenue, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, month, waste_type, recycled_amount, unit,
                  recycling_method, recycling_rate, revenue, location))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('waste_recycling_add_error', 'Atık geri dönüşümü ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_waste_reduction_project(self, company_id: int, project_name: str,
                                  project_type: str, start_date: str, end_date: str,
                                  investment_cost: float, waste_reduction: float,
                                  reduction_unit: str, cost_savings: float = None,
                                  payback_period: float = None) -> bool:
        """Atık azaltma projesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO waste_reduction_projects 
                (company_id, project_name, project_type, start_date, end_date,
                 investment_cost, waste_reduction, reduction_unit, cost_savings,
                 payback_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, project_name, project_type, start_date, end_date,
                  investment_cost, waste_reduction, reduction_unit, cost_savings,
                  payback_period))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('waste_reduction_project_add_error', 'Atık azaltma projesi ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def set_waste_target(self, company_id: int, target_year: int, target_type: str,
                        baseline_year: int, baseline_generation: float,
                        target_reduction_percent: float, recycling_target_percent: float = None) -> bool:
        """Atık hedefi belirle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            target_generation = baseline_generation * (1 - target_reduction_percent / 100)

            cursor.execute("""
                INSERT OR REPLACE INTO waste_targets 
                (company_id, target_year, target_type, baseline_year, 
                 baseline_generation, target_reduction_percent, target_generation,
                 recycling_target_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, target_year, target_type, baseline_year,
                  baseline_generation, target_reduction_percent, target_generation,
                  recycling_target_percent))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('waste_target_set_error', 'Atık hedefi belirleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_waste_summary(self, company_id: int, year: int) -> Dict:
        """Atık özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Toplam atık üretimi
            cursor.execute("""
                SELECT waste_type, waste_category, SUM(waste_amount), unit, SUM(disposal_cost)
                FROM waste_generation 
                WHERE company_id = ? AND year = ?
                GROUP BY waste_type, waste_category, unit
            """, (company_id, year))

            waste_generation = {}
            total_cost = 0
            for row in cursor.fetchall():
                waste_type, category, amount, unit, cost = row
                if waste_type not in waste_generation:
                    waste_generation[waste_type] = {
                        'category': category,
                        'amount': 0,
                        'unit': unit,
                        'cost': 0
                    }
                waste_generation[waste_type]['amount'] += amount
                waste_generation[waste_type]['cost'] += cost or 0
                total_cost += cost or 0

            # Atık geri dönüşümü
            cursor.execute("""
                SELECT waste_type, SUM(recycled_amount), unit, SUM(revenue)
                FROM waste_recycling 
                WHERE company_id = ? AND year = ?
                GROUP BY waste_type, unit
            """, (company_id, year))

            waste_recycling = {}
            total_revenue = 0
            for row in cursor.fetchall():
                waste_type, amount, unit, revenue = row
                waste_recycling[waste_type] = {
                    'amount': amount,
                    'unit': unit,
                    'revenue': revenue or 0
                }
                total_revenue += revenue or 0

            # Toplam atık üretimi (ton cinsinden)
            total_generation = 0
            for data in waste_generation.values():
                if data['unit'] == 'ton':
                    total_generation += data['amount']
                elif data['unit'] == 'kg':
                    total_generation += data['amount'] / 1000
                elif data['unit'] == 'g':
                    total_generation += data['amount'] / 1000000

            # Toplam geri dönüşüm (ton cinsinden)
            total_recycled = 0
            for data in waste_recycling.values():
                if data['unit'] == 'ton':
                    total_recycled += data['amount']
                elif data['unit'] == 'kg':
                    total_recycled += data['amount'] / 1000
                elif data['unit'] == 'g':
                    total_recycled += data['amount'] / 1000000

            # Geri dönüşüm oranı
            recycling_ratio = (total_recycled / total_generation * 100) if total_generation > 0 else 0

            # Tehlikeli atık oranı
            cursor.execute("""
                SELECT SUM(waste_amount) FROM waste_generation 
                WHERE company_id = ? AND year = ? AND hazardous_status = 'Hazardous'
            """, (company_id, year))
            hazardous_amount = cursor.fetchone()[0] or 0
            hazardous_ratio = (hazardous_amount / total_generation * 100) if total_generation > 0 else 0

            return {
                'waste_generation': waste_generation,
                'waste_recycling': waste_recycling,
                'total_generation': total_generation,
                'total_recycled': total_recycled,
                'recycling_ratio': recycling_ratio,
                'hazardous_ratio': hazardous_ratio,
                'total_cost': total_cost,
                'total_revenue': total_revenue,
                'year': year,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"{self.lm.tr('waste_summary_get_error', 'Atık özeti getirme hatası')}: {e}")
            return {}
        finally:
            conn.close()

    def get_waste_targets(self, company_id: int) -> List[Dict]:
        """Atık hedeflerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT target_year, target_type, baseline_year, baseline_generation,
                       target_reduction_percent, target_generation, recycling_target_percent, status
                FROM waste_targets 
                WHERE company_id = ? AND status = 'active'
                ORDER BY target_year
            """, (company_id,))

            targets = []
            for row in cursor.fetchall():
                targets.append({
                    'target_year': row[0],
                    'target_type': row[1],
                    'baseline_year': row[2],
                    'baseline_generation': row[3],
                    'target_reduction_percent': row[4],
                    'target_generation': row[5],
                    'recycling_target_percent': row[6],
                    'status': row[7]
                })

            return targets

        except Exception as e:
            logging.error(f"Atık hedefleri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_waste_categories(self) -> List[Dict]:
        """Atık kategorilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT waste_type, category, hazardous, recycling_potential, 
                       disposal_method, environmental_impact
                FROM waste_categories 
                ORDER BY category, waste_type
            """)

            categories = []
            for row in cursor.fetchall():
                categories.append({
                    'waste_type': row[0],
                    'category': row[1],
                    'hazardous': row[2],
                    'recycling_potential': row[3],
                    'disposal_method': row[4],
                    'environmental_impact': row[5]
                })

            return categories

        except Exception as e:
            logging.error(f"{self.lm.tr('waste_categories_get_error', 'Atık kategorileri getirme hatası')}: {e}")
            return []
        finally:
            conn.close()

    def calculate_waste_kpis(self, company_id: int, year: int) -> Dict:
        """Atık KPI'larını hesapla"""
        summary = self.get_waste_summary(company_id, year)

        if not summary:
            return {}

        # Atık yoğunluğu (ton/çalışan veya ton/üretim)
        waste_intensity_per_employee = summary['total_generation'] / 100  # Örnek: 100 çalışan
        waste_intensity_per_production = summary['total_generation'] / 1000  # Örnek: 1000 birim üretim

        return {
            'total_waste_generation': summary['total_generation'],
            'waste_recycling_ratio': summary['recycling_ratio'],
            'hazardous_waste_ratio': summary['hazardous_ratio'],
            'waste_cost': summary['total_cost'],
            'recycling_revenue': summary['total_revenue'],
            'waste_intensity_per_employee': waste_intensity_per_employee,
            'waste_intensity_per_production': waste_intensity_per_production,
            'year': year,
            'company_id': company_id
        }
