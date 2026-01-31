#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GDPR/KVKK Uyumluluk Modülü
Veri koruma ve gizlilik yönetimi
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict
from config.database import DB_PATH


class GDPRComplianceManager:
    """GDPR/KVKK uyumluluk yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """GDPR uyumluluk tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    subject_type TEXT NOT NULL,
                    identifier TEXT NOT NULL,
                    data_categories TEXT NOT NULL,
                    processing_purposes TEXT NOT NULL,
                    legal_basis TEXT NOT NULL,
                    consent_status TEXT,
                    retention_period TEXT,
                    data_source TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consent_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    consent_type TEXT NOT NULL,
                    consent_given TEXT NOT NULL,
                    consent_date TEXT NOT NULL,
                    withdrawal_date TEXT,
                    consent_method TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (subject_id) REFERENCES data_subjects(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_breaches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    breach_date TEXT NOT NULL,
                    discovery_date TEXT NOT NULL,
                    breach_type TEXT NOT NULL,
                    affected_data_categories TEXT NOT NULL,
                    affected_subjects_count INTEGER,
                    breach_description TEXT NOT NULL,
                    containment_measures TEXT,
                    notification_status TEXT DEFAULT 'pending',
                    regulatory_notification_date TEXT,
                    subject_notification_date TEXT,
                    resolution_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_processing_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    processing_activity TEXT NOT NULL,
                    data_categories TEXT NOT NULL,
                    processing_purposes TEXT NOT NULL,
                    legal_basis TEXT NOT NULL,
                    data_recipients TEXT,
                    third_country_transfers TEXT,
                    retention_period TEXT NOT NULL,
                    security_measures TEXT,
                    dpo_contact TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] GDPR uyumluluk modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] GDPR uyumluluk modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_data_subject(self, company_id: int, subject_type: str, identifier: str,
                        data_categories: str, processing_purposes: str, legal_basis: str,
                        consent_status: str = None, retention_period: str = None,
                        data_source: str = None) -> bool:
        """Veri sahibi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_subjects 
                (company_id, subject_type, identifier, data_categories, processing_purposes,
                 legal_basis, consent_status, retention_period, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, subject_type, identifier, data_categories, processing_purposes,
                  legal_basis, consent_status, retention_period, data_source))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Veri sahibi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def record_consent(self, company_id: int, subject_id: int, consent_type: str,
                      consent_given: bool, consent_method: str = None,
                      ip_address: str = None, user_agent: str = None) -> bool:
        """Onay kaydı oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            consent_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("""
                INSERT INTO consent_records 
                (company_id, subject_id, consent_type, consent_given, consent_date,
                 consent_method, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, subject_id, consent_type, str(consent_given).lower(),
                  consent_date, consent_method, ip_address, user_agent))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Onay kaydı oluşturma hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def report_data_breach(self, company_id: int, breach_date: str, discovery_date: str,
                          breach_type: str, affected_data_categories: str,
                          affected_subjects_count: int, breach_description: str,
                          containment_measures: str = None) -> bool:
        """Veri ihlali rapor et"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_breaches 
                (company_id, breach_date, discovery_date, breach_type, affected_data_categories,
                 affected_subjects_count, breach_description, containment_measures)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, breach_date, discovery_date, breach_type, affected_data_categories,
                  affected_subjects_count, breach_description, containment_measures))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Veri ihlali rapor etme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_data_processing_record(self, company_id: int, processing_activity: str,
                                 data_categories: str, processing_purposes: str,
                                 legal_basis: str, retention_period: str,
                                 data_recipients: str = None, third_country_transfers: str = None,
                                 security_measures: str = None, dpo_contact: str = None) -> bool:
        """Veri işleme kaydı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_processing_records 
                (company_id, processing_activity, data_categories, processing_purposes,
                 legal_basis, data_recipients, third_country_transfers, retention_period,
                 security_measures, dpo_contact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, processing_activity, data_categories, processing_purposes,
                  legal_basis, data_recipients, third_country_transfers, retention_period,
                  security_measures, dpo_contact))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Veri işleme kaydı ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_gdpr_compliance_summary(self, company_id: int) -> Dict:
        """GDPR uyumluluk özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Veri sahipleri
            cursor.execute("""
                SELECT subject_type, COUNT(*)
                FROM data_subjects 
                WHERE company_id = ?
                GROUP BY subject_type
            """, (company_id,))

            data_subjects_by_type = {}
            total_subjects = 0
            for row in cursor.fetchall():
                subject_type, count = row
                data_subjects_by_type[subject_type] = count
                total_subjects += count

            # Onay kayıtları
            cursor.execute("""
                SELECT consent_type, SUM(CASE WHEN consent_given = 'true' THEN 1 ELSE 0 END), COUNT(*)
                FROM consent_records 
                WHERE company_id = ?
                GROUP BY consent_type
            """, (company_id,))

            consent_summary = {}
            for row in cursor.fetchall():
                consent_type, given_count, total_count = row
                consent_summary[consent_type] = {
                    'given': given_count,
                    'total': total_count,
                    'rate': (given_count / total_count * 100) if total_count > 0 else 0
                }

            # Veri ihlalleri
            cursor.execute("""
                SELECT breach_type, COUNT(*), SUM(affected_subjects_count)
                FROM data_breaches 
                WHERE company_id = ?
                GROUP BY breach_type
            """, (company_id,))

            breach_summary = {}
            total_breaches = 0
            total_affected_subjects = 0
            for row in cursor.fetchall():
                breach_type, count, affected_subjects = row
                breach_summary[breach_type] = {
                    'count': count,
                    'affected_subjects': affected_subjects or 0
                }
                total_breaches += count
                total_affected_subjects += affected_subjects or 0

            # Veri işleme kayıtları
            cursor.execute("""
                SELECT COUNT(*)
                FROM data_processing_records 
                WHERE company_id = ?
            """, (company_id,))

            processing_records_count = cursor.fetchone()[0] or 0

            return {
                'data_subjects_by_type': data_subjects_by_type,
                'total_data_subjects': total_subjects,
                'consent_summary': consent_summary,
                'breach_summary': breach_summary,
                'total_breaches': total_breaches,
                'total_affected_subjects': total_affected_subjects,
                'processing_records_count': processing_records_count,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"GDPR uyumluluk özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()

    def generate_dpo_report(self, company_id: int, period_start: str, period_end: str) -> str:
        """DPO (Veri Koruma Sorumlusu) raporu oluştur"""
        summary = self.get_gdpr_compliance_summary(company_id)

        if not summary:
            return ""

        report = f"""# Veri Koruma Sorumlusu (DPO) Raporu
**Dönem:** {period_start} - {period_end}
**Şirket ID:** {company_id}

## Veri Sahipleri Özeti
- **Toplam Veri Sahibi:** {summary['total_data_subjects']}
"""

        for subject_type, count in summary['data_subjects_by_type'].items():
            report += f"- **{subject_type}:** {count}\n"

        report += """
## Onay Yönetimi
"""

        for consent_type, data in summary['consent_summary'].items():
            report += f"- **{consent_type}:** {data['given']}/{data['total']} (%{data['rate']:.1f})\n"

        report += f"""
## Veri İhlalleri
- **Toplam İhlal:** {summary['total_breaches']}
- **Etkilenen Veri Sahibi:** {summary['total_affected_subjects']}
"""

        for breach_type, data in summary['breach_summary'].items():
            report += f"- **{breach_type}:** {data['count']} ihlal, {data['affected_subjects']} etkilenen\n"

        report += f"""
## Veri İşleme Kayıtları
- **Toplam İşleme Kaydı:** {summary['processing_records_count']}

## Uyumluluk Durumu
Bu rapor, GDPR/KVKK uyumluluk durumunu özetlemektedir.
"""

        return report
