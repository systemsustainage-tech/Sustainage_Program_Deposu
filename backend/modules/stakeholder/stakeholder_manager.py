#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paydaş Yönetimi Modülü (SKDM)
Etkisi/Önem Matrisi, İletişim Planı, Anketler
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List
from config.database import DB_PATH


class StakeholderManager:
    """Paydaş yönetimi ve etkileşim takibi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Paydaş yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
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

            cursor.execute("""
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

            cursor.execute("""
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
            cursor.execute("""
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
                cursor.execute("PRAGMA table_info(stakeholder_surveys)")
                columns = [info[1] for info in cursor.fetchall()]
                
                if 'stakeholder_group' not in columns:
                    cursor.execute("ALTER TABLE stakeholder_surveys ADD COLUMN stakeholder_group TEXT DEFAULT 'Genel'")
                    logging.info("stakeholder_surveys tablosuna stakeholder_group kolonu eklendi.")
                
                if 'response_rate' not in columns:
                    cursor.execute("ALTER TABLE stakeholder_surveys ADD COLUMN response_rate REAL")
                    logging.info("stakeholder_surveys tablosuna response_rate kolonu eklendi.")
                    
                if 'overall_satisfaction' not in columns:
                    cursor.execute("ALTER TABLE stakeholder_surveys ADD COLUMN overall_satisfaction REAL")
                    logging.info("stakeholder_surveys tablosuna overall_satisfaction kolonu eklendi.")

            except Exception as e:
                logging.error(f"Kolon ekleme hatası: {e}")

            # Anket Şablonları
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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

            conn.commit()
            logging.info("[OK] Paydas yonetimi modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Paydas yonetimi modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        stats = {
            'total_stakeholders': 0,
            'active_engagements': 0,
            'completed_surveys': 0,
            'open_complaints': 0
        }
        try:
            cursor.execute("SELECT COUNT(*) FROM stakeholders WHERE company_id = ? AND status = 'active'", (company_id,))
            stats['total_stakeholders'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM stakeholder_engagements WHERE company_id = ?", (company_id,))
            stats['active_engagements'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM stakeholder_surveys WHERE company_id = ?", (company_id,))
            stats['completed_surveys'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM stakeholder_complaints WHERE company_id = ? AND status = 'open'", (company_id,))
            stats['open_complaints'] = cursor.fetchone()[0] or 0
            
            return stats
        except Exception as e:
            logging.error(f"Paydaş istatistikleri getirme hatası: {e}")
            return stats
        finally:
            conn.close()

    def add_stakeholder(self, company_id: int, stakeholder_name: str, stakeholder_type: str,
                      contact_person: str = None, contact_email: str = None,
                      contact_phone: str = None, organization: str = None,
                      sector: str = None, influence_level: str = None,
                      interest_level: str = None, engagement_frequency: str = None) -> bool:
        """Paydaş ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO stakeholders 
                (company_id, stakeholder_name, stakeholder_type, contact_person,
                 contact_email, contact_phone, organization, sector, influence_level,
                 interest_level, engagement_frequency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, stakeholder_name, stakeholder_type, contact_person,
                  contact_email, contact_phone, organization, sector, influence_level,
                  interest_level, engagement_frequency))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Paydaş ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_stakeholder_engagement(self, company_id: int, stakeholder_id: int,
                                 engagement_date: str, engagement_type: str,
                                 engagement_topic: str, participants: str = None,
                                 outcomes: str = None, follow_up_actions: str = None,
                                 satisfaction_score: float = None) -> bool:
        """Paydaş etkileşimi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO stakeholder_engagements 
                (company_id, stakeholder_id, engagement_date, engagement_type,
                 engagement_topic, participants, outcomes, follow_up_actions, satisfaction_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, stakeholder_id, engagement_date, engagement_type,
                  engagement_topic, participants, outcomes, follow_up_actions, satisfaction_score))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Paydaş etkileşimi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_stakeholder_survey(self, company_id: int, survey_name: str, survey_period: str,
                             survey_type: str, stakeholder_group: str,
                             response_count: int = None, total_invitations: int = None,
                             overall_satisfaction: float = None, key_findings: str = None) -> bool:
        """Paydaş anketi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            response_rate = None
            if response_count and total_invitations:
                response_rate = (response_count / total_invitations) * 100

            cursor.execute("""
                INSERT INTO stakeholder_surveys 
                (company_id, survey_name, survey_period, survey_type, stakeholder_group,
                 response_count, total_invitations, response_rate, overall_satisfaction, key_findings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, survey_name, survey_period, survey_type, stakeholder_group,
                  response_count, total_invitations, response_rate, overall_satisfaction, key_findings))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Paydaş anketi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # İletişim Planı CRUD
    def add_communication_plan(self, company_id: int, communication_channel: str,
                                frequency: str = None, owner: str = None,
                                next_action: str = None, notes: str = None,
                                stakeholder_id: int = None) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO stakeholder_communication_plans
                (company_id, stakeholder_id, communication_channel, frequency, owner, next_action, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, stakeholder_id, communication_channel, frequency, owner, next_action, notes))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"İletişim planı ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_communication_plans(self, company_id: int) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, stakeholder_id, communication_channel, frequency, owner, next_action, notes, created_at
                FROM stakeholder_communication_plans
                WHERE company_id = ?
                ORDER BY created_at DESC
            """, (company_id,))
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, r)) for r in cursor.fetchall()]
        except Exception as e:
            logging.error(f"İletişim planları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    # Anket Şablonları CRUD
    def add_survey_template(self, company_id: int, template_name: str,
                            stakeholder_category: str, questions_json: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO stakeholder_survey_templates
                (company_id, template_name, stakeholder_category, questions_json)
                VALUES (?, ?, ?, ?)
            """, (company_id, template_name, stakeholder_category, questions_json))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Anket şablonu ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_survey_templates(self, company_id: int) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, template_name, stakeholder_category, questions_json, created_at
                FROM stakeholder_survey_templates
                WHERE company_id = ?
                ORDER BY created_at DESC
            """, (company_id,))
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, r)) for r in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Anket şablonları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    # Eylem Planı CRUD
    def add_action_plan(self, company_id: int, title: str, description: str = None,
                        owner: str = None, due_date: str = None, status: str = 'open',
                        stakeholder_id: int = None, engagement_id: int = None) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            now = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO stakeholder_action_plans
                (company_id, title, description, owner, due_date, status, stakeholder_id, engagement_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, title, description, owner, due_date, status, stakeholder_id, engagement_id, now, now))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Eylem planı ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def update_action_plan_status(self, plan_id: int, status: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE stakeholder_action_plans SET status = ?, updated_at = ? WHERE id = ?
            """, (status, datetime.now().isoformat(), plan_id))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Eylem planı güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_action_plans(self, company_id: int) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, title, description, owner, due_date, status, stakeholder_id, engagement_id, created_at, updated_at
                FROM stakeholder_action_plans WHERE company_id = ? ORDER BY created_at DESC
            """, (company_id,))
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, r)) for r in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Eylem planları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_engagements(self, company_id: int, limit: int = 100) -> List[Dict]:
        """Toplantı/Etkileşim kayıtlarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT id, stakeholder_id, engagement_date, engagement_type, engagement_topic,
                       participants, outcomes, follow_up_actions, satisfaction_score, created_at
                FROM stakeholder_engagements
                WHERE company_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (company_id, limit)
            )
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, r)) for r in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Etkileşim kayıtları getirme hatası: {e}")
            return []
        finally:
            conn.close()

    # Şikayet Yönetimi CRUD
    def add_complaint(self, company_id: int, description: str, complaint_date: str,
                      stakeholder_id: int = None, channel: str = None, severity: str = None,
                      status: str = 'open') -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO stakeholder_complaints
                (company_id, stakeholder_id, complaint_date, channel, description, severity, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, stakeholder_id, complaint_date, channel, description, severity, status))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Şikayet ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def update_complaint(self, complaint_id: int, status: str, resolution: str = None, resolved_at: str = None) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE stakeholder_complaints SET status = ?, resolution = ?, resolved_at = ? WHERE id = ?
            """, (status, resolution, resolved_at, complaint_id))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Şikayet güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_complaints(self, company_id: int) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT id, stakeholder_id, complaint_date, channel, description, severity, status, resolution, resolved_at, created_at
                FROM stakeholder_complaints WHERE company_id = ? ORDER BY complaint_date DESC
            """, (company_id,))
            cols = [d[0] for d in cursor.description]
            return [dict(zip(cols, r)) for r in cursor.fetchall()]
        except Exception as e:
            logging.error(f"Şikayetler getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def get_stakeholder_summary(self, company_id: int) -> Dict:
        """Paydaş özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Paydaş dağılımı
            cursor.execute("""
                SELECT stakeholder_type, influence_level, interest_level, COUNT(*)
                FROM stakeholders 
                WHERE company_id = ? AND status = 'active'
                GROUP BY stakeholder_type, influence_level, interest_level
            """, (company_id,))

            stakeholder_distribution = {}
            total_stakeholders = 0
            for row in cursor.fetchall():
                st_type, influence, interest, count = row
                if st_type not in stakeholder_distribution:
                    stakeholder_distribution[st_type] = {}
                if influence not in stakeholder_distribution[st_type]:
                    stakeholder_distribution[st_type][influence] = {}
                stakeholder_distribution[st_type][influence][interest] = count
                total_stakeholders += count

            # Etkileşim istatistikleri
            cursor.execute("""
                SELECT engagement_type, COUNT(*), AVG(satisfaction_score)
                FROM stakeholder_engagements 
                WHERE company_id = ?
                GROUP BY engagement_type
            """, (company_id,))

            engagement_summary = {}
            total_engagements = 0
            for row in cursor.fetchall():
                eng_type, count, avg_satisfaction = row
                engagement_summary[eng_type] = {
                    'count': count,
                    'average_satisfaction': avg_satisfaction
                }
                total_engagements += count

            # Anket sonuçları
            cursor.execute("""
                SELECT stakeholder_group, COUNT(*), AVG(response_rate), AVG(overall_satisfaction)
                FROM stakeholder_surveys 
                WHERE company_id = ?
                GROUP BY stakeholder_group
            """, (company_id,))

            survey_summary = {}
            for row in cursor.fetchall():
                group, count, avg_response_rate, avg_satisfaction = row
                survey_summary[group] = {
                    'survey_count': count,
                    'average_response_rate': avg_response_rate,
                    'average_satisfaction': avg_satisfaction
                }

            # Online Anket İstatistikleri (online_surveys tablosu varsa)
            online_survey_summary = {'active_surveys': 0, 'total_responses': 0, 'sdg_performance': {}}
            try:
                # Tablo var mı kontrolü
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='online_surveys'")
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT COUNT(*), SUM(response_count)
                        FROM online_surveys
                        WHERE company_id = ? AND is_active = 1
                    """, (company_id,))
                    online_stats = cursor.fetchone()
                    
                    # SDG Performans Skorlarını al
                    sdg_scores = {}
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sdg_survey_analytics'")
                    if cursor.fetchone():
                        cursor.execute("""
                            SELECT ssa.sdg_id, AVG(ssa.average_score) as final_score
                            FROM sdg_survey_analytics ssa
                            JOIN online_surveys os ON ssa.survey_id = os.id
                            WHERE os.company_id = ? AND os.is_active = 1
                            GROUP BY ssa.sdg_id
                            ORDER BY final_score DESC
                            LIMIT 5
                        """, (company_id,))
                        for row in cursor.fetchall():
                            sdg_scores[row[0]] = round(row[1], 2)
                    
                    online_survey_summary = {
                        'active_surveys': online_stats[0] if online_stats and online_stats[0] else 0,
                        'total_responses': online_stats[1] if online_stats and online_stats[1] else 0,
                        'sdg_performance': sdg_scores
                    }
            except Exception as e_online:
                logging.warning(f"Online anket istatistikleri alınamadı: {e_online}")

            return {
                'stakeholder_distribution': stakeholder_distribution,
                'total_stakeholders': total_stakeholders,
                'engagement_summary': engagement_summary,
                'total_engagements': total_engagements,
                'survey_summary': survey_summary,
                'online_survey_summary': online_survey_summary,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"Paydaş özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()

    def generate_stakeholder_matrix(self, company_id: int) -> Dict:
        """Paydaş Etkisi/Önem Matrisi oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT stakeholder_name, stakeholder_type, influence_level, interest_level
                FROM stakeholders 
                WHERE company_id = ? AND status = 'active'
            """, (company_id,))

            # Matris kategorileri
            high_high = []  # Yüksek Etki - Yüksek İlgi
            high_low = []   # Yüksek Etki - Düşük İlgi
            low_high = []   # Düşük Etki - Yüksek İlgi
            low_low = []    # Düşük Etki - Düşük İlgi

            for row in cursor.fetchall():
                name, st_type, influence, interest = row
                stakeholder = {
                    'name': name,
                    'type': st_type,
                    'influence': influence,
                    'interest': interest
                }

                if influence == 'High' and interest == 'High':
                    high_high.append(stakeholder)
                elif influence == 'High' and interest == 'Low':
                    high_low.append(stakeholder)
                elif influence == 'Low' and interest == 'High':
                    low_high.append(stakeholder)
                else:
                    low_low.append(stakeholder)

            return {
                'high_influence_high_interest': high_high,
                'high_influence_low_interest': high_low,
                'low_influence_high_interest': low_high,
                'low_influence_low_interest': low_low,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"Paydaş matrisi oluşturma hatası: {e}")
            return {}
        finally:
            conn.close()
