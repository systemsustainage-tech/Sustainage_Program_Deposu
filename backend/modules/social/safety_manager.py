#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İş Sağlığı ve Güvenliği Yönetimi Modülü
İSG olayları, eğitimleri ve güvenlik metrikleri
Refactored for Multi-tenancy using BaseTenantManager
"""

import logging
import os
from typing import Dict, List, Optional
from config.database import DB_PATH
try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    from core.base_manager import BaseTenantManager


class SafetyManager(BaseTenantManager):
    """İş Sağlığı ve Güvenliği yönetimi"""

    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        
        super().__init__(db_path, company_id)
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """İSG yönetimi tablolarını oluştur"""
        try:
            # İSG olayları
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS safety_incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    incident_date TEXT NOT NULL,
                    incident_type TEXT NOT NULL,
                    severity_level TEXT NOT NULL,
                    location TEXT,
                    department TEXT,
                    employee_id INTEGER,
                    description TEXT,
                    root_cause TEXT,
                    corrective_actions TEXT,
                    prevention_measures TEXT,
                    lost_work_days INTEGER,
                    medical_treatment TEXT,
                    investigation_status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # İSG eğitimleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS safety_trainings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    training_date TEXT NOT NULL,
                    training_type TEXT NOT NULL,
                    training_topic TEXT NOT NULL,
                    trainer_name TEXT,
                    participant_count INTEGER NOT NULL,
                    duration_hours REAL,
                    training_method TEXT,
                    assessment_score REAL,
                    certification_validity TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Risk değerlendirmeleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS risk_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    risk_area TEXT NOT NULL,
                    hazard_type TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    probability_score INTEGER,
                    severity_score INTEGER,
                    risk_score INTEGER,
                    existing_controls TEXT,
                    additional_controls TEXT,
                    responsible_person TEXT,
                    review_date TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # İSG denetimleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS safety_audits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    audit_date TEXT NOT NULL,
                    audit_type TEXT NOT NULL,
                    auditor_name TEXT,
                    audit_scope TEXT,
                    compliance_score REAL,
                    non_conformities INTEGER,
                    observations INTEGER,
                    recommendations INTEGER,
                    follow_up_date TEXT,
                    status TEXT DEFAULT 'completed',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # İSG hedefleri
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS safety_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_value REAL,
                    target_value REAL,
                    target_unit TEXT,
                    target_description TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # İSG KPI'ları
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS safety_kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER,
                    kpi_name TEXT NOT NULL,
                    kpi_value REAL NOT NULL,
                    kpi_unit TEXT NOT NULL,
                    benchmark_value REAL,
                    target_value REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            logging.info("[OK] ISG yonetimi modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] ISG yonetimi modulu tablo olusturma: {e}")

    def add_safety_incident(self, company_id: int, incident_date: str, incident_type: str,
                          severity_level: str, location: str = None, department: str = None,
                          employee_id: int = None, description: str = None, root_cause: str = None,
                          corrective_actions: str = None, prevention_measures: str = None,
                          lost_work_days: int = None, medical_treatment: str = None,
                          investigation_status: str = None) -> bool:
        """İSG olayı ekle"""
        try:
            data = {
                'incident_date': incident_date,
                'incident_type': incident_type,
                'severity_level': severity_level,
                'location': location,
                'department': department,
                'employee_id': employee_id,
                'description': description,
                'root_cause': root_cause,
                'corrective_actions': corrective_actions,
                'prevention_measures': prevention_measures,
                'lost_work_days': lost_work_days,
                'medical_treatment': medical_treatment,
                'investigation_status': investigation_status
            }
            
            self.insert('safety_incidents', data, company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"İSG olayı ekleme hatası: {e}")
            return False

    def add_safety_training(self, company_id: int, training_date: str, training_type: str,
                          training_topic: str, trainer_name: str, participant_count: int,
                          duration_hours: float = None, training_method: str = None,
                          assessment_score: float = None, certification_validity: str = None) -> bool:
        """İSG eğitimi ekle"""
        try:
            data = {
                'training_date': training_date,
                'training_type': training_type,
                'training_topic': training_topic,
                'trainer_name': trainer_name,
                'participant_count': participant_count,
                'duration_hours': duration_hours,
                'training_method': training_method,
                'assessment_score': assessment_score,
                'certification_validity': certification_validity
            }
            
            self.insert('safety_trainings', data, company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"İSG eğitimi ekleme hatası: {e}")
            return False

    def add_risk_assessment(self, company_id: int, assessment_date: str, risk_area: str,
                          hazard_type: str, risk_level: str, probability_score: int,
                          severity_score: int, existing_controls: str = None,
                          additional_controls: str = None, responsible_person: str = None,
                          review_date: str = None) -> bool:
        """Risk değerlendirmesi ekle"""
        try:
            risk_score = probability_score * severity_score
            
            data = {
                'assessment_date': assessment_date,
                'risk_area': risk_area,
                'hazard_type': hazard_type,
                'risk_level': risk_level,
                'probability_score': probability_score,
                'severity_score': severity_score,
                'risk_score': risk_score,
                'existing_controls': existing_controls,
                'additional_controls': additional_controls,
                'responsible_person': responsible_person,
                'review_date': review_date
            }
            
            self.insert('risk_assessments', data, company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"Risk değerlendirmesi ekleme hatası: {e}")
            return False

    def add_safety_audit(self, company_id: int, audit_date: str, audit_type: str,
                        auditor_name: str, audit_scope: str, compliance_score: float,
                        non_conformities: int, observations: int, recommendations: int,
                        follow_up_date: str = None) -> bool:
        """İSG denetimi ekle"""
        try:
            data = {
                'audit_date': audit_date,
                'audit_type': audit_type,
                'auditor_name': auditor_name,
                'audit_scope': audit_scope,
                'compliance_score': compliance_score,
                'non_conformities': non_conformities,
                'observations': observations,
                'recommendations': recommendations,
                'follow_up_date': follow_up_date
            }
            
            self.insert('safety_audits', data, company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"İSG denetimi ekleme hatası: {e}")
            return False

    def set_safety_target(self, company_id: int, target_year: int, target_type: str,
                         baseline_value: float, target_value: float, target_unit: str,
                         target_description: str = None) -> bool:
        """İSG hedefi belirle"""
        try:
            # Note: insert() doesn't support REPLACE, so we use execute_update for this specific query if we want REPLACE logic.
            # However, standard insert is often fine unless uniqueness constraint exists.
            # Given the original code used INSERT OR REPLACE, let's stick to execute_update to match logic.
            
            self.execute_update("""
                INSERT OR REPLACE INTO safety_targets 
                (company_id, target_year, target_type, baseline_value, target_value,
                 target_unit, target_description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, target_year, target_type, baseline_value, target_value,
                  target_unit, target_description))
            return True

        except Exception as e:
            logging.error(f"İSG hedefi belirleme hatası: {e}")
            return False

    def get_safety_summary(self, company_id: int, year: int) -> Dict:
        """İSG özeti getir"""
        try:
            # İSG olayları
            rows = self.execute_query("""
                SELECT incident_type, severity_level, COUNT(*), SUM(lost_work_days)
                FROM safety_incidents 
                WHERE company_id = ? AND strftime('%Y', incident_date) = ?
                GROUP BY incident_type, severity_level
            """, (company_id, str(year)))

            incident_summary = {}
            total_incidents = 0
            total_lost_days = 0
            for row in rows:
                incident_type, severity, count, lost_days = row
                if incident_type not in incident_summary:
                    incident_summary[incident_type] = {}
                incident_summary[incident_type][severity] = count
                total_incidents += count
                total_lost_days += lost_days or 0

            # İSG eğitimleri
            rows = self.execute_query("""
                SELECT training_type, COUNT(*), SUM(participant_count), SUM(duration_hours), AVG(assessment_score)
                FROM safety_trainings 
                WHERE company_id = ? AND strftime('%Y', training_date) = ?
                GROUP BY training_type
            """, (company_id, str(year)))

            training_summary = {}
            total_participants = 0
            total_hours = 0
            for row in rows:
                training_type, count, participants, hours, avg_score = row
                training_summary[training_type] = {
                    'sessions': count,
                    'participants': participants,
                    'hours': hours or 0,
                    'average_score': avg_score
                }
                total_participants += participants or 0
                total_hours += hours or 0

            # Risk değerlendirmeleri
            rows = self.execute_query("""
                SELECT risk_level, COUNT(*), AVG(risk_score)
                FROM risk_assessments 
                WHERE company_id = ? AND strftime('%Y', assessment_date) = ? AND status = 'active'
                GROUP BY risk_level
            """, (company_id, str(year)))

            risk_summary = {}
            total_risks = 0
            for row in rows:
                risk_level, count, avg_score = row
                risk_summary[risk_level] = {
                    'count': count,
                    'average_score': avg_score
                }
                total_risks += count

            # İSG denetimleri
            rows = self.execute_query("""
                SELECT AVG(compliance_score), SUM(non_conformities), SUM(observations), COUNT(*)
                FROM safety_audits 
                WHERE company_id = ? AND strftime('%Y', audit_date) = ?
            """, (company_id, str(year)))

            if rows:
                audit_result = rows[0]
                # Check if result is dict or tuple (BaseTenantManager returns dict usually, but execute_query returns list of tuples/rows from sqlite3 unless row_factory set)
                # DatabaseManager uses row_factory=sqlite3.Row, so it behaves like dict/tuple
                
                # If using index access:
                avg_compliance = audit_result[0] or 0
                total_non_conformities = audit_result[1] or 0
                total_observations = audit_result[2] or 0
                total_audits = audit_result[3] or 0
            else:
                avg_compliance = 0
                total_non_conformities = 0
                total_observations = 0
                total_audits = 0

            return {
                'incident_summary': incident_summary,
                'total_incidents': total_incidents,
                'total_lost_work_days': total_lost_days,
                'training_summary': training_summary,
                'total_training_participants': total_participants,
                'total_training_hours': total_hours,
                'risk_summary': risk_summary,
                'total_risks': total_risks,
                'average_compliance_score': avg_compliance,
                'total_non_conformities': total_non_conformities,
                'total_observations': total_observations,
                'total_audits': total_audits,
                'year': year,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"İSG özeti getirme hatası: {e}")
            return {}

    def get_safety_targets(self, company_id: int) -> List[Dict]:
        """İSG hedeflerini getir"""
        try:
            return self.select('safety_targets', company_id=company_id, where="status = 'active'", order_by='target_year')
        except Exception as e:
            logging.error(f"İSG hedefleri getirme hatası: {e}")
            return []

    def calculate_safety_kpis(self, company_id: int, year: int, total_employees: int = 100) -> Dict:
        """İSG KPI'larını hesapla"""
        summary = self.get_safety_summary(company_id, year)

        if not summary:
            return {}

        # İSG olay oranları (100.000 çalışan başına)
        incident_rate = (summary['total_incidents'] / total_employees) * 100000

        # Kayıp iş günü oranı (100.000 çalışan başına)
        lost_time_rate = (summary['total_lost_work_days'] / total_employees) * 100000

        # Eğitim katılım oranı
        training_participation_rate = (summary['total_training_participants'] / total_employees) * 100 if total_employees > 0 else 0

        # Risk seviyesi dağılımı
        high_risk_ratio = 0
        medium_risk_ratio = 0
        low_risk_ratio = 0

        if summary['total_risks'] > 0:
            high_risk_ratio = (summary['risk_summary'].get('High', {}).get('count', 0) / summary['total_risks']) * 100
            medium_risk_ratio = (summary['risk_summary'].get('Medium', {}).get('count', 0) / summary['total_risks']) * 100
            low_risk_ratio = (summary['risk_summary'].get('Low', {}).get('count', 0) / summary['total_risks']) * 100

        return {
            'total_incidents': summary['total_incidents'],
            'incident_rate_per_100k': incident_rate,
            'total_lost_work_days': summary['total_lost_work_days'],
            'lost_time_rate_per_100k': lost_time_rate,
            'training_participation_rate': training_participation_rate,
            'average_compliance_score': summary['average_compliance_score'],
            'high_risk_ratio': high_risk_ratio,
            'medium_risk_ratio': medium_risk_ratio,
            'low_risk_ratio': low_risk_ratio,
            'total_audits': summary['total_audits'],
            'year': year,
            'company_id': company_id
        }
