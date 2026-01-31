#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Etik ve Uyumluluk Yönetimi Modülü
Etik davranış, uyumluluk ve risk yönetimi
"""

import logging
import os
import sqlite3
from typing import Dict
from config.database import DB_PATH


class EthicsComplianceManager:
    """Etik ve uyumluluk yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Etik ve uyumluluk tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ethics_violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    violation_date TEXT NOT NULL,
                    violation_type TEXT NOT NULL,
                    severity_level TEXT NOT NULL,
                    description TEXT,
                    reporter_name TEXT,
                    investigation_status TEXT,
                    disciplinary_action TEXT,
                    preventive_measures TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS compliance_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    regulation_type TEXT NOT NULL,
                    compliance_status TEXT NOT NULL,
                    compliance_score REAL,
                    non_compliance_items TEXT,
                    corrective_actions TEXT,
                    next_review_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ethics_training (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    training_date TEXT NOT NULL,
                    training_topic TEXT NOT NULL,
                    participant_count INTEGER NOT NULL,
                    completion_rate REAL,
                    assessment_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Etik ve uyumluluk modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Etik ve uyumluluk modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_ethics_violation(self, company_id: int, violation_date: str, violation_type: str,
                           severity_level: str, description: str = None, reporter_name: str = None,
                           investigation_status: str = None, disciplinary_action: str = None,
                           preventive_measures: str = None) -> bool:
        """Etik ihlal ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO ethics_violations 
                (company_id, violation_date, violation_type, severity_level, description,
                 reporter_name, investigation_status, disciplinary_action, preventive_measures)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, violation_date, violation_type, severity_level, description,
                  reporter_name, investigation_status, disciplinary_action, preventive_measures))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Etik ihlal ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_compliance_assessment(self, company_id: int, assessment_date: str, regulation_type: str,
                                compliance_status: str, compliance_score: float = None,
                                non_compliance_items: str = None, corrective_actions: str = None,
                                next_review_date: str = None) -> bool:
        """Uyumluluk değerlendirmesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO compliance_assessments 
                (company_id, assessment_date, regulation_type, compliance_status,
                 compliance_score, non_compliance_items, corrective_actions, next_review_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, assessment_date, regulation_type, compliance_status,
                  compliance_score, non_compliance_items, corrective_actions, next_review_date))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Uyumluluk değerlendirmesi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_ethics_training(self, company_id: int, training_date: str, training_topic: str,
                          participant_count: int, completion_rate: float = None,
                          assessment_score: float = None) -> bool:
        """Etik eğitimi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO ethics_training 
                (company_id, training_date, training_topic, participant_count,
                 completion_rate, assessment_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, training_date, training_topic, participant_count,
                  completion_rate, assessment_score))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Etik eğitimi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_ethics_compliance_summary(self, company_id: int, year: int) -> Dict:
        """Etik ve uyumluluk özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Etik ihlaller
            cursor.execute("""
                SELECT violation_type, severity_level, COUNT(*)
                FROM ethics_violations 
                WHERE company_id = ? AND strftime('%Y', violation_date) = ?
                GROUP BY violation_type, severity_level
            """, (company_id, str(year)))

            violation_summary = {}
            total_violations = 0
            for row in cursor.fetchall():
                violation_type, severity, count = row
                if violation_type not in violation_summary:
                    violation_summary[violation_type] = {}
                violation_summary[violation_type][severity] = count
                total_violations += count

            # Uyumluluk değerlendirmeleri
            cursor.execute("""
                SELECT regulation_type, compliance_status, AVG(compliance_score), COUNT(*)
                FROM compliance_assessments 
                WHERE company_id = ? AND strftime('%Y', assessment_date) = ?
                GROUP BY regulation_type, compliance_status
            """, (company_id, str(year)))

            compliance_summary = {}
            total_assessments = 0
            for row in cursor.fetchall():
                regulation_type, compliance_status, avg_score, count = row
                if regulation_type not in compliance_summary:
                    compliance_summary[regulation_type] = {}
                compliance_summary[regulation_type][compliance_status] = {
                    'count': count,
                    'average_score': avg_score
                }
                total_assessments += count

            # Etik eğitimleri
            cursor.execute("""
                SELECT training_topic, COUNT(*), SUM(participant_count), AVG(completion_rate), AVG(assessment_score)
                FROM ethics_training 
                WHERE company_id = ? AND strftime('%Y', training_date) = ?
                GROUP BY training_topic
            """, (company_id, str(year)))

            training_summary = {}
            total_participants = 0
            for row in cursor.fetchall():
                topic, sessions, participants, completion_rate, avg_score = row
                training_summary[topic] = {
                    'sessions': sessions,
                    'participants': participants,
                    'completion_rate': completion_rate,
                    'average_score': avg_score
                }
                total_participants += participants or 0

            return {
                'violation_summary': violation_summary,
                'total_violations': total_violations,
                'compliance_summary': compliance_summary,
                'total_assessments': total_assessments,
                'training_summary': training_summary,
                'total_training_participants': total_participants,
                'year': year,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"Etik ve uyumluluk özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()
