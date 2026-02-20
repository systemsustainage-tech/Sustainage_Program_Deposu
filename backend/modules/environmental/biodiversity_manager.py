#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Biyoçeşitlilik Yönetimi Modülü
Biyoçeşitlilik koruma, habitat yönetimi ve ekosistem hizmetleri
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


class BiodiversityManager(BaseTenantManager):
    """Biyoçeşitlilik yönetimi ve koruma"""

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
        """Biyoçeşitlilik yönetimi tablolarını oluştur"""
        try:
            # Habitat alanları
            self.execute_update("""
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
            self.execute_update("""
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
            self.execute_update("""
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
            self.execute_update("""
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
            self.execute_update("""
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
            self.execute_update("""
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

            logging.info(f"[OK] {self.lm.tr('biodiversity_module_tables_created', 'Biyoçeşitlilik yönetimi modülü tabloları başarıyla oluşturuldu')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('biodiversity_module_table_error', 'Biyoçeşitlilik yönetimi modülü tablo oluşturma')}: {e}")

    def _migrate_tables(self) -> None:
        """Tablo şemalarını güncelle"""
        # Gelecekteki şema değişiklikleri için placeholder
        pass

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        cid = self._ensure_context(company_id)
        stats = {
            'habitat_count': 0, 'species_count': 0, 'project_count': 0,
            'total_count': 0, 'total_area': 0
        }

        try:
            res_habitat = self.execute_query("SELECT COUNT(*) as count FROM habitat_areas WHERE company_id = ?", (cid,))
            stats['habitat_count'] = res_habitat[0]['count'] if res_habitat else 0

            res_species = self.execute_query("SELECT COUNT(*) as count FROM biodiversity_species WHERE company_id = ?", (cid,))
            stats['species_count'] = res_species[0]['count'] if res_species else 0

            res_projects = self.execute_query("SELECT COUNT(*) as count FROM biodiversity_projects WHERE company_id = ?", (cid,))
            stats['project_count'] = res_projects[0]['count'] if res_projects else 0
            
            res_area = self.execute_query("SELECT SUM(area_size) as total FROM habitat_areas WHERE company_id = ?", (cid,))
            stats['total_area'] = res_area[0]['total'] if res_area and res_area[0]['total'] else 0
            
            stats['total_count'] = stats['habitat_count'] + stats['species_count'] + stats['project_count']

            return stats
        except Exception as e:
            logging.error(f"Biodiversity dashboard stats error: {e}")
            return stats

    def get_recent_records(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Son eklenen kayıtları getir"""
        cid = self._ensure_context(company_id)
        records = []

        try:
            # Habitat, Species ve Projects tablolarından birleştirilmiş veri
            query = """
                SELECT 'Habitat' as type, habitat_name as name, area_size || ' ' || area_unit as area, protection_status as status, created_at 
                FROM habitat_areas WHERE company_id = ?
                UNION ALL
                SELECT 'Tür' as type, species_name as name, '-' as area, conservation_status as status, created_at 
                FROM biodiversity_species WHERE company_id = ?
                UNION ALL
                SELECT 'Proje' as type, project_name as name, '-' as area, status as status, created_at 
                FROM biodiversity_projects WHERE company_id = ?
                ORDER BY created_at DESC LIMIT ?
            """
            rows = self.execute_query(query, (cid, cid, cid, limit))
            
            for row in rows:
                records.append({
                    'category': row['type'],
                    'description': row['name'],
                    'area': row['area'],
                    'status': row['status'],
                    'date': row['created_at']
                })
            
            return records
        except Exception as e:
            logging.error(f"Biodiversity recent records error: {e}")
            return []

    def add_habitat_area(self, company_id: int, habitat_name: str, habitat_type: str,
                        area_size: float, area_unit: str, location: str = None,
                        coordinates: str = None, biodiversity_value: str = None,
                        protection_status: str = None, management_plan: str = None) -> bool:
        """Habitat alanı ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT INTO habitat_areas 
                (company_id, habitat_name, habitat_type, area_size, area_unit,
                 location, coordinates, biodiversity_value, protection_status, management_plan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, habitat_name, habitat_type, area_size, area_unit,
                  location, coordinates, biodiversity_value, protection_status, management_plan))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('habitat_area_add_error', 'Habitat alanı ekleme hatası')}: {e}")
            return False

    def add_biodiversity_species(self, company_id: int, species_name: str,
                               species_type: str, conservation_status: str = None,
                               habitat_requirements: str = None, population_count: int = None,
                               last_survey_date: str = None, threat_factors: str = None,
                               protection_measures: str = None) -> bool:
        """Biyoçeşitlilik türü ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT INTO biodiversity_species 
                (company_id, species_name, species_type, conservation_status,
                 habitat_requirements, population_count, last_survey_date,
                 threat_factors, protection_measures)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, species_name, species_type, conservation_status,
                  habitat_requirements, population_count, last_survey_date,
                  threat_factors, protection_measures))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('biodiversity_species_add_error', 'Biyoçeşitlilik türü ekleme hatası')}: {e}")
            return False

    def add_biodiversity_project(self, company_id: int, project_name: str,
                               project_type: str, start_date: str, end_date: str,
                               investment_cost: float, project_area: float = None,
                               area_unit: str = None, target_species: str = None,
                               expected_benefits: str = None) -> bool:
        """Biyoçeşitlilik projesi ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT INTO biodiversity_projects 
                (company_id, project_name, project_type, start_date, end_date,
                 investment_cost, project_area, area_unit, target_species, expected_benefits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, project_name, project_type, start_date, end_date,
                  investment_cost, project_area, area_unit, target_species, expected_benefits))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('biodiversity_project_add_error', 'Biyoçeşitlilik projesi ekleme hatası')}: {e}")
            return False

    def add_ecosystem_service(self, company_id: int, year: int, service_type: str,
                            service_value: float, value_unit: str, measurement_method: str = None,
                            beneficiary: str = None, location: str = None) -> bool:
        """Ekosistem hizmeti ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT INTO ecosystem_services 
                (company_id, year, service_type, service_value, value_unit,
                 measurement_method, beneficiary, location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, year, service_type, service_value, value_unit,
                  measurement_method, beneficiary, location))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('ecosystem_service_add_error', 'Ekosistem hizmeti ekleme hatası')}: {e}")
            return False

    def add_biodiversity_impact_assessment(self, company_id: int, assessment_date: str,
                                         impact_type: str, impact_level: str,
                                         affected_species: str = None, mitigation_measures: str = None,
                                         monitoring_plan: str = None, compliance_status: str = None) -> bool:
        """Biyoçeşitlilik etki değerlendirmesi ekle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT INTO biodiversity_impact_assessment 
                (company_id, assessment_date, impact_type, impact_level,
                 affected_species, mitigation_measures, monitoring_plan, compliance_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, assessment_date, impact_type, impact_level,
                  affected_species, mitigation_measures, monitoring_plan, compliance_status))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('biodiversity_impact_assessment_add_error', 'Biyoçeşitlilik etki değerlendirmesi ekleme hatası')}: {e}")
            return False

    def set_biodiversity_target(self, company_id: int, target_year: int, target_type: str,
                              baseline_value: float, baseline_unit: str, target_value: float,
                              target_unit: str, target_description: str = None) -> bool:
        """Biyoçeşitlilik hedefi belirle"""
        cid = self._ensure_context(company_id)

        try:
            self.execute_update("""
                INSERT OR REPLACE INTO biodiversity_targets 
                (company_id, target_year, target_type, baseline_value, baseline_unit,
                 target_value, target_unit, target_description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, target_year, target_type, baseline_value, baseline_unit,
                  target_value, target_unit, target_description))
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('biodiversity_target_set_error', 'Biyoçeşitlilik hedefi belirleme hatası')}: {e}")
            return False

    def get_biodiversity_summary(self, company_id: int) -> Dict:
        """Biyoçeşitlilik özeti getir"""
        cid = self._ensure_context(company_id)

        try:
            # Habitat alanları
            rows_habitat = self.execute_query("""
                SELECT habitat_type, SUM(area_size) as total_area, area_unit, COUNT(*) as count
                FROM habitat_areas 
                WHERE company_id = ?
                GROUP BY habitat_type, area_unit
            """, (cid,))

            habitat_summary = {}
            total_area = 0
            for row in rows_habitat:
                habitat_type = row['habitat_type']
                area = row['total_area']
                unit = row['area_unit']
                count = row['count']
                
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
            rows_species = self.execute_query("""
                SELECT species_type, conservation_status, COUNT(*) as count
                FROM biodiversity_species 
                WHERE company_id = ?
                GROUP BY species_type, conservation_status
            """, (cid,))

            species_summary = {}
            total_species = 0
            for row in rows_species:
                species_type = row['species_type']
                conservation_status = row['conservation_status']
                count = row['count']
                
                if species_type not in species_summary:
                    species_summary[species_type] = {}
                species_summary[species_type][conservation_status] = count
                total_species += count

            # Aktif projeler
            res_projects = self.execute_query("""
                SELECT COUNT(*) as count, SUM(investment_cost) as total_cost, SUM(project_area) as total_area
                FROM biodiversity_projects 
                WHERE company_id = ? AND status = 'active'
            """, (cid,))

            project_result = res_projects[0] if res_projects else {}
            active_projects = project_result.get('count', 0) or 0
            total_investment = project_result.get('total_cost', 0) or 0
            total_project_area = project_result.get('total_area', 0) or 0

            return {
                'habitat_summary': habitat_summary,
                'species_summary': species_summary,
                'total_habitat_area': total_area,
                'total_species_count': total_species,
                'active_projects': active_projects,
                'total_investment': total_investment,
                'total_project_area': total_project_area,
                'company_id': cid
            }

        except Exception as e:
            logging.error(f"Biyoçeşitlilik özeti getirme hatası: {e}")
            return {}

    def get_biodiversity_targets(self, company_id: int) -> List[Dict]:
        """Biyoçeşitlilik hedeflerini getir"""
        cid = self._ensure_context(company_id)

        try:
            rows = self.execute_query("""
                SELECT target_year, target_type, baseline_value, baseline_unit,
                       target_value, target_unit, target_description, status
                FROM biodiversity_targets 
                WHERE company_id = ? AND status = 'active'
                ORDER BY target_year
            """, (cid,))

            targets = []
            for row in rows:
                targets.append({
                    'target_year': row['target_year'],
                    'target_type': row['target_type'],
                    'baseline_value': row['baseline_value'],
                    'baseline_unit': row['baseline_unit'],
                    'target_value': row['target_value'],
                    'target_unit': row['target_unit'],
                    'target_description': row['target_description'],
                    'status': row['status']
                })

            return targets

        except Exception as e:
            logging.error(f"Biyoçeşitlilik hedefleri getirme hatası: {e}")
            return []
