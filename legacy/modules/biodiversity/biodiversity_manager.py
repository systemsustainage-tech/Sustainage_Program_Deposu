#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Biyoçeşitlilik Yönetimi Modülü
Biyoçeşitlilik koruma, habitat yönetimi ve ekosistem hizmetleri
"""

import logging
import os
import sqlite3
from typing import Dict, List

from utils.language_manager import LanguageManager
from config.database import DB_PATH


class BiodiversityManager:
    """Biyoçeşitlilik yönetimi ve koruma"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.lm = LanguageManager()
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Biyoçeşitlilik yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Habitat alanları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habitat_areas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    habitat_name TEXT NOT NULL,
                    habitat_type TEXT NOT NULL,
                    area_size REAL NOT NULL,
                    area_unit TEXT NOT NULL,
                    location TEXT,
                    coordinates TEXT,
                    biodiversity_value TEXT,
                    protection_status TEXT,
                    management_plan TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Biyoçeşitlilik türleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS biodiversity_species (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    species_name TEXT NOT NULL,
                    species_type TEXT NOT NULL,
                    conservation_status TEXT,
                    habitat_requirements TEXT,
                    population_count INTEGER,
                    last_survey_date TEXT,
                    threat_factors TEXT,
                    protection_measures TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Biyoçeşitlilik projeleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS biodiversity_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    investment_cost REAL,
                    project_area REAL,
                    area_unit TEXT,
                    target_species TEXT,
                    expected_benefits TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Ekosistem hizmetleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ecosystem_services (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    service_type TEXT NOT NULL,
                    service_value REAL,
                    value_unit TEXT,
                    measurement_method TEXT,
                    beneficiary TEXT,
                    location TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Biyoçeşitlilik etki değerlendirmesi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS biodiversity_impact_assessment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    impact_type TEXT NOT NULL,
                    impact_level TEXT NOT NULL,
                    affected_species TEXT,
                    mitigation_measures TEXT,
                    monitoring_plan TEXT,
                    compliance_status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Biyoçeşitlilik hedefleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS biodiversity_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_value REAL,
                    baseline_unit TEXT,
                    target_value REAL,
                    target_unit TEXT,
                    target_description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info(f"[OK] {self.lm.tr('biodiversity_module_tables_created', 'Biyoçeşitlilik yönetimi modülü tabloları başarıyla oluşturuldu')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('biodiversity_module_table_error', 'Biyoçeşitlilik yönetimi modülü tablo oluşturma')}: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_habitat_area(self, company_id: int, habitat_name: str, habitat_type: str,
                        area_size: float, area_unit: str, location: str = None,
                        coordinates: str = None, biodiversity_value: str = None,
                        protection_status: str = None, management_plan: str = None) -> bool:
        """Habitat alanı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO habitat_areas 
                (company_id, habitat_name, habitat_type, area_size, area_unit,
                 location, coordinates, biodiversity_value, protection_status, management_plan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, habitat_name, habitat_type, area_size, area_unit,
                  location, coordinates, biodiversity_value, protection_status, management_plan))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('habitat_area_add_error', 'Habitat alanı ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_biodiversity_species(self, company_id: int, species_name: str,
                               species_type: str, conservation_status: str = None,
                               habitat_requirements: str = None, population_count: int = None,
                               last_survey_date: str = None, threat_factors: str = None,
                               protection_measures: str = None) -> bool:
        """Biyoçeşitlilik türü ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO biodiversity_species 
                (company_id, species_name, species_type, conservation_status,
                 habitat_requirements, population_count, last_survey_date,
                 threat_factors, protection_measures)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, species_name, species_type, conservation_status,
                  habitat_requirements, population_count, last_survey_date,
                  threat_factors, protection_measures))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('biodiversity_species_add_error', 'Biyoçeşitlilik türü ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_biodiversity_project(self, company_id: int, project_name: str,
                               project_type: str, start_date: str, end_date: str,
                               investment_cost: float, project_area: float = None,
                               area_unit: str = None, target_species: str = None,
                               expected_benefits: str = None) -> bool:
        """Biyoçeşitlilik projesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO biodiversity_projects 
                (company_id, project_name, project_type, start_date, end_date,
                 investment_cost, project_area, area_unit, target_species, expected_benefits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, project_name, project_type, start_date, end_date,
                  investment_cost, project_area, area_unit, target_species, expected_benefits))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('biodiversity_project_add_error', 'Biyoçeşitlilik projesi ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_ecosystem_service(self, company_id: int, year: int, service_type: str,
                            service_value: float, value_unit: str, measurement_method: str = None,
                            beneficiary: str = None, location: str = None) -> bool:
        """Ekosistem hizmeti ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO ecosystem_services 
                (company_id, year, service_type, service_value, value_unit,
                 measurement_method, beneficiary, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, service_type, service_value, value_unit,
                  measurement_method, beneficiary, location))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('ecosystem_service_add_error', 'Ekosistem hizmeti ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_biodiversity_impact_assessment(self, company_id: int, assessment_date: str,
                                         impact_type: str, impact_level: str,
                                         affected_species: str = None, mitigation_measures: str = None,
                                         monitoring_plan: str = None, compliance_status: str = None) -> bool:
        """Biyoçeşitlilik etki değerlendirmesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO biodiversity_impact_assessment 
                (company_id, assessment_date, impact_type, impact_level,
                 affected_species, mitigation_measures, monitoring_plan, compliance_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, assessment_date, impact_type, impact_level,
                  affected_species, mitigation_measures, monitoring_plan, compliance_status))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('biodiversity_impact_assessment_add_error', 'Biyoçeşitlilik etki değerlendirmesi ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def set_biodiversity_target(self, company_id: int, target_year: int, target_type: str,
                              baseline_value: float, baseline_unit: str, target_value: float,
                              target_unit: str, target_description: str = None) -> bool:
        """Biyoçeşitlilik hedefi belirle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO biodiversity_targets 
                (company_id, target_year, target_type, baseline_value, baseline_unit,
                 target_value, target_unit, target_description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, target_year, target_type, baseline_value, baseline_unit,
                  target_value, target_unit, target_description))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('biodiversity_target_set_error', 'Biyoçeşitlilik hedefi belirleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_biodiversity_summary(self, company_id: int) -> Dict:
        """Biyoçeşitlilik özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Habitat alanları
            cursor.execute("""
                SELECT habitat_type, SUM(area_size), area_unit, COUNT(*)
                FROM habitat_areas 
                WHERE company_id = ?
                GROUP BY habitat_type, area_unit
            """, (company_id,))

            habitat_summary = {}
            total_area = 0
            for row in cursor.fetchall():
                habitat_type, area, unit, count = row
                habitat_summary[habitat_type] = {
                    'area': area,
                    'unit': unit,
                    'count': count
                }
                # Alanı m² cinsine çevir
                if unit == 'm²':
                    total_area += area
                elif unit == 'ha':
                    total_area += area * 10000
                elif unit == 'km²':
                    total_area += area * 1000000

            # Biyoçeşitlilik türleri
            cursor.execute("""
                SELECT species_type, conservation_status, COUNT(*)
                FROM biodiversity_species 
                WHERE company_id = ?
                GROUP BY species_type, conservation_status
            """, (company_id,))

            species_summary = {}
            total_species = 0
            for row in cursor.fetchall():
                species_type, conservation_status, count = row
                if species_type not in species_summary:
                    species_summary[species_type] = {}
                species_summary[species_type][conservation_status] = count
                total_species += count

            # Aktif projeler
            cursor.execute("""
                SELECT COUNT(*), SUM(investment_cost), SUM(project_area)
                FROM biodiversity_projects 
                WHERE company_id = ? AND status = 'active'
            """, (company_id,))

            project_result = cursor.fetchone()
            active_projects = project_result[0] or 0
            total_investment = project_result[1] or 0
            total_project_area = project_result[2] or 0

            return {
                'habitat_summary': habitat_summary,
                'species_summary': species_summary,
                'total_habitat_area': total_area,
                'total_species_count': total_species,
                'active_projects': active_projects,
                'total_investment': total_investment,
                'total_project_area': total_project_area,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"Biyoçeşitlilik özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()

    def get_biodiversity_targets(self, company_id: int) -> List[Dict]:
        """Biyoçeşitlilik hedeflerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT target_year, target_type, baseline_value, baseline_unit,
                       target_value, target_unit, target_description, status
                FROM biodiversity_targets 
                WHERE company_id = ? AND status = 'active'
                ORDER BY target_year
            """, (company_id,))

            targets = []
            for row in cursor.fetchall():
                targets.append({
                    'target_year': row[0],
                    'target_type': row[1],
                    'baseline_value': row[2],
                    'baseline_unit': row[3],
                    'target_value': row[4],
                    'target_unit': row[5],
                    'target_description': row[6],
                    'status': row[7]
                })

            return targets

        except Exception as e:
            logging.error(f"Biyoçeşitlilik hedefleri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_ecosystem_services(self, company_id: int, year: int) -> List[Dict]:
        """Ekosistem hizmetlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT service_type, SUM(service_value), value_unit, measurement_method,
                       beneficiary, location
                FROM ecosystem_services 
                WHERE company_id = ? AND year = ?
                GROUP BY service_type, value_unit, measurement_method, beneficiary, location
            """, (company_id, year))

            services = []
            for row in cursor.fetchall():
                services.append({
                    'service_type': row[0],
                    'total_value': row[1],
                    'value_unit': row[2],
                    'measurement_method': row[3],
                    'beneficiary': row[4],
                    'location': row[5]
                })

            return services

        except Exception as e:
            logging.error(f"{self.lm.tr('ecosystem_services_get_error', 'Ekosistem hizmetleri getirme hatası')}: {e}")
            return []
        finally:
            conn.close()

    def calculate_biodiversity_kpis(self, company_id: int) -> Dict:
        """Biyoçeşitlilik KPI'larını hesapla"""
        summary = self.get_biodiversity_summary(company_id)

        if not summary:
            return {}

        # Biyoçeşitlilik yoğunluğu (tür/m²)
        biodiversity_density = (summary['total_species_count'] / summary['total_habitat_area']) if summary['total_habitat_area'] > 0 else 0

        # Habitat koruma oranı
        protected_area = 0
        for habitat_data in summary['habitat_summary'].values():
            # Korumalı alan varsayımı - gerçekte protection_status'a göre hesaplanmalı
            protected_area += habitat_data['area']

        protection_ratio = (protected_area / summary['total_habitat_area'] * 100) if summary['total_habitat_area'] > 0 else 0

        return {
            'total_habitat_area': summary['total_habitat_area'],
            'total_species_count': summary['total_species_count'],
            'biodiversity_density': biodiversity_density,
            'protection_ratio': protection_ratio,
            'active_projects': summary['active_projects'],
            'investment_per_hectare': (summary['total_investment'] / (summary['total_habitat_area'] / 10000)) if summary['total_habitat_area'] > 0 else 0,
            'company_id': company_id
        }
