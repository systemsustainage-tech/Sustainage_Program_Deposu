#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KALİTE VE MÜŞTERİ MEMNUNİYETİ MODÜLÜ
- ISO 9001 ve kalite yönetim sistemleri
- Müşteri memnuniyet metrikleri
- Ürün kalite göstergeleri
- Kalite kontrol süreçleri
"""

import sqlite3
from typing import Dict, List


class QualityModule:
    """Kalite ve müşteri memnuniyeti yönetimi sınıfı"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def create_quality_tables(self) -> None:
        """Kalite tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Kalite metrikleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_metrics (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                period TEXT NOT NULL,
                iso9001_certified BOOLEAN DEFAULT 0, -- ISO 9001 sertifikası
                iso14001_certified BOOLEAN DEFAULT 0, -- ISO 14001 sertifikası
                iso45001_certified BOOLEAN DEFAULT 0, -- ISO 45001 sertifikası
                customer_complaint_rate REAL, -- Müşteri şikayet oranı (%)
                customer_complaint_count INTEGER DEFAULT 0, -- Şikayet sayısı
                product_recall_count INTEGER DEFAULT 0, -- Ürün geri çağırma sayısı
                nps_score REAL, -- Net Promoter Score
                customer_satisfaction_score REAL, -- Müşteri memnuniyet skoru (1-10)
                quality_error_rate REAL, -- Kalite kontrol hata oranı (%)
                defect_rate REAL, -- Defekt oranı (%)
                first_pass_yield REAL, -- İlk geçiş verimliliği (%)
                supplier_quality_score REAL, -- Tedarikçi kalite skoru (1-10)
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Kalite sertifikaları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_certifications (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                certification_type TEXT NOT NULL, -- ISO 9001, ISO 14001, vb.
                certification_body TEXT, -- Sertifika veren kuruluş
                certificate_number TEXT,
                issue_date TEXT,
                expiry_date TEXT,
                status TEXT DEFAULT 'active', -- active, expired, suspended
                scope TEXT, -- Sertifika kapsamı
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Müşteri anketleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_surveys (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                survey_name TEXT NOT NULL,
                survey_type TEXT, -- NPS, CSAT, CES
                survey_date TEXT,
                total_responses INTEGER DEFAULT 0,
                average_score REAL,
                promoter_percentage REAL, -- NPS için
                detractor_percentage REAL, -- NPS için
                passive_percentage REAL, -- NPS için
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Kalite iyileştirme projeleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_improvement_projects (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                project_name TEXT NOT NULL,
                project_type TEXT, -- Six Sigma, Lean, Kaizen, vb.
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT DEFAULT 'active', -- active, completed, cancelled
                cost_savings REAL, -- Maliyet tasarrufu
                quality_improvement REAL, -- Kalite iyileştirme oranı
                sdg_mapping TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    def add_quality_metrics(self, company_id: int, period: str,
                           iso9001_certified: bool = False,
                           iso14001_certified: bool = False,
                           iso45001_certified: bool = False,
                           customer_complaint_rate: float = None,
                           customer_complaint_count: int = 0,
                           product_recall_count: int = 0,
                           nps_score: float = None,
                           customer_satisfaction_score: float = None,
                           quality_error_rate: float = None,
                           defect_rate: float = None,
                           first_pass_yield: float = None,
                           supplier_quality_score: float = None) -> int:
        """Kalite metrikleri ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO quality_metrics 
            (company_id, period, iso9001_certified, iso14001_certified, iso45001_certified,
             customer_complaint_rate, customer_complaint_count, product_recall_count,
             nps_score, customer_satisfaction_score, quality_error_rate, defect_rate,
             first_pass_yield, supplier_quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, period, iso9001_certified, iso14001_certified, iso45001_certified,
              customer_complaint_rate, customer_complaint_count, product_recall_count,
              nps_score, customer_satisfaction_score, quality_error_rate, defect_rate,
              first_pass_yield, supplier_quality_score))

        metric_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return metric_id

    def add_certification(self, company_id: int, certification_type: str,
                         certification_body: str = None, certificate_number: str = None,
                         issue_date: str = None, expiry_date: str = None,
                         scope: str = None) -> int:
        """Kalite sertifikası ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO quality_certifications 
            (company_id, certification_type, certification_body, certificate_number,
             issue_date, expiry_date, scope)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (company_id, certification_type, certification_body, certificate_number,
              issue_date, expiry_date, scope))

        cert_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return cert_id

    def add_customer_survey(self, company_id: int, survey_name: str,
                           survey_type: str, survey_date: str,
                           total_responses: int = 0, average_score: float = None,
                           promoter_percentage: float = None,
                           detractor_percentage: float = None,
                           passive_percentage: float = None) -> int:
        """Müşteri anketi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO customer_surveys 
            (company_id, survey_name, survey_type, survey_date, total_responses,
             average_score, promoter_percentage, detractor_percentage, passive_percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (company_id, survey_name, survey_type, survey_date, total_responses,
              average_score, promoter_percentage, detractor_percentage, passive_percentage))

        survey_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return survey_id

    def get_quality_dashboard(self, company_id: int, period: str = None) -> Dict:
        """Kalite dashboard verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Son dönem metrikleri
        if period:
            cursor.execute("""
                SELECT * FROM quality_metrics 
                WHERE company_id = ? AND period = ?
                ORDER BY created_at DESC LIMIT 1
            """, (company_id, period))
        else:
            cursor.execute("""
                SELECT * FROM quality_metrics 
                WHERE company_id = ?
                ORDER BY created_at DESC LIMIT 1
            """, (company_id,))

        metrics = cursor.fetchone()

        # Aktif sertifikalar
        cursor.execute("""
            SELECT COUNT(*) FROM quality_certifications 
            WHERE company_id = ? AND status = 'active'
        """, (company_id,))
        active_certifications = cursor.fetchone()[0]

        # Son müşteri anketi
        cursor.execute("""
            SELECT average_score, nps_score FROM customer_surveys 
            WHERE company_id = ?
            ORDER BY survey_date DESC LIMIT 1
        """, (company_id,))
        latest_survey = cursor.fetchone()

        # Aktif iyileştirme projeleri
        cursor.execute("""
            SELECT COUNT(*) FROM quality_improvement_projects 
            WHERE company_id = ? AND status = 'active'
        """, (company_id,))
        active_projects = cursor.fetchone()[0]

        conn.close()

        if metrics:
            return {
                'iso9001_certified': bool(metrics[3]),
                'iso14001_certified': bool(metrics[4]),
                'iso45001_certified': bool(metrics[5]),
                'customer_complaint_rate': metrics[6],
                'customer_complaint_count': metrics[7],
                'product_recall_count': metrics[8],
                'nps_score': metrics[9],
                'customer_satisfaction_score': metrics[10],
                'quality_error_rate': metrics[11],
                'defect_rate': metrics[12],
                'first_pass_yield': metrics[13],
                'supplier_quality_score': metrics[14],
                'active_certifications': active_certifications,
                'latest_survey_score': latest_survey[0] if latest_survey else None,
                'latest_nps_score': latest_survey[1] if latest_survey else None,
                'active_projects': active_projects
            }
        else:
            return {
                'iso9001_certified': False,
                'iso14001_certified': False,
                'iso45001_certified': False,
                'customer_complaint_rate': 0,
                'customer_complaint_count': 0,
                'product_recall_count': 0,
                'nps_score': 0,
                'customer_satisfaction_score': 0,
                'quality_error_rate': 0,
                'defect_rate': 0,
                'first_pass_yield': 0,
                'supplier_quality_score': 0,
                'active_certifications': active_certifications,
                'latest_survey_score': None,
                'latest_nps_score': None,
                'active_projects': active_projects
            }

    def get_quality_trends(self, company_id: int, years: int = 3) -> List[Dict]:
        """Kalite trendlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT period, customer_complaint_rate, nps_score, 
                   customer_satisfaction_score, quality_error_rate, defect_rate
            FROM quality_metrics 
            WHERE company_id = ?
            ORDER BY period DESC
            LIMIT ?
        """, (company_id, years))

        trends = []
        for row in cursor.fetchall():
            trends.append({
                'period': row[0],
                'customer_complaint_rate': row[1],
                'nps_score': row[2],
                'customer_satisfaction_score': row[3],
                'quality_error_rate': row[4],
                'defect_rate': row[5]
            })

        conn.close()
        return trends
