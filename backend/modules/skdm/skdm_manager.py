#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKDM Manager - Sürdürülebilir Kalkınma Modülü Yöneticisi
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List
from config.database import DB_PATH


class SKDMManager:
    """SKDM Modülü Yönetim Sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self) -> None:
        """SKDM tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Karbon yönetimi tablosu
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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

            conn.commit()
            logging.info("[OK] SKDM tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] SKDM tablolari olusturulamadi: {e}")
        finally:
            conn.close()

    def get_carbon_summary(self, company_id: int, year: int = None) -> Dict:
        """Karbon yönetimi özeti"""
        if year is None:
            year = datetime.now().year

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM skdm_carbon_management 
                WHERE company_id = ? AND year = ?
                ORDER BY updated_at DESC LIMIT 1
            """, (company_id, year))

            result = cursor.fetchone()
            if result:
                return {
                    'total_emissions': result[3],
                    'scope1': result[4],
                    'scope2': result[5],
                    'scope3': result[6],
                    'reduction_target': result[7],
                    'reduction_achieved': result[8],
                    'carbon_price': result[9],
                    'offset_purchased': result[10],
                    'renewable_energy': result[11]
                }
            return {}

        except Exception as e:
            logging.error(f"[HATA] Karbon ozeti alinamadi: {e}")
            return {}
        finally:
            conn.close()

    def get_water_summary(self, company_id: int, year: int = None) -> Dict:
        """Su yönetimi özeti"""
        if year is None:
            year = datetime.now().year

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM skdm_water_management 
                WHERE company_id = ? AND year = ?
                ORDER BY updated_at DESC LIMIT 1
            """, (company_id, year))

            result = cursor.fetchone()
            if result:
                return {
                    'total_consumption': result[3],
                    'reuse_percentage': result[4],
                    'efficiency_score': result[5],
                    'risk_level': result[6],
                    'conservation_projects': result[7],
                    'treatment_percentage': result[8]
                }
            return {}

        except Exception as e:
            logging.error(f"[HATA] Su ozeti alinamadi: {e}")
            return {}
        finally:
            conn.close()

    def get_waste_summary(self, company_id: int, year: int = None) -> Dict:
        """Atık yönetimi özeti"""
        if year is None:
            year = datetime.now().year

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM skdm_waste_management 
                WHERE company_id = ? AND year = ?
                ORDER BY updated_at DESC LIMIT 1
            """, (company_id, year))

            result = cursor.fetchone()
            if result:
                return {
                    'total_waste': result[3],
                    'recycled_percentage': result[4],
                    'reduced_percentage': result[5],
                    'hazardous_percentage': result[6],
                    'circular_score': result[7],
                    'waste_to_energy': result[8]
                }
            return {}

        except Exception as e:
            logging.error(f"[HATA] Atik ozeti alinamadi: {e}")
            return {}
        finally:
            conn.close()

    def get_supply_chain_summary(self, company_id: int, year: int = None) -> Dict:
        """Tedarik zinciri özeti"""
        if year is None:
            year = datetime.now().year

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM skdm_supply_chain 
                WHERE company_id = ? AND year = ?
                ORDER BY updated_at DESC LIMIT 1
            """, (company_id, year))

            result = cursor.fetchone()
            if result:
                return {
                    'suppliers_assessed': result[3],
                    'sustainable_percentage': result[4],
                    'supply_chain_emissions': result[5],
                    'audits': result[6],
                    'ethical_score': result[7],
                    'local_sourcing': result[8]
                }
            return {}

        except Exception as e:
            logging.error(f"[HATA] Tedarik zinciri ozeti alinamadi: {e}")
            return {}
        finally:
            conn.close()

    def get_scope3_categories(self, company_id: int, year: int = None) -> List[Dict]:
        """Scope 3 kategorileri"""
        if year is None:
            year = datetime.now().year

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM skdm_scope3_categories 
                WHERE company_id = ? AND year = ?
                ORDER BY emissions DESC
            """, (company_id, year))

            results = cursor.fetchall()
            categories = []
            for result in results:
                categories.append({
                    'category_code': result[3],
                    'category_name': result[4],
                    'emissions': result[5],
                    'data_quality': result[6],
                    'calculation_method': result[7],
                    'verification_status': result[8]
                })
            return categories

        except Exception as e:
            logging.error(f"[HATA] Scope 3 kategorileri alinamadi: {e}")
            return []
        finally:
            conn.close()

    def get_emission_projects(self, company_id: int) -> List[Dict]:
        """Emisyon azaltma projeleri"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM skdm_emission_projects 
                WHERE company_id = ?
                ORDER BY start_date DESC
            """, (company_id,))

            results = cursor.fetchall()
            projects = []
            for result in results:
                projects.append({
                    'project_name': result[2],
                    'project_type': result[3],
                    'start_date': result[4],
                    'end_date': result[5],
                    'expected_reduction': result[6],
                    'actual_reduction': result[7],
                    'investment_amount': result[8],
                    'status': result[9],
                    'description': result[10]
                })
            return projects

        except Exception as e:
            logging.error(f"[HATA] Emisyon projeleri alinamadi: {e}")
            return []
        finally:
            conn.close()

    def get_stakeholders(self, company_id: int) -> List[Dict]:
        """Paydaş listesi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM skdm_stakeholder_management 
                WHERE company_id = ?
                ORDER BY stakeholder_name
            """, (company_id,))

            results = cursor.fetchall()
            stakeholders = []
            for result in results:
                stakeholders.append({
                    'stakeholder_name': result[2],
                    'stakeholder_type': result[3],
                    'engagement_level': result[4],
                    'satisfaction_score': result[5],
                    'last_contact_date': result[6],
                    'next_contact_date': result[7],
                    'key_concerns': result[8]
                })
            return stakeholders

        except Exception as e:
            logging.error(f"[HATA] Paydaslar alinamadi: {e}")
            return []
        finally:
            conn.close()

    def add_carbon_data(self, company_id: int, year: int, data: Dict) -> bool:
        """Karbon verisi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO skdm_carbon_management 
                (company_id, year, total_emissions, scope1_emissions, scope2_emissions, 
                 scope3_emissions, reduction_target, reduction_achieved, carbon_price, 
                 offset_purchased, renewable_energy_percentage, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, data.get('total_emissions', 0),
                  data.get('scope1_emissions', 0), data.get('scope2_emissions', 0),
                  data.get('scope3_emissions', 0), data.get('reduction_target', 0),
                  data.get('reduction_achieved', 0), data.get('carbon_price', 0),
                  data.get('offset_purchased', 0), data.get('renewable_energy_percentage', 0),
                  datetime.now()))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"[HATA] Karbon verisi eklenemedi: {e}")
            return False
        finally:
            conn.close()

    def add_emission_project(self, company_id: int, project_data: Dict) -> bool:
        """Emisyon azaltma projesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO skdm_emission_projects 
                (company_id, project_name, project_type, start_date, end_date,
                 expected_reduction, actual_reduction, investment_amount, status, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, project_data.get('project_name', ''),
                  project_data.get('project_type', ''), project_data.get('start_date', ''),
                  project_data.get('end_date', ''), project_data.get('expected_reduction', 0),
                  project_data.get('actual_reduction', 0), project_data.get('investment_amount', 0),
                  project_data.get('status', 'Planning'), project_data.get('description', '')))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"[HATA] Emisyon projesi eklenemedi: {e}")
            return False
        finally:
            conn.close()

    def add_stakeholder(self, company_id: int, stakeholder_data: Dict) -> bool:
        """Paydaş ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO skdm_stakeholder_management 
                (company_id, stakeholder_name, stakeholder_type, engagement_level,
                 satisfaction_score, last_contact_date, next_contact_date, key_concerns)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id,
                  stakeholder_data.get('stakeholder_name', ''),
                  stakeholder_data.get('stakeholder_type', ''),
                  stakeholder_data.get('engagement_level', 'Low'),
                  stakeholder_data.get('satisfaction_score', 0),
                  stakeholder_data.get('last_contact_date'),
                  stakeholder_data.get('next_contact_date'),
                  stakeholder_data.get('key_concerns', '')))

            conn.commit()
            logging.info(f"[OK] Paydaş eklendi: {stakeholder_data.get('stakeholder_name')}")
            return True

        except Exception as e:
            logging.error(f"[HATA] Paydaş eklenemedi: {e}")
            return False
        finally:
            conn.close()

    def update_stakeholder(self, stakeholder_id: int, stakeholder_data: Dict) -> bool:
        """Paydaş güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE skdm_stakeholder_management 
                SET stakeholder_name = ?,
                    stakeholder_type = ?,
                    engagement_level = ?,
                    satisfaction_score = ?,
                    last_contact_date = ?,
                    next_contact_date = ?,
                    key_concerns = ?,
                    updated_at = ?
                WHERE id = ?
            """, (stakeholder_data.get('stakeholder_name', ''),
                  stakeholder_data.get('stakeholder_type', ''),
                  stakeholder_data.get('engagement_level', 'Low'),
                  stakeholder_data.get('satisfaction_score', 0),
                  stakeholder_data.get('last_contact_date'),
                  stakeholder_data.get('next_contact_date'),
                  stakeholder_data.get('key_concerns', ''),
                  datetime.now(),
                  stakeholder_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"[HATA] Paydaş güncellenemedi: {e}")
            return False
        finally:
            conn.close()

    def delete_stakeholder(self, stakeholder_id: int) -> bool:
        """Paydaş sil"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM skdm_stakeholder_management WHERE id = ?", (stakeholder_id,))
            conn.commit()
            return True

        except Exception as e:
            logging.error(f"[HATA] Paydaş silinemedi: {e}")
            return False
        finally:
            conn.close()
