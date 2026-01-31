#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS/ESRS Modülü
Çift Önemlendirme, ESRS gereklilikleri, AB Taksonomisi
"""

import logging
import os
import sqlite3
from typing import Dict
from config.database import DB_PATH


class TSRSESRSManager:
    """TSRS/ESRS ve AB Taksonomisi yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """TSRS/ESRS tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Çift Önemlendirme Matrisi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS double_materiality_assessment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assessment_year INTEGER NOT NULL,
                    topic_name TEXT NOT NULL,
                    impact_materiality_score REAL,
                    financial_materiality_score REAL,
                    double_materiality_level TEXT NOT NULL,
                    esrs_relevance TEXT,
                    stakeholder_impact TEXT,
                    business_impact TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # ESRS Gereklilikleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS esrs_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    esrs_standard TEXT NOT NULL,
                    requirement_number TEXT NOT NULL,
                    requirement_title TEXT NOT NULL,
                    compliance_status TEXT NOT NULL,
                    reporting_content TEXT,
                    data_sources TEXT,
                    assurance_status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # AB Taksonomisi Uyumluluk
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS eu_taxonomy_compliance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_period TEXT NOT NULL,
                    economic_activity TEXT NOT NULL,
                    taxonomy_code TEXT NOT NULL,
                    alignment_percentage REAL,
                    turnover_share REAL,
                    capex_share REAL,
                    opex_share REAL,
                    nfrd_requirement TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Sürdürülebilirlik Hedefleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sustainability_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_category TEXT NOT NULL,
                    target_name TEXT NOT NULL,
                    baseline_year INTEGER,
                    baseline_value REAL,
                    target_value REAL,
                    target_unit TEXT,
                    achievement_status TEXT,
                    progress_percentage REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] TSRS/ESRS modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] TSRS/ESRS modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_double_materiality_assessment(self, company_id: int, assessment_year: int,
                                        topic_name: str, impact_materiality_score: float,
                                        financial_materiality_score: float,
                                        double_materiality_level: str,
                                        esrs_relevance: str = None,
                                        stakeholder_impact: str = None,
                                        business_impact: str = None) -> bool:
        """Çift önemlendirme değerlendirmesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO double_materiality_assessment 
                (company_id, assessment_year, topic_name, impact_materiality_score,
                 financial_materiality_score, double_materiality_level, esrs_relevance,
                 stakeholder_impact, business_impact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, assessment_year, topic_name, impact_materiality_score,
                  financial_materiality_score, double_materiality_level, esrs_relevance,
                  stakeholder_impact, business_impact))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Çift önemlendirme değerlendirmesi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_esrs_requirement(self, company_id: int, reporting_period: str,
                           esrs_standard: str, requirement_number: str,
                           requirement_title: str, compliance_status: str,
                           reporting_content: str = None, data_sources: str = None,
                           assurance_status: str = None) -> bool:
        """ESRS gereklilik ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO esrs_requirements 
                (company_id, reporting_period, esrs_standard, requirement_number,
                 requirement_title, compliance_status, reporting_content, data_sources, assurance_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, reporting_period, esrs_standard, requirement_number,
                  requirement_title, compliance_status, reporting_content, data_sources, assurance_status))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"ESRS gereklilik ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_eu_taxonomy_compliance(self, company_id: int, reporting_period: str,
                                 economic_activity: str, taxonomy_code: str,
                                 alignment_percentage: float, turnover_share: float = None,
                                 capex_share: float = None, opex_share: float = None,
                                 nfrd_requirement: str = None) -> bool:
        """AB Taksonomisi uyumluluk ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO eu_taxonomy_compliance 
                (company_id, reporting_period, economic_activity, taxonomy_code,
                 alignment_percentage, turnover_share, capex_share, opex_share, nfrd_requirement)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, reporting_period, economic_activity, taxonomy_code,
                  alignment_percentage, turnover_share, capex_share, opex_share, nfrd_requirement))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"AB Taksonomisi uyumluluk ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_sustainability_target(self, company_id: int, target_year: int,
                                target_category: str, target_name: str,
                                baseline_year: int = None, baseline_value: float = None,
                                target_value: float = None, target_unit: str = None,
                                achievement_status: str = None, progress_percentage: float = None) -> bool:
        """Sürdürülebilirlik hedefi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sustainability_targets 
                (company_id, target_year, target_category, target_name, baseline_year,
                 baseline_value, target_value, target_unit, achievement_status, progress_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, target_year, target_category, target_name, baseline_year,
                  baseline_value, target_value, target_unit, achievement_status, progress_percentage))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Sürdürülebilirlik hedefi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_tsrs_esrs_summary(self, company_id: int, reporting_period: str) -> Dict:
        """TSRS/ESRS özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Çift Önemlendirme
            assessment_year = reporting_period.split('-')[0]
            cursor.execute("""
                SELECT topic_name, impact_materiality_score, financial_materiality_score,
                       double_materiality_level, esrs_relevance
                FROM double_materiality_assessment 
                WHERE company_id = ? AND assessment_year = ?
                ORDER BY double_materiality_level DESC, impact_materiality_score DESC
            """, (company_id, assessment_year))

            double_materiality_topics = []
            for row in cursor.fetchall():
                topic_name, impact_score, financial_score, level, esrs_relevance = row
                double_materiality_topics.append({
                    'topic_name': topic_name,
                    'impact_materiality_score': impact_score,
                    'financial_materiality_score': financial_score,
                    'double_materiality_level': level,
                    'esrs_relevance': esrs_relevance
                })

            # ESRS Uyumluluk
            cursor.execute("""
                SELECT esrs_standard, compliance_status, COUNT(*)
                FROM esrs_requirements 
                WHERE company_id = ? AND reporting_period = ?
                GROUP BY esrs_standard, compliance_status
            """, (company_id, reporting_period))

            esrs_compliance = {}
            for row in cursor.fetchall():
                standard, status, count = row
                if standard not in esrs_compliance:
                    esrs_compliance[standard] = {}
                esrs_compliance[standard][status] = count

            # AB Taksonomisi
            cursor.execute("""
                SELECT economic_activity, alignment_percentage, turnover_share, capex_share, opex_share
                FROM eu_taxonomy_compliance 
                WHERE company_id = ? AND reporting_period = ?
                ORDER BY alignment_percentage DESC
            """, (company_id, reporting_period))

            taxonomy_activities = []
            total_alignment = 0
            for row in cursor.fetchall():
                activity, alignment, turnover, capex, opex = row
                taxonomy_activities.append({
                    'economic_activity': activity,
                    'alignment_percentage': alignment,
                    'turnover_share': turnover,
                    'capex_share': capex,
                    'opex_share': opex
                })
                total_alignment += alignment or 0

            # Sürdürülebilirlik Hedefleri
            cursor.execute("""
                SELECT target_category, target_name, target_value, target_unit,
                       achievement_status, progress_percentage
                FROM sustainability_targets 
                WHERE company_id = ? AND target_year = ?
                ORDER BY target_category, target_name
            """, (company_id, assessment_year))

            sustainability_targets = []
            for row in cursor.fetchall():
                category, name, value, unit, status, progress = row
                sustainability_targets.append({
                    'target_category': category,
                    'target_name': name,
                    'target_value': value,
                    'target_unit': unit,
                    'achievement_status': status,
                    'progress_percentage': progress
                })

            return {
                'double_materiality_topics': double_materiality_topics,
                'esrs_compliance': esrs_compliance,
                'taxonomy_activities': taxonomy_activities,
                'total_taxonomy_alignment': total_alignment,
                'sustainability_targets': sustainability_targets,
                'reporting_period': reporting_period,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"TSRS/ESRS özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()

    def generate_nfrd_disclosures(self, company_id: int, reporting_period: str) -> str:
        """NFRD açıklamaları oluştur"""
        summary = self.get_tsrs_esrs_summary(company_id, reporting_period)

        if not summary:
            return ""

        nfrd_content = f"# NFRD Açıklamaları - {reporting_period}\n\n"

        # Çift Önemlendirme
        nfrd_content += "## Çift Önemlendirme Değerlendirmesi\n\n"
        nfrd_content += "| Konu | Etki Önemliliği | Finansal Önemlilik | Çift Önemlilik Seviyesi |\n"
        nfrd_content += "|------|----------------|-------------------|------------------------|\n"

        for topic in summary['double_materiality_topics']:
            nfrd_content += f"| {topic['topic_name']} | {topic['impact_materiality_score']} | {topic['financial_materiality_score']} | {topic['double_materiality_level']} |\n"

        nfrd_content += "\n"

        # AB Taksonomisi
        nfrd_content += "## AB Taksonomisi Uyumluluk\n\n"
        nfrd_content += "| Ekonomik Faaliyet | Uyumluluk Oranı | Ciro Payı | Yatırım Payı | İşletme Gideri Payı |\n"
        nfrd_content += "|-------------------|-----------------|-----------|--------------|-------------------|\n"

        for activity in summary['taxonomy_activities']:
            nfrd_content += f"| {activity['economic_activity']} | {activity['alignment_percentage']}% | {activity['turnover_share']}% | {activity['capex_share']}% | {activity['opex_share']}% |\n"

        nfrd_content += f"\n**Toplam Taksonomi Uyumluluğu: {summary['total_taxonomy_alignment']}%**\n\n"

        # Sürdürülebilirlik Hedefleri
        nfrd_content += "## Sürdürülebilirlik Hedefleri\n\n"
        nfrd_content += "| Kategori | Hedef | Hedef Değer | İlerleme | Durum |\n"
        nfrd_content += "|----------|-------|-------------|----------|-------|\n"

        for target in summary['sustainability_targets']:
            nfrd_content += f"| {target['target_category']} | {target['target_name']} | {target['target_value']} {target['target_unit']} | {target['progress_percentage']}% | {target['achievement_status']} |\n"

        return nfrd_content
