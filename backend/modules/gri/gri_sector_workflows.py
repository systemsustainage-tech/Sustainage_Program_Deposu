#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Sector-Specific Standards Workflows - Sprint 5
GRI 11 (Oil & Gas), 12 (Coal), 13 (Agriculture), 14 (Mining) için özel iş akışları
"""

import logging
import os
import sqlite3
from typing import Dict, List
from utils.language_manager import LanguageManager
from config.database import DB_PATH


class GRISectorWorkflows:
    """GRI sektör standartları iş akışları sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.lm = LanguageManager()

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def get_sector_standards(self) -> Dict[str, Dict]:
        """Sektör standartları ve özel gereksinimlerini getir"""
        return {
            "GRI 11": {
                "name": self.lm.tr('gri_11_name', "Oil and Gas Sector"),
                "description": self.lm.tr('gri_11_desc', "Petrol ve gaz sektörü için özel standartlar"),
                "key_topics": [
                    self.lm.tr('topic_eia', "Environmental Impact Assessment"),
                    self.lm.tr('topic_spill', "Spill Prevention and Response"),
                    self.lm.tr('topic_community', "Community Engagement"),
                    self.lm.tr('topic_health_safety', "Health and Safety"),
                    self.lm.tr('topic_climate', "Climate Change Adaptation"),
                    self.lm.tr('topic_water', "Water Management"),
                    self.lm.tr('topic_biodiversity', "Biodiversity Impact")
                ],
                "mandatory_indicators": [
                    "GRI 11-1", "GRI 11-2", "GRI 11-3", "GRI 11-4", "GRI 11-5",
                    "GRI 11-6", "GRI 11-7", "GRI 11-8", "GRI 11-9", "GRI 11-10"
                ],
                "special_requirements": [
                    self.lm.tr('req_eia_completion', "Environmental Impact Assessment completion"),
                    self.lm.tr('req_spill_plan', "Spill response plan documentation"),
                    self.lm.tr('req_community_records', "Community consultation records"),
                    self.lm.tr('req_safety_reporting', "Safety incident reporting"),
                    self.lm.tr('req_climate_risk', "Climate risk assessment")
                ]
            },
            "GRI 12": {
                "name": self.lm.tr('gri_12_name', "Coal Sector"),
                "description": self.lm.tr('gri_12_desc', "Kömür sektörü için özel standartlar"),
                "key_topics": [
                    self.lm.tr('topic_mine_safety', "Mine Safety"),
                    self.lm.tr('topic_env_rehab', "Environmental Rehabilitation"),
                    self.lm.tr('topic_community_resettlement', "Community Resettlement"),
                    self.lm.tr('topic_air_quality', "Air Quality Management"),
                    self.lm.tr('topic_water_contam', "Water Contamination Prevention"),
                    self.lm.tr('topic_worker_health', "Worker Health Monitoring"),
                    self.lm.tr('topic_land_use', "Land Use Impact")
                ],
                "mandatory_indicators": [
                    "GRI 12-1", "GRI 12-2", "GRI 12-3", "GRI 12-4", "GRI 12-5",
                    "GRI 12-6", "GRI 12-7", "GRI 12-8", "GRI 12-9", "GRI 12-10"
                ],
                "special_requirements": [
                    self.lm.tr('req_mine_safety_cert', "Mine safety certification"),
                    self.lm.tr('req_env_rehab_plan', "Environmental rehabilitation plan"),
                    self.lm.tr('req_community_consult', "Community consultation documentation"),
                    self.lm.tr('req_air_quality_data', "Air quality monitoring data"),
                    self.lm.tr('req_worker_health_records', "Worker health assessment records")
                ]
            },
            "GRI 13": {
                "name": self.lm.tr('gri_13_name', "Agriculture, Aquaculture and Fishing Sectors"),
                "description": self.lm.tr('gri_13_desc', "Tarım, su ürünleri ve balıkçılık sektörleri için özel standartlar"),
                "key_topics": [
                    self.lm.tr('topic_sust_agri', "Sustainable Agriculture Practices"),
                    self.lm.tr('topic_water_usage', "Water Usage and Quality"),
                    self.lm.tr('topic_soil_health', "Soil Health Management"),
                    self.lm.tr('topic_animal_welfare', "Animal Welfare"),
                    self.lm.tr('topic_food_safety', "Food Safety"),
                    self.lm.tr('topic_biodiversity_cons', "Biodiversity Conservation"),
                    self.lm.tr('topic_labor_rights_agri', "Labor Rights in Agriculture")
                ],
                "mandatory_indicators": [
                    "GRI 13-1", "GRI 13-2", "GRI 13-3", "GRI 13-4", "GRI 13-5",
                    "GRI 13-6", "GRI 13-7", "GRI 13-8", "GRI 13-9", "GRI 13-10"
                ],
                "special_requirements": [
                    self.lm.tr('req_sust_farming_cert', "Sustainable farming certification"),
                    self.lm.tr('req_water_monitoring', "Water usage monitoring"),
                    self.lm.tr('req_soil_assessment', "Soil quality assessment"),
                    self.lm.tr('req_animal_welfare', "Animal welfare compliance"),
                    self.lm.tr('req_food_safety', "Food safety certification")
                ]
            },
            "GRI 14": {
                "name": self.lm.tr('gri_14_name', "Mining Sector"),
                "description": self.lm.tr('gri_14_desc', "Madencilik sektörü için özel standartlar"),
                "key_topics": [
                    self.lm.tr('topic_mine_lifecycle', "Mine Lifecycle Management"),
                    self.lm.tr('topic_env_impact', "Environmental Impact Assessment"),
                    self.lm.tr('topic_community_rel', "Community Relations"),
                    self.lm.tr('topic_health_safety_mining', "Health and Safety"),
                    self.lm.tr('topic_water_tailings', "Water and Tailings Management"),
                    self.lm.tr('topic_biodiversity_prot', "Biodiversity Protection"),
                    self.lm.tr('topic_artisanal_mining', "Artisanal and Small-scale Mining")
                ],
                "mandatory_indicators": [
                    "GRI 14-1", "GRI 14-2", "GRI 14-3", "GRI 14-4", "GRI 14-5",
                    "GRI 14-6", "GRI 14-7", "GRI 14-8", "GRI 14-9", "GRI 14-10"
                ],
                "special_requirements": [
                    self.lm.tr('req_mine_lifecycle', "Mine lifecycle documentation"),
                    self.lm.tr('req_env_impact', "Environmental impact assessment"),
                    self.lm.tr('req_community_plan', "Community engagement plan"),
                    self.lm.tr('req_safety_system', "Safety management system"),
                    self.lm.tr('req_water_plan', "Water management plan")
                ]
            }
        }

    def get_sector_workflow_steps(self, sector_code: str) -> List[Dict]:
        """Sektör için iş akışı adımlarını getir"""
        workflows = {
            "GRI 11": [
                {
                    "step": 1,
                    "title": self.lm.tr('step_sector_analysis', "Sektör Analizi"),
                    "description": self.lm.tr('desc_oil_gas_impact', "Petrol ve gaz operasyonlarının çevresel etkilerini analiz et"),
                    "duration": self.lm.tr('duration_2_4_weeks', "2-4 hafta"),
                    "required_docs": [self.lm.tr('doc_eia', "Environmental Impact Assessment"), self.lm.tr('doc_ops_data', "Operational Data")],
                    "stakeholders": [self.lm.tr('stakeholder_env_team', "Environmental Team"), self.lm.tr('stakeholder_ops_team', "Operations Team"), self.lm.tr('stakeholder_legal', "Legal Team")]
                },
                {
                    "step": 2,
                    "title": self.lm.tr('step_risk_assessment', "Risk Değerlendirmesi"),
                    "description": self.lm.tr('desc_spill_risk', "Spill riski ve diğer çevresel riskleri değerlendir"),
                    "duration": self.lm.tr('duration_1_2_weeks', "1-2 hafta"),
                    "required_docs": [self.lm.tr('doc_risk_report', "Risk Assessment Report"), self.lm.tr('doc_safety_proc', "Safety Procedures")],
                    "stakeholders": [self.lm.tr('stakeholder_risk_mgmt', "Risk Management"), self.lm.tr('stakeholder_safety_team', "Safety Team"), self.lm.tr('stakeholder_insurance', "Insurance")]
                },
                {
                    "step": 3,
                    "title": self.lm.tr('step_community_engagement', "Topluluk Etkileşimi"),
                    "description": self.lm.tr('desc_community_plan', "Yerel topluluklarla etkileşim planını hazırla"),
                    "duration": self.lm.tr('duration_3_6_weeks', "3-6 hafta"),
                    "required_docs": [self.lm.tr('doc_community_records', "Community Consultation Records"), self.lm.tr('doc_engagement_plan', "Engagement Plan")],
                    "stakeholders": [self.lm.tr('stakeholder_community_rel', "Community Relations"), self.lm.tr('stakeholder_local_gov', "Local Government"), self.lm.tr('stakeholder_ngos', "NGOs")]
                }
            ],
            "GRI 12": [
                {
                    "step": 1,
                    "title": self.lm.tr('step_mine_safety_assessment', "Maden Güvenliği Değerlendirmesi"),
                    "description": self.lm.tr('desc_mine_safety', "Maden güvenlik standartlarını değerlendir"),
                    "duration": self.lm.tr('duration_2_3_weeks', "2-3 hafta"),
                    "required_docs": [self.lm.tr('doc_safety_audit', "Safety Audit Report"), self.lm.tr('doc_mining_license', "Mining License")],
                    "stakeholders": [self.lm.tr('stakeholder_mining_eng', "Mining Engineers"), self.lm.tr('stakeholder_safety_insp', "Safety Inspectors"), self.lm.tr('stakeholder_regulators', "Regulators")]
                },
                {
                    "step": 2,
                    "title": self.lm.tr('step_env_rehab', "Çevresel Rehabilitasyon"),
                    "description": self.lm.tr('desc_rehab_plan', "Maden alanlarının çevresel rehabilitasyon planını hazırla"),
                    "duration": self.lm.tr('duration_4_8_weeks', "4-8 hafta"),
                    "required_docs": [self.lm.tr('doc_rehab_plan', "Rehabilitation Plan"), self.lm.tr('doc_env_baseline', "Environmental Baseline")],
                    "stakeholders": [self.lm.tr('stakeholder_env_consult', "Environmental Consultants"), self.lm.tr('stakeholder_land_owners', "Land Owners"), self.lm.tr('stakeholder_gov', "Government")]
                }
            ],
            "GRI 13": [
                {
                    "step": 1,
                    "title": self.lm.tr('step_sust_agri_assessment', "Sürdürülebilir Tarım Değerlendirmesi"),
                    "description": self.lm.tr('desc_agri_impact', "Tarım uygulamalarının sürdürülebilirlik etkisini değerlendir"),
                    "duration": self.lm.tr('duration_3_4_weeks', "3-4 hafta"),
                    "required_docs": [self.lm.tr('doc_sust_assessment', "Sustainability Assessment"), self.lm.tr('doc_farm_records', "Farm Records")],
                    "stakeholders": [self.lm.tr('stakeholder_agri_experts', "Agricultural Experts"), self.lm.tr('stakeholder_farmers', "Farmers"), self.lm.tr('stakeholder_cert_bodies', "Certification Bodies")]
                },
                {
                    "step": 2,
                    "title": self.lm.tr('step_water_soil_mgmt', "Su ve Toprak Yönetimi"),
                    "description": self.lm.tr('desc_water_soil_plan', "Su kullanımı ve toprak sağlığı planını hazırla"),
                    "duration": self.lm.tr('duration_2_3_weeks', "2-3 hafta"),
                    "required_docs": [self.lm.tr('doc_water_usage', "Water Usage Data"), self.lm.tr('doc_soil_report', "Soil Quality Report")],
                    "stakeholders": [self.lm.tr('stakeholder_water_mgmt', "Water Management"), self.lm.tr('stakeholder_soil_sci', "Soil Scientists"), self.lm.tr('stakeholder_env_agency', "Environmental Agency")]
                }
            ],
            "GRI 14": [
                {
                    "step": 1,
                    "title": self.lm.tr('step_mine_lifecycle', "Maden Yaşam Döngüsü Planlaması"),
                    "description": self.lm.tr('desc_mine_lifecycle_plan', "Maden operasyonlarının tüm yaşam döngüsünü planla"),
                    "duration": self.lm.tr('duration_4_6_weeks', "4-6 hafta"),
                    "required_docs": [self.lm.tr('doc_lifecycle_plan', "Lifecycle Plan"), self.lm.tr('doc_mining_license', "Mining License")],
                    "stakeholders": [self.lm.tr('stakeholder_mining_eng', "Mining Engineers"), self.lm.tr('stakeholder_env_consult', "Environmental Consultants"), self.lm.tr('stakeholder_investors', "Investors")]
                },
                {
                    "step": 2,
                    "title": self.lm.tr('step_eia', "Çevresel Etki Değerlendirmesi"),
                    "description": self.lm.tr('desc_mining_eia', "Madencilik faaliyetlerinin çevresel etkilerini değerlendir"),
                    "duration": self.lm.tr('duration_6_8_weeks', "6-8 hafta"),
                    "required_docs": [self.lm.tr('doc_eia_report', "EIA Report"), self.lm.tr('doc_baseline_studies', "Baseline Studies")],
                    "stakeholders": [self.lm.tr('stakeholder_env_consult', "Environmental Consultants"), self.lm.tr('stakeholder_gov', "Government"), self.lm.tr('stakeholder_local_communities', "Local Communities")]
                }
            ]
        }

        return workflows.get(sector_code, [])

    def create_sector_workflow_templates(self) -> None:
        """Sektör iş akışı şablonlarını veritabanına kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Sektör iş akışı tablosu oluştur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_sector_workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sector_code TEXT NOT NULL,
                    sector_name TEXT NOT NULL,
                    description TEXT,
                    key_topics TEXT,
                    mandatory_indicators TEXT,
                    special_requirements TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Sektör iş akışı adımları tablosu oluştur
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_workflow_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id INTEGER,
                    step_number INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    duration TEXT,
                    required_docs TEXT,
                    stakeholders TEXT,
                    FOREIGN KEY (workflow_id) REFERENCES gri_sector_workflows(id)
                )
            """)

            # Sektör standartlarını kaydet
            sector_standards = self.get_sector_standards()

            for sector_code, sector_data in sector_standards.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_sector_workflows 
                    (sector_code, sector_name, description, key_topics, mandatory_indicators, special_requirements)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    sector_code,
                    sector_data['name'],
                    sector_data['description'],
                    ','.join(sector_data['key_topics']),
                    ','.join(sector_data['mandatory_indicators']),
                    ','.join(sector_data['special_requirements'])
                ))

                workflow_id = cursor.lastrowid

                # İş akışı adımlarını kaydet
                workflow_steps = self.get_sector_workflow_steps(sector_code)

                for step in workflow_steps:
                    cursor.execute("""
                        INSERT INTO gri_workflow_steps 
                        (workflow_id, step_number, title, description, duration, required_docs, stakeholders)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        workflow_id,
                        step['step'],
                        step['title'],
                        step['description'],
                        step['duration'],
                        ','.join(step['required_docs']),
                        ','.join(step['stakeholders'])
                    ))

            conn.commit()
            logging.info(f"Sektör iş akışları oluşturuldu: {len(sector_standards)} sektör")

        except Exception as e:
            logging.error(f"Sektör iş akışları oluşturulurken hata: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_sector_compliance_status(self, company_id: int, sector_code: str) -> Dict:
        """Sektör uyumluluk durumunu değerlendir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Sektör standartlarını al
            cursor.execute("""
                SELECT * FROM gri_sector_workflows WHERE sector_code = ?
            """, (sector_code,))

            sector_data = cursor.fetchone()
            if not sector_data:
                return {"error": self.lm.tr('error_sector_not_found', "Sektör bulunamadı")}

            # Zorunlu göstergeleri kontrol et
            mandatory_indicators = sector_data[5].split(',') if sector_data[5] else []

            completed_indicators = []
            missing_indicators = []

            for indicator_code in mandatory_indicators:
                cursor.execute("""
                    SELECT COUNT(*) FROM gri_responses gr
                    JOIN gri_indicators gi ON gr.indicator_id = gi.id
                    WHERE gi.code = ? AND gr.company_id = ? AND gr.response_value IS NOT NULL
                """, (indicator_code.strip(), company_id))

                count = cursor.fetchone()[0]
                if count > 0:
                    completed_indicators.append(indicator_code.strip())
                else:
                    missing_indicators.append(indicator_code.strip())

            # Uyumluluk yüzdesini hesapla
            total_mandatory = len(mandatory_indicators)
            completed_count = len(completed_indicators)
            compliance_percentage = (completed_count / total_mandatory * 100) if total_mandatory > 0 else 0

            return {
                "sector_code": sector_code,
                "sector_name": sector_data[2],
                "total_mandatory_indicators": total_mandatory,
                "completed_indicators": completed_count,
                "missing_indicators": missing_indicators,
                "compliance_percentage": compliance_percentage,
                "compliance_status": self.lm.tr('status_compliant', "Compliant") if compliance_percentage >= 80 else self.lm.tr('status_non_compliant', "Non-Compliant")
            }

        except Exception as e:
            logging.error(f"Sektör uyumluluk durumu değerlendirilirken hata: {e}")
            return {"error": str(e)}
        finally:
            conn.close()

def create_sector_workflows() -> None:
    """Sektör iş akışlarını oluştur"""
    workflows = GRISectorWorkflows()
    workflows.create_sector_workflow_templates()
    logging.info("Sektör iş akışları başarıyla oluşturuldu")

if __name__ == "__main__":
    create_sector_workflows()
