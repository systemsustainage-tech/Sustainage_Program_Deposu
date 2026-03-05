#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKDM Manager - Sürdürülebilir Kalkınma Modülü Yöneticisi
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from backend.core.base_manager import BaseTenantManager
try:
    from config.database import DB_PATH
except ImportError:
    from backend.config.database import DB_PATH

try:
    from backend.modules.cbam.cbam_manager import CBAMManager
except ImportError:
    # Fallback if path issues
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    from modules.cbam.cbam_manager import CBAMManager


class SKDMManager(CBAMManager):
    """
    SKDM (Sınırda Karbon Düzenleme Mekanizması) Modülü Yöneticisi.
    Bu sınıf, CBAMManager'dan miras alarak tüm CBAM işlevlerini (AB uyumlu) sağlar.
    Ayrıca eski SKDM tablolarını da destekler (geriye dönük uyumluluk için).
    """

    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None) -> None:
        # CBAMManager init çağrılır (bu sayede cbam_ tabloları oluşur)
        super().__init__(db_path, company_id)
        # SKDM'e özel ek tablolar (varsa)
        self._init_skdm_tables()

    def _init_skdm_tables(self) -> None:
        """Eski SKDM tablolarını oluştur (geriye dönük uyumluluk)"""
        try:
            # Karbon yönetimi tablosu
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS skdm_carbon_management (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_emissions REAL NOT NULL,
                    scope1_emissions REAL DEFAULT 0,
                    scope2_emissions REAL DEFAULT 0,
                    scope3_emissions REAL DEFAULT 0,
                    reduction_target REAL,
                    reduction_achieved REAL DEFAULT 0,
                    carbon_price REAL,
                    offset_purchased REAL DEFAULT 0,
                    renewable_energy_percentage REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Su yönetimi tablosu
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS skdm_water_management (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_water_consumption REAL NOT NULL,
                    water_reuse_percentage REAL DEFAULT 0,
                    water_efficiency_score INTEGER DEFAULT 0,
                    water_risk_level TEXT DEFAULT 'Low',
                    water_conservation_projects INTEGER DEFAULT 0,
                    wastewater_treatment_percentage REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Atık yönetimi tablosu
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS skdm_waste_management (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total_waste_generated REAL NOT NULL,
                    waste_recycled_percentage REAL DEFAULT 0,
                    waste_reduced_percentage REAL DEFAULT 0,
                    hazardous_waste_percentage REAL DEFAULT 0,
                    circular_economy_score INTEGER DEFAULT 0,
                    waste_to_energy_percentage REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Tedarik zinciri tablosu
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS skdm_supply_chain (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    suppliers_assessed INTEGER DEFAULT 0,
                    suppliers_sustainable_percentage REAL DEFAULT 0,
                    supply_chain_emissions REAL DEFAULT 0,
                    supplier_audits INTEGER DEFAULT 0,
                    ethical_sourcing_score INTEGER DEFAULT 0,
                    local_sourcing_percentage REAL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Scope 3 kategorileri tablosu
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS skdm_scope3_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    category_code TEXT NOT NULL,
                    category_name TEXT NOT NULL,
                    emissions REAL NOT NULL,
                    data_quality TEXT DEFAULT 'Low',
                    calculation_method TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Emisyon azaltma projeleri tablosu
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS skdm_emission_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE,
                    expected_reduction REAL NOT NULL,
                    actual_reduction REAL DEFAULT 0,
                    investment_amount REAL NOT NULL,
                    status TEXT DEFAULT 'Planning',
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Paydaş yönetimi tablosu
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS skdm_stakeholder_management (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_name TEXT NOT NULL,
                    stakeholder_type TEXT NOT NULL,
                    engagement_level TEXT DEFAULT 'Low',
                    satisfaction_score INTEGER DEFAULT 0,
                    last_contact_date DATE,
                    next_contact_date DATE,
                    key_concerns TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            logging.info("[OK] SKDM tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] SKDM tablolari olusturulamadi: {e}")


    def get_carbon_summary(self, company_id: int, year: int = None) -> Dict:
        """Karbon yönetimi özeti"""
        if year is None:
            year = datetime.now().year

        try:
            sql = """
                SELECT * FROM skdm_carbon_management 
                WHERE company_id = ? AND year = ?
                ORDER BY updated_at DESC LIMIT 1
            """
            rows = self.execute_query(sql, (company_id, year), company_id=company_id)

            if rows:
                result = rows[0]
                return {
                    'total_emissions': result['total_emissions'],
                    'scope1': result['scope1_emissions'],
                    'scope2': result['scope2_emissions'],
                    'scope3': result['scope3_emissions'],
                    'reduction_target': result['reduction_target'],
                    'reduction_achieved': result['reduction_achieved'],
                    'carbon_price': result['carbon_price'],
                    'offset_purchased': result['offset_purchased'],
                    'renewable_energy': result['renewable_energy_percentage']
                }
            return {}

        except Exception as e:
            logging.error(f"[HATA] Karbon ozeti alinamadi: {e}")
            return {}

    def get_water_summary(self, company_id: int, year: int = None) -> Dict:
        """Su yönetimi özeti"""
        if year is None:
            year = datetime.now().year

        try:
            sql = """
                SELECT * FROM skdm_water_management 
                WHERE company_id = ? AND year = ?
                ORDER BY updated_at DESC LIMIT 1
            """
            rows = self.execute_query(sql, (company_id, year), company_id=company_id)

            if rows:
                result = rows[0]
                return {
                    'total_consumption': result['total_water_consumption'],
                    'reuse_percentage': result['water_reuse_percentage'],
                    'efficiency_score': result['water_efficiency_score'],
                    'risk_level': result['water_risk_level'],
                    'conservation_projects': result['water_conservation_projects'],
                    'treatment_percentage': result['wastewater_treatment_percentage']
                }
            return {}

        except Exception as e:
            logging.error(f"[HATA] Su ozeti alinamadi: {e}")
            return {}

    def get_waste_summary(self, company_id: int, year: int = None) -> Dict:
        """Atık yönetimi özeti"""
        if year is None:
            year = datetime.now().year

        try:
            sql = """
                SELECT * FROM skdm_waste_management 
                WHERE company_id = ? AND year = ?
                ORDER BY updated_at DESC LIMIT 1
            """
            rows = self.execute_query(sql, (company_id, year), company_id=company_id)

            if rows:
                result = rows[0]
                return {
                    'total_waste': result['total_waste_generated'],
                    'recycled_percentage': result['waste_recycled_percentage'],
                    'reduced_percentage': result['waste_reduced_percentage'],
                    'hazardous_percentage': result['hazardous_waste_percentage'],
                    'circular_score': result['circular_economy_score'],
                    'waste_to_energy': result['waste_to_energy_percentage']
                }
            return {}

        except Exception as e:
            logging.error(f"[HATA] Atik ozeti alinamadi: {e}")
            return {}

    def get_supply_chain_summary(self, company_id: int, year: int = None) -> Dict:
        """Tedarik zinciri özeti"""
        if year is None:
            year = datetime.now().year

        try:
            sql = """
                SELECT * FROM skdm_supply_chain 
                WHERE company_id = ? AND year = ?
                ORDER BY updated_at DESC LIMIT 1
            """
            rows = self.execute_query(sql, (company_id, year), company_id=company_id)

            if rows:
                result = rows[0]
                return {
                    'suppliers_assessed': result['suppliers_assessed'],
                    'sustainable_percentage': result['suppliers_sustainable_percentage'],
                    'supply_chain_emissions': result['supply_chain_emissions'],
                    'audits': result['supplier_audits'],
                    'ethical_score': result['ethical_sourcing_score'],
                    'local_sourcing': result['local_sourcing_percentage']
                }
            return {}

        except Exception as e:
            logging.error(f"[HATA] Tedarik zinciri ozeti alinamadi: {e}")
            return {}

    def get_scope3_categories(self, company_id: int, year: int = None) -> List[Dict]:
        """Scope 3 kategorileri"""
        if year is None:
            year = datetime.now().year

        try:
            sql = """
                SELECT * FROM skdm_scope3_categories 
                WHERE company_id = ? AND year = ?
                ORDER BY emissions DESC
            """
            rows = self.execute_query(sql, (company_id, year), company_id=company_id)
            
            categories = []
            for result in rows:
                categories.append({
                    'category_code': result['category_code'],
                    'category_name': result['category_name'],
                    'emissions': result['emissions'],
                    'data_quality': result['data_quality'],
                    'calculation_method': result['calculation_method'],
                    'verification_status': result['verification_status']
                })
            return categories

        except Exception as e:
            logging.error(f"[HATA] Scope 3 kategorileri alinamadi: {e}")
            return []


    def get_emission_projects(self, company_id: int) -> List[Dict]:
        """Emisyon azaltma projeleri"""
        try:
            sql = """
                SELECT * FROM skdm_emission_projects 
                WHERE company_id = ?
                ORDER BY start_date DESC
            """
            rows = self.execute_query(sql, (company_id,), company_id=company_id)

            projects = []
            for result in rows:
                projects.append({
                    'project_name': result['project_name'],
                    'project_type': result['project_type'],
                    'start_date': result['start_date'],
                    'end_date': result['end_date'],
                    'expected_reduction': result['expected_reduction'],
                    'actual_reduction': result['actual_reduction'],
                    'investment_amount': result['investment_amount'],
                    'status': result['status'],
                    'description': result['description']
                })
            return projects

        except Exception as e:
            logging.error(f"[HATA] Emisyon projeleri alinamadi: {e}")
            return []

    def get_stakeholders(self, company_id: int) -> List[Dict]:
        """Paydaş listesi"""
        try:
            sql = """
                SELECT * FROM skdm_stakeholder_management 
                WHERE company_id = ?
                ORDER BY stakeholder_name
            """
            rows = self.execute_query(sql, (company_id,), company_id=company_id)

            stakeholders = []
            for result in rows:
                stakeholders.append({
                    'stakeholder_name': result['stakeholder_name'],
                    'stakeholder_type': result['stakeholder_type'],
                    'engagement_level': result['engagement_level'],
                    'satisfaction_score': result['satisfaction_score'],
                    'last_contact_date': result['last_contact_date'],
                    'next_contact_date': result['next_contact_date'],
                    'key_concerns': result['key_concerns']
                })
            return stakeholders

        except Exception as e:
            logging.error(f"[HATA] Paydaslar alinamadi: {e}")
            return []

    def add_carbon_data(self, company_id: int, year: int, data: Dict) -> bool:
        """Karbon verisi ekle"""
        try:
            sql = """
                INSERT OR REPLACE INTO skdm_carbon_management 
                (company_id, year, total_emissions, scope1_emissions, scope2_emissions, 
                 scope3_emissions, reduction_target, reduction_achieved, carbon_price, 
                 offset_purchased, renewable_energy_percentage, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.execute_update(sql, (company_id, year, data.get('total_emissions', 0),
                  data.get('scope1_emissions', 0), data.get('scope2_emissions', 0),
                  data.get('scope3_emissions', 0), data.get('reduction_target', 0),
                  data.get('reduction_achieved', 0), data.get('carbon_price', 0),
                  data.get('offset_purchased', 0), data.get('renewable_energy_percentage', 0),
                  datetime.now()), company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"[HATA] Karbon verisi eklenemedi: {e}")
            return False

    def add_emission_project(self, company_id: int, project_data: Dict) -> bool:
        """Emisyon azaltma projesi ekle"""
        try:
            sql = """
                INSERT INTO skdm_emission_projects 
                (company_id, project_name, project_type, start_date, end_date,
                 expected_reduction, actual_reduction, investment_amount, status, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.execute_update(sql, (company_id, project_data.get('project_name', ''),
                  project_data.get('project_type', ''), project_data.get('start_date', ''),
                  project_data.get('end_date', ''), project_data.get('expected_reduction', 0),
                  project_data.get('actual_reduction', 0), project_data.get('investment_amount', 0),
                  project_data.get('status', 'Planning'), project_data.get('description', '')), company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"[HATA] Emisyon projesi eklenemedi: {e}")
            return False

    def add_stakeholder(self, company_id: int, stakeholder_data: Dict) -> bool:
        """Paydaş ekle"""
        try:
            sql = """
                INSERT INTO skdm_stakeholder_management 
                (company_id, stakeholder_name, stakeholder_type, engagement_level,
                 satisfaction_score, last_contact_date, next_contact_date, key_concerns)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.execute_update(sql, (company_id,
                  stakeholder_data.get('stakeholder_name', ''),
                  stakeholder_data.get('stakeholder_type', ''),
                  stakeholder_data.get('engagement_level', 'Low'),
                  stakeholder_data.get('satisfaction_score', 0),
                  stakeholder_data.get('last_contact_date'),
                  stakeholder_data.get('next_contact_date'),
                  stakeholder_data.get('key_concerns', '')), company_id=company_id)
            
            logging.info(f"[OK] Paydaş eklendi: {stakeholder_data.get('stakeholder_name')}")
            return True

        except Exception as e:
            logging.error(f"[HATA] Paydaş eklenemedi: {e}")
            return False

    def update_stakeholder(self, stakeholder_id: int, stakeholder_data: Dict, company_id: int) -> bool:
        """Paydaş güncelle"""
        try:
            sql = """
                UPDATE skdm_stakeholder_management 
                SET stakeholder_name = ?, stakeholder_type = ?, engagement_level = ?,
                    satisfaction_score = ?, last_contact_date = ?, next_contact_date = ?,
                    key_concerns = ?, updated_at = ?
                WHERE id = ? AND company_id = ?
            """
            self.execute_update(sql, (
                stakeholder_data.get('stakeholder_name', ''),
                stakeholder_data.get('stakeholder_type', ''),
                stakeholder_data.get('engagement_level', 'Low'),
                stakeholder_data.get('satisfaction_score', 0),
                stakeholder_data.get('last_contact_date'),
                stakeholder_data.get('next_contact_date'),
                stakeholder_data.get('key_concerns', ''),
                datetime.now(),
                stakeholder_id,
                company_id
            ), company_id=company_id)
            
            return True

        except Exception as e:
            logging.error(f"[HATA] Paydaş güncellenemedi: {e}")
            return False

    def delete_stakeholder(self, stakeholder_id: int, company_id: int) -> bool:
        """Paydaş sil"""
        try:
            sql = "DELETE FROM skdm_stakeholder_management WHERE id = ? AND company_id = ?"
            self.execute_update(sql, (stakeholder_id, company_id), company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"[HATA] Paydaş silinemedi: {e}")
            return False
