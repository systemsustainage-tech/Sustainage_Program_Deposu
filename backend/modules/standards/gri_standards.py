#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Standartları Modülü
GRI 1, 2, 3 ve İçerik İndeksi yönetimi
"""

import logging
import os
import sqlite3
from typing import Dict
from config.database import DB_PATH


class GRIStandardsManager:
    """GRI Standartları yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()
        self._upgrade_schema()

    def _init_db_tables(self) -> None:
        """GRI standartları tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # GRI 1 - Temel Gereksinimler
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_1_foundation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    reporting_frequency TEXT NOT NULL,
                    reporting_boundary TEXT NOT NULL,
                    contact_information TEXT,
                    external_assurance TEXT,
                    statement_of_use TEXT,
                    assurance_provider TEXT,
                    assurance_standard TEXT,
                    assurance_scope TEXT,
                    assurance_date TEXT,
                    stakeholder_engagement TEXT,
                    material_topics TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # GRI 2 - Genel Açıklamalar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_2_general_disclosures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    disclosure_number TEXT NOT NULL,
                    disclosure_title TEXT NOT NULL,
                    disclosure_content TEXT NOT NULL,
                    reporting_status TEXT NOT NULL,
                    page_number INTEGER,
                    omission_reason TEXT,
                    data_quality TEXT,
                    external_verification TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # GRI 3 - İçerik İndeksi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_3_content_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    gri_standard TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    disclosure_number TEXT NOT NULL,
                    page_number INTEGER,
                    omission_reason TEXT,
                    reporting_status TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Materiality Assessment
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_materiality_assessment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assessment_year INTEGER NOT NULL,
                    topic_name TEXT NOT NULL,
                    topic_category TEXT NOT NULL,
                    stakeholder_importance_score REAL,
                    business_impact_score REAL,
                    materiality_level TEXT NOT NULL,
                    reporting_boundary TEXT,
                    management_approach TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] GRI standartlari modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] GRI standartlari modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def _upgrade_schema(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(gri_1_foundation)")
            cols = [row[1] for row in cursor.fetchall()]
            if 'statement_of_use' not in cols:
                cursor.execute("ALTER TABLE gri_1_foundation ADD COLUMN statement_of_use TEXT")
            if 'assurance_provider' not in cols:
                cursor.execute("ALTER TABLE gri_1_foundation ADD COLUMN assurance_provider TEXT")
            if 'assurance_standard' not in cols:
                cursor.execute("ALTER TABLE gri_1_foundation ADD COLUMN assurance_standard TEXT")
            if 'assurance_scope' not in cols:
                cursor.execute("ALTER TABLE gri_1_foundation ADD COLUMN assurance_scope TEXT")
            if 'assurance_date' not in cols:
                cursor.execute("ALTER TABLE gri_1_foundation ADD COLUMN assurance_date TEXT")

            cursor.execute("PRAGMA table_info(gri_2_general_disclosures)")
            c2_cols = [row[1] for row in cursor.fetchall()]
            if 'page_number' not in c2_cols:
                cursor.execute("ALTER TABLE gri_2_general_disclosures ADD COLUMN page_number INTEGER")
            if 'omission_reason' not in c2_cols:
                cursor.execute("ALTER TABLE gri_2_general_disclosures ADD COLUMN omission_reason TEXT")

            cursor.execute("PRAGMA table_info(gri_3_content_index)")
            c3_cols = [row[1] for row in cursor.fetchall()]
            if 'omission_reason' not in c3_cols:
                cursor.execute("ALTER TABLE gri_3_content_index ADD COLUMN omission_reason TEXT")
            # Migrate legacy 'ommission_reason' if exists
            cursor.execute("PRAGMA table_info(gri_3_content_index)")
            c3_cols2 = [row[1] for row in cursor.fetchall()]
            if 'ommission_reason' in c3_cols2:
                cursor.execute("UPDATE gri_3_content_index SET omission_reason = ommission_reason WHERE omission_reason IS NULL")
            conn.commit()
        except Exception:
            conn.rollback()
        finally:
            conn.close()

    def add_gri_1_foundation(self, company_id: int, reporting_period: str,
                           reporting_frequency: str, reporting_boundary: str,
                           contact_information: str = None, external_assurance: str = None,
                           stakeholder_engagement: str = None, material_topics: str = None,
                           statement_of_use: str = None, assurance_provider: str = None,
                           assurance_standard: str = None, assurance_scope: str = None,
                           assurance_date: str = None) -> bool:
        """GRI 1 temel gereksinimler ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO gri_1_foundation 
                (company_id, reporting_period, reporting_frequency, reporting_boundary,
                 contact_information, external_assurance, statement_of_use,
                 assurance_provider, assurance_standard, assurance_scope, assurance_date,
                 stakeholder_engagement, material_topics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, reporting_period, reporting_frequency, reporting_boundary,
                  contact_information, external_assurance, statement_of_use,
                  assurance_provider, assurance_standard, assurance_scope, assurance_date,
                  stakeholder_engagement, material_topics))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"GRI 1 temel gereksinimler ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_gri_2_disclosure(self, company_id: int, reporting_period: str,
                           disclosure_number: str, disclosure_title: str,
                           disclosure_content: str, reporting_status: str,
                           page_number: int = None, omission_reason: str = None,
                           data_quality: str = None, external_verification: str = None) -> bool:
        """GRI 2 genel açıklama ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO gri_2_general_disclosures 
                (company_id, reporting_period, disclosure_number, disclosure_title,
                 disclosure_content, reporting_status, page_number, omission_reason,
                 data_quality, external_verification)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, reporting_period, disclosure_number, disclosure_title,
                  disclosure_content, reporting_status, page_number, omission_reason,
                  data_quality, external_verification))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"GRI 2 genel açıklama ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_gri_3_content_index(self, company_id: int, reporting_period: str,
                              gri_standard: str, topic: str, disclosure_number: str,
                              page_number: int = None, omission_reason: str = None,
                              reporting_status: str = "Reported") -> bool:
        """GRI 3 içerik indeksi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO gri_3_content_index 
                (company_id, reporting_period, gri_standard, topic, disclosure_number,
                 page_number, omission_reason, reporting_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, reporting_period, gri_standard, topic, disclosure_number,
                  page_number, omission_reason, reporting_status))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"GRI 3 içerik indeksi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_materiality_assessment(self, company_id: int, assessment_year: int,
                                 topic_name: str, topic_category: str,
                                 stakeholder_importance_score: float,
                                 business_impact_score: float, materiality_level: str,
                                 reporting_boundary: str = None, management_approach: str = None) -> bool:
        """Materialite değerlendirmesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO gri_materiality_assessment 
                (company_id, assessment_year, topic_name, topic_category,
                 stakeholder_importance_score, business_impact_score, materiality_level,
                 reporting_boundary, management_approach)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, assessment_year, topic_name, topic_category,
                  stakeholder_importance_score, business_impact_score, materiality_level,
                  reporting_boundary, management_approach))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Materialite değerlendirmesi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_gri_reporting_status(self, company_id: int, reporting_period: str) -> Dict:
        """GRI raporlama durumu getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # GRI 1 Foundation
            cursor.execute("""
                SELECT reporting_frequency, reporting_boundary, external_assurance,
                       stakeholder_engagement, statement_of_use, assurance_provider,
                       assurance_standard, assurance_scope, assurance_date
                FROM gri_1_foundation 
                WHERE company_id = ? AND reporting_period = ? AND status = 'active'
            """, (company_id, reporting_period))

            gri_1_result = cursor.fetchone()
            gri_1_foundation = {}
            if gri_1_result:
                gri_1_foundation = {
                    'reporting_frequency': gri_1_result[0],
                    'reporting_boundary': gri_1_result[1],
                    'external_assurance': gri_1_result[2],
                    'stakeholder_engagement': gri_1_result[3],
                    'statement_of_use': gri_1_result[4],
                    'assurance_provider': gri_1_result[5],
                    'assurance_standard': gri_1_result[6],
                    'assurance_scope': gri_1_result[7],
                    'assurance_date': gri_1_result[8]
                }

            # GRI 2 Disclosures
            cursor.execute("""
                SELECT disclosure_number, disclosure_title, reporting_status, page_number, omission_reason
                FROM gri_2_general_disclosures 
                WHERE company_id = ? AND reporting_period = ?
                ORDER BY disclosure_number
            """, (company_id, reporting_period))

            gri_2_disclosures = {}
            for row in cursor.fetchall():
                disclosure_number, title, status, page_number, omission_reason = row
                gri_2_disclosures[disclosure_number] = {
                    'title': title,
                    'status': status,
                    'page_number': page_number,
                    'omission_reason': omission_reason
                }

            # GRI 3 Content Index
            cursor.execute("""
                SELECT gri_standard, topic, disclosure_number, page_number, reporting_status, omission_reason
                FROM gri_3_content_index 
                WHERE company_id = ? AND reporting_period = ?
                ORDER BY gri_standard, disclosure_number
            """, (company_id, reporting_period))

            gri_3_content_index = {}
            reported_count = 0
            omitted_count = 0
            for row in cursor.fetchall():
                standard, topic, disclosure, page_number, status, omission = row
                if standard not in gri_3_content_index:
                    gri_3_content_index[standard] = []

                gri_3_content_index[standard].append({
                    'topic': topic,
                    'disclosure': disclosure,
                    'page_number': page_number,
                    'status': status,
                    'omission_reason': omission
                })

                if status == 'Reported':
                    reported_count += 1
                elif status == 'Omitted':
                    omitted_count += 1

            # Materiality Assessment
            cursor.execute("""
                SELECT topic_name, topic_category, stakeholder_importance_score,
                       business_impact_score, materiality_level
                FROM gri_materiality_assessment 
                WHERE company_id = ? AND assessment_year = ?
                ORDER BY materiality_level DESC, stakeholder_importance_score DESC
            """, (company_id, reporting_period.split('-')[0]))

            materiality_topics = []
            for row in cursor.fetchall():
                topic_name, category, stakeholder_score, business_score, level = row
                materiality_topics.append({
                    'topic_name': topic_name,
                    'topic_category': category,
                    'stakeholder_importance_score': stakeholder_score,
                    'business_impact_score': business_score,
                    'materiality_level': level
                })

            return {
                'gri_1_foundation': gri_1_foundation,
                'gri_2_disclosures': gri_2_disclosures,
                'gri_3_content_index': gri_3_content_index,
                'reported_disclosures': reported_count,
                'omitted_disclosures': omitted_count,
                'materiality_topics': materiality_topics,
                'reporting_period': reporting_period,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"GRI raporlama durumu getirme hatası: {e}")
            return {}
        finally:
            conn.close()

    def generate_gri_content_index(self, company_id: int, reporting_period: str) -> str:
        """GRI İçerik İndeksi oluştur"""
        status = self.get_gri_reporting_status(company_id, reporting_period)

        if not status:
            return ""

        content_index = f"# GRI İçerik İndeksi - {reporting_period}\n\n"
        if status.get('gri_1_foundation'):
            fnd = status['gri_1_foundation']
            content_index += "## GRI 1: Foundation Özeti\n\n"
            content_index += f"- Statement of Use: {fnd.get('statement_of_use', '')}\n"
            content_index += f"- External Assurance: {fnd.get('external_assurance', '')}\n"
            ap = fnd.get('assurance_provider', '')
            ast = fnd.get('assurance_standard', '')
            asc = fnd.get('assurance_scope', '')
            ad = fnd.get('assurance_date', '')
            if any([ap, ast, asc, ad]):
                content_index += f"- Assurance Provider: {ap}\n"
                content_index += f"- Assurance Standard: {ast}\n"
                content_index += f"- Assurance Scope: {asc}\n"
                content_index += f"- Assurance Date: {ad}\n"
            content_index += "\n"

        # GRI 2 Genel Açıklamalar
        content_index += "## GRI 2: Genel Açıklamalar\n\n"
        content_index += "| Açıklama No | Açıklama Başlığı | Sayfa | Durum |\n"
        content_index += "|-------------|------------------|-------|-------|\n"

        for disclosure_number, disclosure_data in status['gri_2_disclosures'].items():
            page = disclosure_data.get('page_number') if disclosure_data.get('page_number') is not None else 'TBD'
            omission_reason = disclosure_data.get('omission_reason', '')
            content_index += f"| {disclosure_number} | {disclosure_data['title']} | {page} | {disclosure_data['status']} |\n"
            if disclosure_data['status'] == 'Omitted' and omission_reason:
                content_index += f"> Omission Reason: {omission_reason}\n"

        content_index += "\n"

        # GRI 3 Topic-specific Standards
        content_index += "## GRI 3: Konuya Özel Standartlar\n\n"

        for standard, disclosures in status['gri_3_content_index'].items():
            content_index += f"### {standard}\n\n"
            content_index += "| Konu | Açıklama No | Sayfa | Durum | Eksiklik Nedeni |\n"
            content_index += "|------|-------------|-------|-------|------------------|\n"

            for disclosure in disclosures:
                page = disclosure.get('page_number') if disclosure.get('page_number') is not None else 'TBD'
                omission_reason = disclosure.get('omission_reason', '')
                content_index += f"| {disclosure['topic']} | {disclosure['disclosure']} | {page} | {disclosure['status']} | {omission_reason} |\n"

            content_index += "\n"

        return content_index
