#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paydaş Yönetimi Modülü (SKDM)
Etkisi/Önem Matrisi, İletişim Planı, Anketler
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from config.database import DB_PATH
from backend.core.base_manager import BaseTenantManager

class StakeholderManager(BaseTenantManager):
    """Paydaş yönetimi ve etkileşim takibi"""

    def __init__(self, db_path: Optional[str] = None, company_id: Optional[int] = None) -> None:
        if db_path is None:
            db_path = DB_PATH
        
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
            
        super().__init__(db_path, company_id)
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Paydaş yönetimi tablolarını oluştur"""
        # BaseTenantManager uses DatabaseManager which uses a pool.
        # For DDL, we use self.db.execute_update directly as DDL is global.
        
        try:
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS stakeholders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_name TEXT NOT NULL,
                    stakeholder_type TEXT NOT NULL,
                    contact_person TEXT,
                    contact_email TEXT,
                    contact_phone TEXT,
                    organization TEXT,
                    sector TEXT,
                    influence_level TEXT,
                    interest_level TEXT,
                    engagement_frequency TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS stakeholder_engagements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_id INTEGER NOT NULL,
                    engagement_date TEXT NOT NULL,
                    engagement_type TEXT NOT NULL,
                    engagement_topic TEXT NOT NULL,
                    participants TEXT,
                    outcomes TEXT,
                    follow_up_actions TEXT,
                    satisfaction_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
                )
            """)

            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS stakeholder_surveys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    survey_name TEXT NOT NULL,
                    survey_period TEXT NOT NULL,
                    survey_type TEXT NOT NULL,
                    stakeholder_group TEXT NOT NULL,
                    response_count INTEGER,
                    total_invitations INTEGER,
                    response_rate REAL,
                    overall_satisfaction REAL,
                    key_findings TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # İletişim Planları
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS stakeholder_communication_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_id INTEGER,
                    communication_channel TEXT NOT NULL,   -- Email, Toplantı, Webinar, Rapor, etc.
                    frequency TEXT,                        -- Haftalık, Aylık, Çeyreklik
                    owner TEXT,                            -- Sorumlu kişi/birim
                    next_action TEXT,                      -- Bir sonraki adım
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
                )
            """)

            # Eksik kolon kontrolü ve ekleme (stakeholder_group)
            try:
                # PRAGMA is also safe to run via execute_query (direct)
                rows = self.db.execute_query("PRAGMA table_info(stakeholder_surveys)")
                columns = [row['name'] for row in rows]
                
                if 'stakeholder_group' not in columns:
                    self.db.execute_update("ALTER TABLE stakeholder_surveys ADD COLUMN stakeholder_group TEXT DEFAULT 'Genel'")
                    logging.info("stakeholder_surveys tablosuna stakeholder_group kolonu eklendi.")
                
                if 'response_rate' not in columns:
                    self.db.execute_update("ALTER TABLE stakeholder_surveys ADD COLUMN response_rate REAL")
                    logging.info("stakeholder_surveys tablosuna response_rate kolonu eklendi.")
                    
                if 'overall_satisfaction' not in columns:
                    self.db.execute_update("ALTER TABLE stakeholder_surveys ADD COLUMN overall_satisfaction REAL")
                    logging.info("stakeholder_surveys tablosuna overall_satisfaction kolonu eklendi.")

            except Exception as e:
                logging.error(f"Kolon ekleme hatası: {e}")

            # Anket Şablonları
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS stakeholder_survey_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    template_name TEXT NOT NULL,
                    stakeholder_category TEXT,
                    questions_json TEXT NOT NULL,          -- JSON soru listesi
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Eylem Planları
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS stakeholder_action_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    owner TEXT,
                    due_date TEXT,
                    status TEXT DEFAULT 'open',            -- open, in_progress, closed
                    stakeholder_id INTEGER,
                    engagement_id INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id),
                    FOREIGN KEY (engagement_id) REFERENCES stakeholder_engagements(id)
                )
            """)

            # Şikayet Yönetimi
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS stakeholder_complaints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    stakeholder_id INTEGER,
                    complaint_date TEXT NOT NULL,
                    channel TEXT,                          -- Email, Telefon, Portal, etc.
                    description TEXT NOT NULL,
                    severity TEXT,                         -- Düşük/Orta/Yüksek
                    status TEXT DEFAULT 'open',
                    resolution TEXT,
                    resolved_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (stakeholder_id) REFERENCES stakeholders(id)
                )
            """)

            logging.info("[OK] Paydas yonetimi modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Paydas yonetimi modulu tablo olusturma: {e}")

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        stats = {
            'total_stakeholders': 0,
            'active_engagements': 0,
            'completed_surveys': 0,
            'open_complaints': 0
        }
        try:
            stats['total_stakeholders'] = self.count('stakeholders', company_id, where="status = 'active'")
            stats['active_engagements'] = self.count('stakeholder_engagements', company_id)
            stats['completed_surveys'] = self.count('stakeholder_surveys', company_id)
            stats['open_complaints'] = self.count('stakeholder_complaints', company_id, where="status = 'open'")
            return stats
        except Exception as e:
            logging.error(f"Paydaş istatistikleri getirme hatası: {e}")
            return stats

    def add_stakeholder(self, company_id: int, stakeholder_name: str, stakeholder_type: str,
                      contact_person: str = None, contact_email: str = None,
                      contact_phone: str = None, organization: str = None,
                      sector: str = None, influence_level: str = None,
                      interest_level: str = None, engagement_frequency: str = None) -> bool:
        """Paydaş ekle"""
        try:
            data = {
                'stakeholder_name': stakeholder_name,
                'stakeholder_type': stakeholder_type,
                'contact_person': contact_person,
                'contact_email': contact_email,
                'contact_phone': contact_phone,
                'organization': organization,
                'sector': sector,
                'influence_level': influence_level,
                'interest_level': interest_level,
                'engagement_frequency': engagement_frequency
            }
            self.insert('stakeholders', data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Paydaş ekleme hatası: {e}")
            return False

    def add_stakeholder_engagement(self, company_id: int, stakeholder_id: int,
                                 engagement_date: str, engagement_type: str,
                                 engagement_topic: str, participants: str = None,
                                 outcomes: str = None, follow_up_actions: str = None,
                                 satisfaction_score: float = None) -> bool:
        """Paydaş etkileşimi ekle"""
        try:
            data = {
                'stakeholder_id': stakeholder_id,
                'engagement_date': engagement_date,
                'engagement_type': engagement_type,
                'engagement_topic': engagement_topic,
                'participants': participants,
                'outcomes': outcomes,
                'follow_up_actions': follow_up_actions,
                'satisfaction_score': satisfaction_score
            }
            self.insert('stakeholder_engagements', data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Paydaş etkileşimi ekleme hatası: {e}")
            return False

    def add_stakeholder_survey(self, company_id: int, survey_name: str, survey_period: str,
                             survey_type: str, stakeholder_group: str,
                             response_count: int = None, total_invitations: int = None,
                             overall_satisfaction: float = None, key_findings: str = None) -> bool:
        """Paydaş anketi ekle"""
        try:
            response_rate = None
            if response_count and total_invitations:
                response_rate = (response_count / total_invitations) * 100

            data = {
                'survey_name': survey_name,
                'survey_period': survey_period,
                'survey_type': survey_type,
                'stakeholder_group': stakeholder_group,
                'response_count': response_count,
                'total_invitations': total_invitations,
                'response_rate': response_rate,
                'overall_satisfaction': overall_satisfaction,
                'key_findings': key_findings
            }
            self.insert('stakeholder_surveys', data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Paydaş anketi ekleme hatası: {e}")
            return False

    # İletişim Planı CRUD
    def add_communication_plan(self, company_id: int, communication_channel: str,
                                frequency: str = None, owner: str = None,
                                next_action: str = None, notes: str = None,
                                stakeholder_id: int = None) -> bool:
        try:
            data = {
                'stakeholder_id': stakeholder_id,
                'communication_channel': communication_channel,
                'frequency': frequency,
                'owner': owner,
                'next_action': next_action,
                'notes': notes
            }
            self.insert('stakeholder_communication_plans', data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"İletişim planı ekleme hatası: {e}")
            return False

    def get_communication_plans(self, company_id: int) -> List[Dict]:
        try:
            return self.select(
                'stakeholder_communication_plans', 
                company_id=company_id, 
                order_by='created_at DESC'
            )
        except Exception as e:
            logging.error(f"İletişim planları getirme hatası: {e}")
            return []

    # Anket Şablonları CRUD
    def add_survey_template(self, company_id: int, template_name: str,
                            stakeholder_category: str, questions_json: str) -> bool:
        try:
            data = {
                'template_name': template_name,
                'stakeholder_category': stakeholder_category,
                'questions_json': questions_json
            }
            self.insert('stakeholder_survey_templates', data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Anket şablonu ekleme hatası: {e}")
            return False

    def get_survey_templates(self, company_id: int) -> List[Dict]:
        try:
            return self.select(
                'stakeholder_survey_templates', 
                company_id=company_id, 
                order_by='created_at DESC'
            )
        except Exception as e:
            logging.error(f"Anket şablonları getirme hatası: {e}")
            return []

    # Eylem Planı CRUD
    def add_action_plan(self, company_id: int, title: str, description: str = None,
                        owner: str = None, due_date: str = None, status: str = 'open',
                        stakeholder_id: int = None, engagement_id: int = None) -> bool:
        try:
            now = datetime.now().isoformat()
            data = {
                'title': title,
                'description': description,
                'owner': owner,
                'due_date': due_date,
                'status': status,
                'stakeholder_id': stakeholder_id,
                'engagement_id': engagement_id,
                'created_at': now,
                'updated_at': now
            }
            self.insert('stakeholder_action_plans', data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Eylem planı ekleme hatası: {e}")
            return False

    def update_action_plan_status(self, plan_id: int, status: str, company_id: int) -> bool:
        """
        Eylem planı durumunu güncelle.
        
        Args:
            plan_id: Plan ID
            status: Yeni durum
            company_id: Şirket ID (Multi-tenant güvenlik için zorunlu)
        """
        try:
            data = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
            # company_id filtresi ile güncelleme yaparak diğer şirketlerin verisini koruruz
            affected = self.update(
                'stakeholder_action_plans', 
                data, 
                company_id=company_id, 
                where='id = ?', 
                params=(plan_id,)
            )
            return affected > 0
        except Exception as e:
            logging.error(f"Eylem planı güncelleme hatası: {e}")
            return False

    def get_action_plans(self, company_id: int) -> List[Dict]:
        try:
            return self.select(
                'stakeholder_action_plans', 
                company_id=company_id, 
                order_by='created_at DESC'
            )
        except Exception as e:
            logging.error(f"Eylem planları getirme hatası: {e}")
            return []

    def get_engagements(self, company_id: int, limit: int = 100) -> List[Dict]:
        """Toplantı/Etkileşim kayıtlarını getir"""
        try:
            return self.select(
                'stakeholder_engagements',
                company_id=company_id,
                order_by='id DESC',
                limit=limit
            )
        except Exception as e:
            logging.error(f"Etkileşim kayıtları getirme hatası: {e}")
            return []

    # Şikayet Yönetimi CRUD
    def add_complaint(self, company_id: int, description: str, complaint_date: str,
                      stakeholder_id: int = None, channel: str = None, severity: str = None,
                      status: str = 'open') -> bool:
        try:
            data = {
                'stakeholder_id': stakeholder_id,
                'description': description,
                'complaint_date': complaint_date,
                'channel': channel,
                'severity': severity,
                'status': status
            }
            self.insert('stakeholder_complaints', data, company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"Şikayet ekleme hatası: {e}")
            return False
