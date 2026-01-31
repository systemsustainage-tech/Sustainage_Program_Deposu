import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List
from config.database import DB_PATH


class ProductTechManager:
    """Ürün ve Teknoloji modülü yöneticisi - AR-GE, Kalite, Güvenlik, Acil Durum"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        # db_path göreli ise proje köküne göre mutlak hale getir
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    # AR-GE ve İnovasyon Metrikleri
    def save_innovation_metrics(self, company_id: int, rd_investment_ratio: float,
                               patent_applications: int, ecodesign_integration: bool,
                               lca_implementation: bool, innovation_budget: float,
                               reporting_period: str) -> bool:
        """İnovasyon metriklerini kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO innovation_metrics 
                (company_id, rd_investment_ratio, patent_applications, ecodesign_integration,
                 lca_implementation, innovation_budget, reporting_period, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, rd_investment_ratio, patent_applications, ecodesign_integration,
                  lca_implementation, innovation_budget, reporting_period, datetime.now().isoformat()))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"İnovasyon metrikleri kaydetme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_innovation_metrics(self, company_id: int) -> List[Dict]:
        """İnovasyon metriklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT rd_investment_ratio, patent_applications, ecodesign_integration,
                   lca_implementation, innovation_budget, reporting_period, created_date
            FROM innovation_metrics
            WHERE company_id = ?
            ORDER BY created_date DESC
        """, (company_id,))

        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'rd_investment_ratio': row[0],
                'patent_applications': row[1],
                'ecodesign_integration': bool(row[2]),
                'lca_implementation': bool(row[3]),
                'innovation_budget': row[4],
                'reporting_period': row[5],
                'created_date': row[6]
            })

        conn.close()
        return metrics

    # Kalite Metrikleri
    def save_quality_metrics(self, company_id: int, iso9001_certified: bool,
                            customer_complaint_rate: float, product_recall_count: int,
                            nps_score: float, quality_error_rate: float,
                            reporting_period: str) -> bool:
        """Kalite metriklerini kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO quality_metrics 
                (company_id, iso9001_certified, customer_complaint_rate, product_recall_count,
                 nps_score, quality_error_rate, reporting_period, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, iso9001_certified, customer_complaint_rate, product_recall_count,
                  nps_score, quality_error_rate, reporting_period, datetime.now().isoformat()))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Kalite metrikleri kaydetme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_quality_metrics(self, company_id: int) -> List[Dict]:
        """Kalite metriklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT iso9001_certified, customer_complaint_rate, product_recall_count,
                   nps_score, quality_error_rate, reporting_period, created_date
            FROM quality_metrics
            WHERE company_id = ?
            ORDER BY created_date DESC
        """, (company_id,))

        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'iso9001_certified': bool(row[0]),
                'customer_complaint_rate': row[1],
                'product_recall_count': row[2],
                'nps_score': row[3],
                'quality_error_rate': row[4],
                'reporting_period': row[5],
                'created_date': row[6]
            })

        conn.close()
        return metrics

    # Dijital Güvenlik Metrikleri
    def save_digital_security_metrics(self, company_id: int, iso27001_certified: bool,
                                     cybersecurity_training_hours: int, data_breach_count: int,
                                     digital_transformation_score: float, ai_applications_count: int,
                                     reporting_period: str) -> bool:
        """Dijital güvenlik metriklerini kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO digital_security_metrics 
                (company_id, iso27001_certified, cybersecurity_training_hours, data_breach_count,
                 digital_transformation_score, ai_applications_count, reporting_period, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, iso27001_certified, cybersecurity_training_hours, data_breach_count,
                  digital_transformation_score, ai_applications_count, reporting_period, datetime.now().isoformat()))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Dijital güvenlik metrikleri kaydetme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_digital_security_metrics(self, company_id: int) -> List[Dict]:
        """Dijital güvenlik metriklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT iso27001_certified, cybersecurity_training_hours, data_breach_count,
                   digital_transformation_score, ai_applications_count, reporting_period, created_date
            FROM digital_security_metrics
            WHERE company_id = ?
            ORDER BY created_date DESC
        """, (company_id,))

        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'iso27001_certified': bool(row[0]),
                'cybersecurity_training_hours': row[1],
                'data_breach_count': row[2],
                'digital_transformation_score': row[3],
                'ai_applications_count': row[4],
                'reporting_period': row[5],
                'created_date': row[6]
            })

        conn.close()
        return metrics

    # Acil Durum Yönetimi Metrikleri
    def save_emergency_metrics(self, company_id: int, business_continuity_plan: bool,
                              emergency_drill_frequency: int, risk_assessment_score: float,
                              crisis_management_team: bool, insurance_coverage_score: float,
                              reporting_period: str) -> bool:
        """Acil durum metriklerini kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO emergency_metrics 
                (company_id, business_continuity_plan, emergency_drill_frequency, risk_assessment_score,
                 crisis_management_team, insurance_coverage_score, reporting_period, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, business_continuity_plan, emergency_drill_frequency, risk_assessment_score,
                  crisis_management_team, insurance_coverage_score, reporting_period, datetime.now().isoformat()))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Acil durum metrikleri kaydetme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_emergency_metrics(self, company_id: int) -> List[Dict]:
        """Acil durum metriklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT business_continuity_plan, emergency_drill_frequency, risk_assessment_score,
                   crisis_management_team, insurance_coverage_score, reporting_period, created_date
            FROM emergency_metrics
            WHERE company_id = ?
            ORDER BY created_date DESC
        """, (company_id,))

        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'business_continuity_plan': bool(row[0]),
                'emergency_drill_frequency': row[1],
                'risk_assessment_score': row[2],
                'crisis_management_team': bool(row[3]),
                'insurance_coverage_score': row[4],
                'reporting_period': row[5],
                'created_date': row[6]
            })

        conn.close()
        return metrics

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
