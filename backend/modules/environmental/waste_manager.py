#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atık Yönetimi Modülü
Atık türleri, geri dönüşüm ve atık azaltma yönetimi
"""

import logging
import os
from typing import Dict, List, Optional, Any

# BaseTenantManager'ı içe aktar
try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from backend.core.base_manager import BaseTenantManager

try:
    from utils.language_manager import LanguageManager
    from config.database import DB_PATH
except ImportError:
    from backend.utils.language_manager import LanguageManager
    from backend.config.database import DB_PATH


class WasteManager(BaseTenantManager):
    """Atık yönetimi ve geri dönüşüm"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        self.lm = LanguageManager()
        final_db_path = db_path or DB_PATH
        if final_db_path and not os.path.isabs(final_db_path):
             base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
             final_db_path = os.path.join(base_dir, final_db_path)
        
        super().__init__(final_db_path, company_id)
        self._init_db_tables()
        self._migrate_tables()

    def _migrate_tables(self) -> None:
        """Tablo şemalarını güncelle"""
        try:
            # waste_generation tablosu için sütun kontrolü
            try:
                columns = [row['name'] for row in self.execute_query("PRAGMA table_info(waste_generation)")]
                
                if 'invoice_date' not in columns:
                    self.execute_update("ALTER TABLE waste_generation ADD COLUMN invoice_date TEXT")
                    logging.info("Added invoice_date column to waste_generation")
                    
                if 'due_date' not in columns:
                    self.execute_update("ALTER TABLE waste_generation ADD COLUMN due_date TEXT")
                    logging.info("Added due_date column to waste_generation")

                if 'supplier' not in columns:
                    self.execute_update("ALTER TABLE waste_generation ADD COLUMN supplier TEXT")
                    logging.info("Added supplier column to waste_generation")
                    
            except Exception as e:
                logging.error(f"Migration error for waste_generation: {e}")

        except Exception as e:
            logging.error(f"Migration general error: {e}")

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        return self.calculate_waste_metrics(company_id)

    def get_recent_records(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Son eklenen kayıtları getir"""
        cid = self._ensure_context(company_id)
        records = []

        try:
            # Check schema to handle column name differences
            columns = [row['name'] for row in self.execute_query("PRAGMA table_info(waste_generation)")]
            
            amount_col = 'amount' if 'amount' in columns else 'waste_amount'
            
            query = f"""
                SELECT waste_type, {amount_col}, unit, disposal_method, created_at 
                FROM waste_generation 
                WHERE company_id = ? 
                ORDER BY created_at DESC LIMIT ?
            """
            
            rows = self.execute_query(query, (cid, limit))
            
            for row in rows:
                records.append({
                    'type': row['waste_type'],
                    'amount': row[amount_col], # row uses column name as key
                    'unit': row['unit'],
                    'method': row['disposal_method'],
                    'date': row['created_at']
                })
            
            return records
        except Exception as e:
            logging.error(f"Waste recent records error: {e}")
            return []

    def get_waste_records(self, company_id: int, year: str = None) -> List[Dict]:
        """Atık kayıtlarını getir (Raporlama için)"""
        cid = self._ensure_context(company_id)
        records = []

        try:
            # Check schema
            columns = [row['name'] for row in self.execute_query("PRAGMA table_info(waste_generation)")]
            
            amount_col = 'amount' if 'amount' in columns else 'waste_amount'
            category_col = 'waste_category' if 'waste_category' in columns else 'waste_type'
            
            # Construct dynamic query based on available columns
            select_parts = [
                "'Atık Üretimi' as type",
                "waste_type",
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
            params = [cid]
            
            if year and str(year).isdigit() and 'year' in columns:
                query += " AND year = ?"
                params.append(int(year))
                
            rows = self.execute_query(query, tuple(params))
            for row in rows:
                records.append({
                    'type': row['type'],
                    'waste_type': row['waste_type'],
                    'category': row['category'],
                    'amount': row['amount'],
                    'unit': row['unit'],
                    'method': row['disposal_method'],
                    'date': row['created_at'],
                    'cost': row['disposal_cost'],
                    'location': row['location'],
                    'invoice_date': row['invoice_date'],
                    'due_date': row['due_date'],
                    'supplier': row['supplier']
                })

            # Geri dönüşüm kayıtları (if table exists)
            try:
                # Check if table exists
                tbl_check = self.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='waste_recycling'")
                if tbl_check:
                    # Logic for recycling records could be added here if needed
                    pass
            except:
                pass
                
            return records

        except Exception as e:
            logging.error(f"Atık kayıtları getirme hatası: {e}")
            return []

    def calculate_waste_metrics(self, company_id: int, year: int = None) -> Dict:
        """Atık metriklerini hesapla"""
        cid = self._ensure_context(company_id)
        metrics = {'total_waste': 0, 'total_recycled': 0, 'recycling_ratio': 0}

        try:
            # Check schema
            columns = [row['name'] for row in self.execute_query("PRAGMA table_info(waste_generation)")]
            amount_col = 'amount' if 'amount' in columns else 'waste_amount'

            # Toplam Atık
            query = f"SELECT SUM({amount_col}) as total FROM waste_generation WHERE company_id = ?"
            params = [cid]
            if year and 'year' in columns:
                query += " AND year = ?"
                params.append(year)
            
            res = self.execute_query(query, tuple(params))
            metrics['total_waste'] = res[0]['total'] if res and res[0]['total'] else 0

            # Toplam Geri Dönüşüm
            tbl_check = self.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='waste_recycling'")
            if tbl_check:
                query = "SELECT SUM(recycled_amount) as total FROM waste_recycling WHERE company_id = ?"
                res_rec = self.execute_query(query, (cid,))
                metrics['total_recycled'] = res_rec[0]['total'] if res_rec and res_rec[0]['total'] else 0
            
            # Geri Dönüşüm Oranı
            if metrics['total_waste'] > 0:
                metrics['recycling_ratio'] = (metrics['total_recycled'] / metrics['total_waste']) * 100
            else:
                metrics['recycling_ratio'] = 0

            return metrics

        except Exception as e:
            logging.error(f"Atık metrikleri hesaplama hatası: {e}")
            return metrics

    def _init_db_tables(self):
        """Atık yönetimi tablolarını oluştur"""
        try:
            # Atık üretimi
            self.execute_update("""
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
            
            # Atık geri dönüşümü
            self.execute_update("""
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
            self.execute_update("""
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
            self.execute_update("""
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
            self.execute_update("""
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
            self._add_default_waste_categories()

            logging.info(f"[OK] {self.lm.tr('waste_module_tables_created', 'Atık yönetimi modülü tabloları başarıyla oluşturuldu')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('waste_module_table_error', 'Atık yönetimi modülü tablo oluşturma')}: {e}")

    def _add_default_waste_categories(self) -> None:
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
            # Use direct DB access to avoid tenant filtering/context requirements for global lookup table
            self.db.execute_update("""
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
        cid = self._ensure_context(company_id)

        try:
            self.insert('waste_generation', {
                'company_id': cid,
                'year': year,
                'month': month,
                'waste_type': waste_type,
                'waste_category': waste_category,
                'waste_amount': waste_amount,
                'unit': unit,
                'disposal_method': disposal_method,
                'disposal_cost': disposal_cost,
                'location': location,
                'hazardous_status': hazardous_status,
                'invoice_date': invoice_date,
                'due_date': due_date,
                'supplier': supplier
            })
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('waste_generation_add_error', 'Atık üretimi ekleme hatası')}: {e}")
            return False

    def add_waste_recycling(self, company_id: int, year: int, waste_type: str,
                          recycled_amount: float, unit: str, recycling_method: str = None,
                          recycling_rate: float = None, revenue: float = None,
                          location: str = None, month: int = None) -> bool:
        """Atık geri dönüşümü ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.insert('waste_recycling', {
                'company_id': cid,
                'year': year,
                'month': month,
                'waste_type': waste_type,
                'recycled_amount': recycled_amount,
                'unit': unit,
                'recycling_method': recycling_method,
                'recycling_rate': recycling_rate,
                'revenue': revenue,
                'location': location
            })
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('waste_recycling_add_error', 'Atık geri dönüşümü ekleme hatası')}: {e}")
            return False

    def add_waste_reduction_project(self, company_id: int, project_name: str,
                                  project_type: str, start_date: str, end_date: str,
                                  investment_cost: float, waste_reduction: float,
                                  reduction_unit: str, cost_savings: float = None,
                                  payback_period: float = None) -> bool:
        """Atık azaltma projesi ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.insert('waste_reduction_projects', {
                'company_id': cid,
                'project_name': project_name,
                'project_type': project_type,
                'start_date': start_date,
                'end_date': end_date,
                'investment_cost': investment_cost,
                'waste_reduction': waste_reduction,
                'reduction_unit': reduction_unit,
                'cost_savings': cost_savings,
                'payback_period': payback_period
            })
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('waste_reduction_project_add_error', 'Atık azaltma projesi ekleme hatası')}: {e}")
            return False
