#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACİL DURUM VE AFET YÖNETİMİ MODÜLÜ
- İş sürekliliği planları
- Risk değerlendirme matrisi
- Acil durum tatbikatları
- Kriz yönetim süreçleri
"""

import sqlite3
from typing import Dict, List


class EmergencyManagementModule:
    """Acil durum ve afet yönetimi sınıfı"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def create_emergency_management_tables(self) -> None:
        """Acil durum yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Acil durum metrikleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergency_metrics (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                period TEXT NOT NULL,
                business_continuity_plan BOOLEAN DEFAULT 0, -- İş sürekliliği planı
                emergency_response_team BOOLEAN DEFAULT 0, -- Acil durum ekibi
                risk_assessment_matrix BOOLEAN DEFAULT 0, -- Risk değerlendirme matrisi
                emergency_drills_count INTEGER DEFAULT 0, -- Acil durum tatbikat sayısı
                drill_participation_rate REAL, -- Tatbikat katılım oranı (%)
                insurance_coverage REAL, -- Sigorta kapsamı (TL)
                emergency_contacts_count INTEGER DEFAULT 0, -- Acil durum iletişim sayısı
                evacuation_plan BOOLEAN DEFAULT 0, -- Tahliye planı
                communication_plan BOOLEAN DEFAULT 0, -- İletişim planı
                backup_systems_count INTEGER DEFAULT 0, -- Yedek sistem sayısı
                recovery_time_objective REAL, -- Kurtarma süre hedefi (saat)
                maximum_tolerable_downtime REAL, -- Maksimum kabul edilebilir kesinti (saat)
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Risk değerlendirme tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_assessments (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                risk_category TEXT NOT NULL, -- Doğal, Teknolojik, İnsan, Finansal
                risk_description TEXT NOT NULL,
                probability_score INTEGER, -- Olasılık skoru (1-5)
                impact_score INTEGER, -- Etki skoru (1-5)
                risk_level TEXT, -- Düşük, Orta, Yüksek, Kritik
                mitigation_measures TEXT, -- Azaltma önlemleri
                responsible_person TEXT, -- Sorumlu kişi
                review_date TEXT, -- İnceleme tarihi
                status TEXT DEFAULT 'active', -- active, mitigated, closed
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Acil durum tatbikatları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergency_drills (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                drill_name TEXT NOT NULL,
                drill_type TEXT, -- Yangın, Deprem, Siber Saldırı, Kimyasal Sızıntı
                drill_date TEXT,
                participants_count INTEGER DEFAULT 0,
                duration_minutes INTEGER, -- Tatbikat süresi (dakika)
                success_rate REAL, -- Başarı oranı (%)
                lessons_learned TEXT, -- Öğrenilen dersler
                improvement_areas TEXT, -- İyileştirme alanları
                next_drill_date TEXT, -- Sonraki tatbikat tarihi
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Acil durum olayları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emergency_incidents (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                incident_type TEXT NOT NULL, -- Yangın, Deprem, Siber Saldırı, vb.
                severity TEXT NOT NULL, -- Düşük, Orta, Yüksek, Kritik
                incident_date TEXT,
                resolution_date TEXT,
                description TEXT,
                impact_assessment TEXT,
                response_time_minutes INTEGER, -- Müdahale süresi (dakika)
                financial_impact REAL, -- Mali etki (TL)
                lessons_learned TEXT,
                prevention_measures TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # İş sürekliliği planları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_continuity_plans (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                plan_name TEXT NOT NULL,
                plan_type TEXT, -- Genel, Departman, Kritik Süreç
                description TEXT,
                version TEXT,
                approval_date TEXT,
                review_date TEXT,
                status TEXT DEFAULT 'active', -- active, draft, archived
                critical_processes TEXT, -- Kritik süreçler (JSON)
                backup_procedures TEXT, -- Yedekleme prosedürleri
                communication_protocols TEXT, -- İletişim protokolleri
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    def add_emergency_metrics(self, company_id: int, period: str,
                             business_continuity_plan: bool = False,
                             emergency_response_team: bool = False,
                             risk_assessment_matrix: bool = False,
                             emergency_drills_count: int = 0,
                             drill_participation_rate: float = None,
                             insurance_coverage: float = None,
                             emergency_contacts_count: int = 0,
                             evacuation_plan: bool = False,
                             communication_plan: bool = False,
                             backup_systems_count: int = 0,
                             recovery_time_objective: float = None,
                             maximum_tolerable_downtime: float = None) -> int:
        """Acil durum metrikleri ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO emergency_metrics 
            (company_id, period, business_continuity_plan, emergency_response_team,
             risk_assessment_matrix, emergency_drills_count, drill_participation_rate,
             insurance_coverage, emergency_contacts_count, evacuation_plan,
             communication_plan, backup_systems_count, recovery_time_objective,
             maximum_tolerable_downtime)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, period, business_continuity_plan, emergency_response_team,
              risk_assessment_matrix, emergency_drills_count, drill_participation_rate,
              insurance_coverage, emergency_contacts_count, evacuation_plan,
              communication_plan, backup_systems_count, recovery_time_objective,
              maximum_tolerable_downtime))

        metric_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return metric_id

    def add_risk_assessment(self, company_id: int, risk_category: str,
                           risk_description: str, probability_score: int,
                           impact_score: int, mitigation_measures: str = None,
                           responsible_person: str = None, review_date: str = None) -> int:
        """Risk değerlendirmesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Risk seviyesini hesapla
        risk_score = probability_score * impact_score
        if risk_score <= 4:
            risk_level = "Düşük"
        elif risk_score <= 9:
            risk_level = "Orta"
        elif risk_score <= 16:
            risk_level = "Yüksek"
        else:
            risk_level = "Kritik"

        cursor.execute("""
            INSERT INTO risk_assessments 
            (company_id, risk_category, risk_description, probability_score,
             impact_score, risk_level, mitigation_measures, responsible_person, review_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, risk_category, risk_description, probability_score,
              impact_score, risk_level, mitigation_measures, responsible_person, review_date))

        risk_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return risk_id

    def add_emergency_drill(self, company_id: int, drill_name: str,
                           drill_type: str, drill_date: str,
                           participants_count: int = 0, duration_minutes: int = None,
                           success_rate: float = None, lessons_learned: str = None,
                           improvement_areas: str = None, next_drill_date: str = None) -> int:
        """Acil durum tatbikatı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO emergency_drills 
            (company_id, drill_name, drill_type, drill_date, participants_count,
             duration_minutes, success_rate, lessons_learned, improvement_areas, next_drill_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, drill_name, drill_type, drill_date, participants_count,
              duration_minutes, success_rate, lessons_learned, improvement_areas, next_drill_date))

        drill_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return drill_id

    def add_emergency_incident(self, company_id: int, incident_type: str,
                              severity: str, incident_date: str = None,
                              resolution_date: str = None, description: str = None,
                              impact_assessment: str = None, response_time_minutes: int = None,
                              financial_impact: float = None, lessons_learned: str = None,
                              prevention_measures: str = None) -> int:
        """Acil durum olayı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO emergency_incidents 
            (company_id, incident_type, severity, incident_date, resolution_date,
             description, impact_assessment, response_time_minutes, financial_impact,
             lessons_learned, prevention_measures)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, incident_type, severity, incident_date, resolution_date,
              description, impact_assessment, response_time_minutes, financial_impact,
              lessons_learned, prevention_measures))

        incident_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return incident_id

    def get_emergency_management_dashboard(self, company_id: int, period: str = None) -> Dict:
        """Acil durum yönetimi dashboard verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Son dönem metrikleri
        if period:
            cursor.execute("""
                SELECT * FROM emergency_metrics 
                WHERE company_id = ? AND period = ?
                ORDER BY created_at DESC LIMIT 1
            """, (company_id, period))
        else:
            cursor.execute("""
                SELECT * FROM emergency_metrics 
                WHERE company_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (company_id,))

        metrics = cursor.fetchone()

        # Aktif riskler
        cursor.execute("""
            SELECT COUNT(*) FROM risk_assessments 
            WHERE company_id = ? AND status = 'active'
        """, (company_id,))
        active_risks = cursor.fetchone()[0]

        # Yüksek riskli durumlar
        cursor.execute("""
            SELECT COUNT(*) FROM risk_assessments 
            WHERE company_id = ? AND risk_level IN ('Yüksek', 'Kritik')
        """, (company_id,))
        high_risks = cursor.fetchone()[0]

        # Son 12 aydaki tatbikatlar
        cursor.execute("""
            SELECT COUNT(*) FROM emergency_drills 
            WHERE company_id = ? AND drill_date >= date('now', '-12 months')
        """, (company_id,))
        recent_drills = cursor.fetchone()[0]

        # Son 12 aydaki olaylar
        cursor.execute("""
            SELECT COUNT(*) FROM emergency_incidents 
            WHERE company_id = ? AND incident_date >= date('now', '-12 months')
        """, (company_id,))
        recent_incidents = cursor.fetchone()[0]

        conn.close()

        if metrics:
            return {
                'business_continuity_plan': bool(metrics[3]),
                'emergency_response_team': bool(metrics[4]),
                'risk_assessment_matrix': bool(metrics[5]),
                'emergency_drills_count': metrics[6],
                'drill_participation_rate': metrics[7],
                'insurance_coverage': metrics[8],
                'emergency_contacts_count': metrics[9],
                'evacuation_plan': bool(metrics[10]),
                'communication_plan': bool(metrics[11]),
                'backup_systems_count': metrics[12],
                'recovery_time_objective': metrics[13],
                'maximum_tolerable_downtime': metrics[14],
                'active_risks': active_risks,
                'high_risks': high_risks,
                'recent_drills': recent_drills,
                'recent_incidents': recent_incidents
            }
        else:
            return {
                'business_continuity_plan': False,
                'emergency_response_team': False,
                'risk_assessment_matrix': False,
                'emergency_drills_count': 0,
                'drill_participation_rate': 0,
                'insurance_coverage': 0,
                'emergency_contacts_count': 0,
                'evacuation_plan': False,
                'communication_plan': False,
                'backup_systems_count': 0,
                'recovery_time_objective': 0,
                'maximum_tolerable_downtime': 0,
                'active_risks': active_risks,
                'high_risks': high_risks,
                'recent_drills': recent_drills,
                'recent_incidents': recent_incidents
            }

    def get_risk_matrix(self, company_id: int) -> List[Dict]:
        """Risk matrisini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT risk_category, risk_description, probability_score, impact_score,
                   risk_level, mitigation_measures, responsible_person, review_date
            FROM risk_assessments 
            WHERE company_id = ? AND status = 'active'
            ORDER BY (probability_score * impact_score) DESC
        """, (company_id,))

        risks = []
        for row in cursor.fetchall():
            risks.append({
                'risk_category': row[0],
                'risk_description': row[1],
                'probability_score': row[2],
                'impact_score': row[3],
                'risk_level': row[4],
                'mitigation_measures': row[5],
                'responsible_person': row[6],
                'review_date': row[7]
            })

        conn.close()
        return risks
