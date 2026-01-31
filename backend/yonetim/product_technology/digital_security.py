#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DİJİTAL GÜVENLİK VE DİJİTALLEŞME MODÜLÜ
- Bilgi güvenliği yönetimi (ISO 27001)
- Siber güvenlik metrikleri
- Dijital dönüşüm takibi
- Yapay zeka uygulamaları
"""

import sqlite3
from typing import Dict, List


class DigitalSecurityModule:
    """Dijital güvenlik ve dijitalleşme yönetimi sınıfı"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def create_digital_security_tables(self) -> None:
        """Dijital güvenlik tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Dijital güvenlik metrikleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS digital_security_metrics (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                period TEXT NOT NULL,
                iso27001_certified BOOLEAN DEFAULT 0, -- ISO 27001 sertifikası
                cybersecurity_training_hours REAL, -- Siber güvenlik eğitim saatleri
                data_breach_count INTEGER DEFAULT 0, -- Veri ihlali sayısı
                data_breach_severity TEXT, -- Düşük, Orta, Yüksek, Kritik
                digital_transformation_budget REAL, -- Dijital dönüşüm bütçesi
                ai_applications_count INTEGER DEFAULT 0, -- AI uygulama sayısı
                cloud_adoption_percentage REAL, -- Bulut kullanım oranı (%)
                automation_percentage REAL, -- Otomasyon oranı (%)
                digital_literacy_score REAL, -- Dijital okuryazarlık skoru (1-10)
                cybersecurity_incidents INTEGER DEFAULT 0, -- Siber güvenlik olayları
                incident_response_time REAL, -- Olay müdahale süresi (saat)
                backup_frequency TEXT, -- Yedekleme sıklığı
                disaster_recovery_plan BOOLEAN DEFAULT 0, -- Afet kurtarma planı
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Dijital dönüşüm projeleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS digital_transformation_projects (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                project_name TEXT NOT NULL,
                project_type TEXT, -- AI, IoT, Cloud, Automation, Blockchain
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                budget REAL,
                status TEXT DEFAULT 'active', -- active, completed, cancelled
                roi_percentage REAL, -- Yatırım getirisi (%)
                digital_maturity_level TEXT, -- Başlangıç, Gelişen, Olgun, Lider
                sdg_mapping TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Siber güvenlik olayları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cybersecurity_incidents (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                incident_type TEXT NOT NULL, -- Malware, Phishing, DDoS, Data Breach
                severity TEXT NOT NULL, -- Low, Medium, High, Critical
                description TEXT,
                incident_date TEXT,
                resolution_date TEXT,
                impact_assessment TEXT,
                response_time_hours REAL,
                financial_impact REAL,
                lessons_learned TEXT,
                prevention_measures TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Dijital güvenlik eğitimleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cybersecurity_trainings (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                training_name TEXT NOT NULL,
                training_type TEXT, -- Awareness, Technical, Management
                participants_count INTEGER DEFAULT 0,
                training_hours REAL,
                completion_rate REAL, -- Tamamlanma oranı (%)
                effectiveness_score REAL, -- Etkinlik skoru (1-10)
                training_date TEXT,
                trainer TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    def add_digital_security_metrics(self, company_id: int, period: str,
                                    iso27001_certified: bool = False,
                                    cybersecurity_training_hours: float = 0,
                                    data_breach_count: int = 0,
                                    data_breach_severity: str = None,
                                    digital_transformation_budget: float = None,
                                    ai_applications_count: int = 0,
                                    cloud_adoption_percentage: float = None,
                                    automation_percentage: float = None,
                                    digital_literacy_score: float = None,
                                    cybersecurity_incidents: int = 0,
                                    incident_response_time: float = None,
                                    backup_frequency: str = None,
                                    disaster_recovery_plan: bool = False) -> int:
        """Dijital güvenlik metrikleri ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO digital_security_metrics 
            (company_id, period, iso27001_certified, cybersecurity_training_hours,
             data_breach_count, data_breach_severity, digital_transformation_budget,
             ai_applications_count, cloud_adoption_percentage, automation_percentage,
             digital_literacy_score, cybersecurity_incidents, incident_response_time,
             backup_frequency, disaster_recovery_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, period, iso27001_certified, cybersecurity_training_hours,
              data_breach_count, data_breach_severity, digital_transformation_budget,
              ai_applications_count, cloud_adoption_percentage, automation_percentage,
              digital_literacy_score, cybersecurity_incidents, incident_response_time,
              backup_frequency, disaster_recovery_plan))

        metric_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return metric_id

    def add_digital_transformation_project(self, company_id: int, project_name: str,
                                         project_type: str, description: str = None,
                                         start_date: str = None, end_date: str = None,
                                         budget: float = None, roi_percentage: float = None,
                                         digital_maturity_level: str = None,
                                         sdg_mapping: str = None) -> int:
        """Dijital dönüşüm projesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO digital_transformation_projects 
            (company_id, project_name, project_type, description,
             start_date, end_date, budget, roi_percentage, digital_maturity_level, sdg_mapping)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, project_name, project_type, description,
              start_date, end_date, budget, roi_percentage, digital_maturity_level, sdg_mapping))

        project_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return project_id

    def add_cybersecurity_incident(self, company_id: int, incident_type: str,
                                  severity: str, description: str = None,
                                  incident_date: str = None, resolution_date: str = None,
                                  impact_assessment: str = None, response_time_hours: float = None,
                                  financial_impact: float = None, lessons_learned: str = None,
                                  prevention_measures: str = None) -> int:
        """Siber güvenlik olayı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO cybersecurity_incidents 
            (company_id, incident_type, severity, description, incident_date,
             resolution_date, impact_assessment, response_time_hours, financial_impact,
             lessons_learned, prevention_measures)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, incident_type, severity, description, incident_date,
              resolution_date, impact_assessment, response_time_hours, financial_impact,
              lessons_learned, prevention_measures))

        incident_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return incident_id

    def add_cybersecurity_training(self, company_id: int, training_name: str,
                                  training_type: str, participants_count: int = 0,
                                  training_hours: float = 0, completion_rate: float = None,
                                  effectiveness_score: float = None, training_date: str = None,
                                  trainer: str = None) -> int:
        """Siber güvenlik eğitimi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO cybersecurity_trainings 
            (company_id, training_name, training_type, participants_count,
             training_hours, completion_rate, effectiveness_score, training_date, trainer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, training_name, training_type, participants_count,
              training_hours, completion_rate, effectiveness_score, training_date, trainer))

        training_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return training_id

    def get_digital_security_dashboard(self, company_id: int, period: str = None) -> Dict:
        """Dijital güvenlik dashboard verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Son dönem metrikleri
        if period:
            cursor.execute("""
                SELECT * FROM digital_security_metrics 
                WHERE company_id = ? AND period = ?
                ORDER BY created_at DESC LIMIT 1
            """, (company_id, period))
        else:
            cursor.execute("""
                SELECT * FROM digital_security_metrics 
                WHERE company_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (company_id,))

        metrics = cursor.fetchone()

        # Aktif dijital dönüşüm projeleri
        cursor.execute("""
            SELECT COUNT(*) FROM digital_transformation_projects 
            WHERE company_id = ? AND status = 'active'
        """, (company_id,))
        active_projects = cursor.fetchone()[0]

        # Son 12 aydaki siber güvenlik olayları
        cursor.execute("""
            SELECT COUNT(*) FROM cybersecurity_incidents 
            WHERE company_id = ? AND incident_date >= date('now', '-12 months')
        """, (company_id,))
        recent_incidents = cursor.fetchone()[0]

        # Toplam eğitim saatleri
        cursor.execute("""
            SELECT SUM(training_hours) FROM cybersecurity_trainings 
            WHERE company_id = ?
        """, (company_id,))
        total_training_hours = cursor.fetchone()[0] or 0

        conn.close()

        if metrics:
            return {
                'iso27001_certified': bool(metrics[3]),
                'cybersecurity_training_hours': metrics[4],
                'data_breach_count': metrics[5],
                'data_breach_severity': metrics[6],
                'digital_transformation_budget': metrics[7],
                'ai_applications_count': metrics[8],
                'cloud_adoption_percentage': metrics[9],
                'automation_percentage': metrics[10],
                'digital_literacy_score': metrics[11],
                'cybersecurity_incidents': metrics[12],
                'incident_response_time': metrics[13],
                'backup_frequency': metrics[14],
                'disaster_recovery_plan': bool(metrics[15]),
                'active_projects': active_projects,
                'recent_incidents': recent_incidents,
                'total_training_hours': total_training_hours
            }
        else:
            return {
                'iso27001_certified': False,
                'cybersecurity_training_hours': 0,
                'data_breach_count': 0,
                'data_breach_severity': None,
                'digital_transformation_budget': 0,
                'ai_applications_count': 0,
                'cloud_adoption_percentage': 0,
                'automation_percentage': 0,
                'digital_literacy_score': 0,
                'cybersecurity_incidents': 0,
                'incident_response_time': 0,
                'backup_frequency': None,
                'disaster_recovery_plan': False,
                'active_projects': active_projects,
                'recent_incidents': recent_incidents,
                'total_training_hours': total_training_hours
            }

    def get_digital_security_trends(self, company_id: int, years: int = 3) -> List[Dict]:
        """Dijital güvenlik trendlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT period, cybersecurity_training_hours, data_breach_count,
                   ai_applications_count, cloud_adoption_percentage, automation_percentage
            FROM digital_security_metrics 
            WHERE company_id = ?
            ORDER BY period DESC
            LIMIT ?
        """, (company_id, years))

        trends = []
        for row in cursor.fetchall():
            trends.append({
                'period': row[0],
                'cybersecurity_training_hours': row[1],
                'data_breach_count': row[2],
                'ai_applications_count': row[3],
                'cloud_adoption_percentage': row[4],
                'automation_percentage': row[5]
            })

        conn.close()
        return trends
