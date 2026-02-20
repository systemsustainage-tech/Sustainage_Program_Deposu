import logging
import os
from datetime import datetime
from typing import Dict, List
from config.database import DB_PATH
from backend.core.base_manager import BaseTenantManager


class ProductTechManager(BaseTenantManager):
    """Ürün ve Teknoloji modülü yöneticisi - AR-GE, Kalite, Güvenlik, Acil Durum"""

    def __init__(self, db_path: str = DB_PATH, company_id: int = None) -> None:
        # db_path göreli ise proje köküne göre mutlak hale getir
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            db_path = os.path.join(base_dir, db_path)
        super().__init__(db_path, company_id)
        self.create_tables()

    def create_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        try:
            # İnovasyon metrikleri tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS innovation_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    rd_investment_ratio REAL,
                    patent_applications INTEGER DEFAULT 0,
                    ecodesign_integration BOOLEAN DEFAULT 0,
                    lca_implementation BOOLEAN DEFAULT 0,
                    innovation_budget REAL,
                    reporting_period TEXT,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)

            # Kalite metrikleri tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    iso9001_certified BOOLEAN DEFAULT 0,
                    customer_satisfaction_score REAL,
                    defect_rate REAL,
                    supplier_quality_score REAL,
                    reporting_period TEXT,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)

            # Dijital güvenlik metrikleri tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS digital_security_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    iso27001_certified BOOLEAN DEFAULT 0,
                    cybersecurity_training_hours REAL,
                    data_breach_count INTEGER DEFAULT 0,
                    digital_transformation_budget REAL,
                    reporting_period TEXT,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)

            # Acil durum metrikleri tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS emergency_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    business_continuity_plan BOOLEAN DEFAULT 0,
                    emergency_drill_frequency INTEGER DEFAULT 0,
                    risk_assessment_score REAL,
                    crisis_management_team BOOLEAN DEFAULT 0,
                    insurance_coverage_score REAL,
                    reporting_period TEXT,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)

            logging.info("[OK] Product Technology tabloları oluşturuldu")

        except Exception as e:
            logging.error(f"[HATA] Product Technology tablo oluşturma hatası: {e}")

    # AR-GE ve İnovasyon Metrikleri
    def save_innovation_metrics(self, company_id: int, rd_investment_ratio: float,
                               patent_applications: int, ecodesign_integration: bool,
                               lca_implementation: bool, innovation_budget: float,
                               reporting_period: str) -> bool:
        """İnovasyon metriklerini kaydet"""
        try:
            self.execute_update("""
                INSERT OR REPLACE INTO innovation_metrics 
                (company_id, rd_investment_ratio, patent_applications, ecodesign_integration,
                 lca_implementation, innovation_budget, reporting_period, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, rd_investment_ratio, patent_applications, ecodesign_integration,
                  lca_implementation, innovation_budget, reporting_period, datetime.now().isoformat()),
            company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"İnovasyon metrikleri kaydetme hatası: {e}")
            return False

    def get_innovation_metrics(self, company_id: int) -> List[Dict]:
        """İnovasyon metriklerini getir"""
        try:
            rows = self.execute_query("""
                SELECT rd_investment_ratio, patent_applications, ecodesign_integration,
                       lca_implementation, innovation_budget, reporting_period, created_date
                FROM innovation_metrics
                WHERE company_id = ?
                ORDER BY created_date DESC
            """, (company_id,), company_id=company_id)

            metrics = []
            for row in rows:
                metrics.append({
                    'rd_investment_ratio': row['rd_investment_ratio'],
                    'patent_applications': row['patent_applications'],
                    'ecodesign_integration': bool(row['ecodesign_integration']),
                    'lca_implementation': bool(row['lca_implementation']),
                    'innovation_budget': row['innovation_budget'],
                    'reporting_period': row['reporting_period'],
                    'created_date': row['created_date']
                })
            return metrics
        except Exception as e:
            logging.error(f"İnovasyon metrikleri getirme hatası: {e}")
            return []

    # Kalite Metrikleri
    def save_quality_metrics(self, company_id: int, iso9001_certified: bool,
                            customer_complaint_rate: float, product_recall_count: int,
                            nps_score: float, quality_error_rate: float,
                            reporting_period: str) -> bool:
        """Kalite metriklerini kaydet"""
        try:
            self.execute_update("""
                INSERT OR REPLACE INTO quality_metrics 
                (company_id, iso9001_certified, customer_complaint_rate, product_recall_count,
                 nps_score, quality_error_rate, reporting_period, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, iso9001_certified, customer_complaint_rate, product_recall_count,
                  nps_score, quality_error_rate, reporting_period, datetime.now().isoformat()),
            company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"Kalite metrikleri kaydetme hatası: {e}")
            return False

    def get_quality_metrics(self, company_id: int) -> List[Dict]:
        """Kalite metriklerini getir"""
        try:
            rows = self.execute_query("""
                SELECT iso9001_certified, customer_complaint_rate, product_recall_count,
                       nps_score, quality_error_rate, reporting_period, created_date
                FROM quality_metrics
                WHERE company_id = ?
                ORDER BY created_date DESC
            """, (company_id,), company_id=company_id)

            metrics = []
            for row in rows:
                metrics.append({
                    'iso9001_certified': bool(row['iso9001_certified']),
                    'customer_complaint_rate': row['customer_complaint_rate'],
                    'product_recall_count': row['product_recall_count'],
                    'nps_score': row['nps_score'],
                    'quality_error_rate': row['quality_error_rate'],
                    'reporting_period': row['reporting_period'],
                    'created_date': row['created_date']
                })
            return metrics
        except Exception as e:
            logging.error(f"Kalite metrikleri getirme hatası: {e}")
            return []

    # Dijital Güvenlik Metrikleri
    def save_digital_security_metrics(self, company_id: int, iso27001_certified: bool,
                                     cybersecurity_training_hours: int, data_breach_count: int,
                                     digital_transformation_score: float, ai_applications_count: int,
                                     reporting_period: str) -> bool:
        """Dijital güvenlik metriklerini kaydet"""
        try:
            self.execute_update("""
                INSERT OR REPLACE INTO digital_security_metrics 
                (company_id, iso27001_certified, cybersecurity_training_hours, data_breach_count,
                 digital_transformation_score, ai_applications_count, reporting_period, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, iso27001_certified, cybersecurity_training_hours, data_breach_count,
                  digital_transformation_score, ai_applications_count, reporting_period, datetime.now().isoformat()),
            company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"Dijital güvenlik metrikleri kaydetme hatası: {e}")
            return False

    def get_digital_security_metrics(self, company_id: int) -> List[Dict]:
        """Dijital güvenlik metriklerini getir"""
        try:
            rows = self.execute_query("""
                SELECT iso27001_certified, cybersecurity_training_hours, data_breach_count,
                       digital_transformation_score, ai_applications_count, reporting_period, created_date
                FROM digital_security_metrics
                WHERE company_id = ?
                ORDER BY created_date DESC
            """, (company_id,), company_id=company_id)

            metrics = []
            for row in rows:
                metrics.append({
                    'iso27001_certified': bool(row['iso27001_certified']),
                    'cybersecurity_training_hours': row['cybersecurity_training_hours'],
                    'data_breach_count': row['data_breach_count'],
                    'digital_transformation_score': row['digital_transformation_score'],
                    'ai_applications_count': row['ai_applications_count'],
                    'reporting_period': row['reporting_period'],
                    'created_date': row['created_date']
                })
            return metrics
        except Exception as e:
            logging.error(f"Dijital güvenlik metrikleri getirme hatası: {e}")
            return []

    # Acil Durum Yönetimi Metrikleri
    def save_emergency_metrics(self, company_id: int, business_continuity_plan: bool,
                              emergency_drill_frequency: int, risk_assessment_score: float,
                              crisis_management_team: bool, insurance_coverage_score: float,
                              reporting_period: str) -> bool:
        """Acil durum metriklerini kaydet"""
        try:
            self.execute_update("""
                INSERT OR REPLACE INTO emergency_metrics 
                (company_id, business_continuity_plan, emergency_drill_frequency, risk_assessment_score,
                 crisis_management_team, insurance_coverage_score, reporting_period, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, business_continuity_plan, emergency_drill_frequency, risk_assessment_score,
                  crisis_management_team, insurance_coverage_score, reporting_period, datetime.now().isoformat()),
            company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"Acil durum metrikleri kaydetme hatası: {e}")
            return False

    def get_emergency_metrics(self, company_id: int) -> List[Dict]:
        """Acil durum metriklerini getir"""
        try:
            rows = self.execute_query("""
                SELECT business_continuity_plan, emergency_drill_frequency, risk_assessment_score,
                       crisis_management_team, insurance_coverage_score, reporting_period, created_date
                FROM emergency_metrics
                WHERE company_id = ?
                ORDER BY created_date DESC
            """, (company_id,), company_id=company_id)

            metrics = []
            for row in rows:
                metrics.append({
                    'business_continuity_plan': bool(row['business_continuity_plan']),
                    'emergency_drill_frequency': row['emergency_drill_frequency'],
                    'risk_assessment_score': row['risk_assessment_score'],
                    'crisis_management_team': bool(row['crisis_management_team']),
                    'insurance_coverage_score': row['insurance_coverage_score'],
                    'reporting_period': row['reporting_period'],
                    'created_date': row['created_date']
                })
            return metrics
        except Exception as e:
            logging.error(f"Acil durum metrikleri getirme hatası: {e}")
            return []

    def get_all_metrics_summary(self, company_id: int) -> Dict:
        """Tüm metriklerin özetini getir"""
        innovation = self.get_innovation_metrics(company_id)
        quality = self.get_quality_metrics(company_id)
        security = self.get_digital_security_metrics(company_id)
        emergency = self.get_emergency_metrics(company_id)

        return {
            'innovation': innovation[0] if innovation else {},
            'quality': quality[0] if quality else {},
            'security': security[0] if security else {},
            'emergency': emergency[0] if emergency else {},
            'has_data': bool(innovation or quality or security or emergency)
        }
