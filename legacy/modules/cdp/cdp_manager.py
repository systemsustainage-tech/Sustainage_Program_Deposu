#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDP (Carbon Disclosure Project) Manager
CDP Climate Change, Water Security ve Forests anketleri için yönetim
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List
from utils.language_manager import LanguageManager
from config.database import DB_PATH


class CDPManager:
    """CDP (Carbon Disclosure Project) yöneticisi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.lm = LanguageManager()
        self._init_cdp_tables()
        self._populate_cdp_questionnaires()

    def _init_cdp_tables(self) -> None:
        """CDP tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # CDP Climate Change anketi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cdp_climate_change (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    question_id TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    question_category TEXT NOT NULL,
                    response TEXT,
                    response_type TEXT DEFAULT 'text',
                    scoring_weight REAL DEFAULT 1.0,
                    evidence TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, reporting_year, question_id)
                )
            """)

            # CDP Water Security anketi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cdp_water_security (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    question_id TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    question_category TEXT NOT NULL,
                    response TEXT,
                    response_type TEXT DEFAULT 'text',
                    scoring_weight REAL DEFAULT 1.0,
                    evidence TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, reporting_year, question_id)
                )
            """)

            # CDP Forests anketi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cdp_forests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    question_id TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    question_category TEXT NOT NULL,
                    response TEXT,
                    response_type TEXT DEFAULT 'text',
                    scoring_weight REAL DEFAULT 1.0,
                    evidence TEXT,
                    verification_status TEXT DEFAULT 'Not Verified',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, reporting_year, question_id)
                )
            """)

            # CDP Scoring sistemi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cdp_scoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    questionnaire_type TEXT NOT NULL,
                    total_score REAL DEFAULT 0.0,
                    grade TEXT DEFAULT 'D',
                    disclosure_score REAL DEFAULT 0.0,
                    awareness_score REAL DEFAULT 0.0,
                    management_score REAL DEFAULT 0.0,
                    leadership_score REAL DEFAULT 0.0,
                    submission_date TIMESTAMP,
                    verification_date TIMESTAMP,
                    status TEXT DEFAULT 'Draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, reporting_year, questionnaire_type)
                )
            """)

            # CDP Soru kategorileri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cdp_question_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    questionnaire_type TEXT NOT NULL,
                    category_code TEXT NOT NULL,
                    category_name TEXT NOT NULL,
                    category_description TEXT,
                    weight REAL DEFAULT 1.0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logging.info("[OK] CDP tabloları oluşturuldu")

        except Exception as e:
            logging.error(f"[ERROR] CDP tabloları oluşturulurken hata: {e}")
        finally:
            conn.close()

    def _populate_cdp_questionnaires(self) -> None:
        """CDP anketlerini doldur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # CDP Climate Change soruları
            climate_questions = [
                # Governance
                ("C1.1", "C1.1", "Governance", self.lm.tr('cdp_c1_1', "Does your organization have board-level oversight of climate-related issues?"), "text", 1.0),
                ("C1.2", "C1.2", "Governance", self.lm.tr('cdp_c1_2', "Please provide details of your organization's climate change governance structure."), "text", 1.0),
                ("C1.3", "C1.3", "Governance", self.lm.tr('cdp_c1_3', "Do you provide incentives for the management of climate-related issues?"), "text", 1.0),

                # Strategy
                ("C2.1", "C2.1", "Strategy", self.lm.tr('cdp_c2_1', "Have you identified any climate-related risks with the potential to have a substantive financial or strategic impact on your business?"), "text", 1.0),
                ("C2.2", "C2.2", "Strategy", self.lm.tr('cdp_c2_2', "How do you define short-, medium- and long-term time horizons?"), "text", 1.0),
                ("C2.3", "C2.3", "Strategy", self.lm.tr('cdp_c2_3', "How do you assess the potential impact of climate-related risks and opportunities on your business?"), "text", 1.0),

                # Risk Management
                ("C3.1", "C3.1", "Risk Management", self.lm.tr('cdp_c3_1', "Do you have a process for identifying, assessing, and managing climate-related risks?"), "text", 1.0),
                ("C3.2", "C3.2", "Risk Management", self.lm.tr('cdp_c3_2', "How do you prioritize climate-related risks?"), "text", 1.0),
                ("C3.3", "C3.3", "Risk Management", self.lm.tr('cdp_c3_3', "How do you monitor climate-related risks?"), "text", 1.0),

                # Metrics and Targets
                ("C4.1", "C4.1", "Metrics and Targets", self.lm.tr('cdp_c4_1', "Do you have a process for identifying, assessing, and managing climate-related opportunities?"), "text", 1.0),
                ("C4.2", "C4.2", "Metrics and Targets", self.lm.tr('cdp_c4_2', "What is your organization's total gross global Scope 1 and Scope 2 greenhouse gas emissions?"), "text", 1.0),
                ("C4.3", "C4.3", "Metrics and Targets", self.lm.tr('cdp_c4_3', "What is your organization's total gross global Scope 3 greenhouse gas emissions?"), "text", 1.0),
            ]

            for question_id, question_code, category, question_text, response_type, weight in climate_questions:
                cursor.execute("""
                    INSERT OR IGNORE INTO cdp_climate_change 
                    (company_id, reporting_year, question_id, question_text, question_category, response_type, scoring_weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (0, 2024, question_id, question_text, category, response_type, weight))

            # CDP Water Security soruları
            water_questions = [
                # Governance
                ("W1.1", "W1.1", "Governance", self.lm.tr('cdp_w1_1', "Does your organization have board-level oversight of water-related issues?"), "text", 1.0),
                ("W1.2", "W1.2", "Governance", self.lm.tr('cdp_w1_2', "Please provide details of your organization's water governance structure."), "text", 1.0),
                ("W1.3", "W1.3", "Governance", self.lm.tr('cdp_w1_3', "Do you provide incentives for the management of water-related issues?"), "text", 1.0),

                # Strategy
                ("W2.1", "W2.1", "Strategy", self.lm.tr('cdp_w2_1', "Have you identified any water-related risks with the potential to have a substantive financial or strategic impact on your business?"), "text", 1.0),
                ("W2.2", "W2.2", "Strategy", self.lm.tr('cdp_w2_2', "How do you assess the potential impact of water-related risks and opportunities on your business?"), "text", 1.0),
                ("W2.3", "W2.3", "Strategy", self.lm.tr('cdp_w2_3', "What water-related opportunities have you identified?"), "text", 1.0),

                # Risk Management
                ("W3.1", "W3.1", "Risk Management", self.lm.tr('cdp_w3_1', "Do you have a process for identifying, assessing, and managing water-related risks?"), "text", 1.0),
                ("W3.2", "W3.2", "Risk Management", self.lm.tr('cdp_w3_2', "How do you prioritize water-related risks?"), "text", 1.0),
                ("W3.3", "W3.3", "Risk Management", self.lm.tr('cdp_w3_3', "How do you monitor water-related risks?"), "text", 1.0),

                # Metrics and Targets
                ("W4.1", "W4.1", "Metrics and Targets", self.lm.tr('cdp_w4_1', "What is your organization's total water withdrawal?"), "text", 1.0),
                ("W4.2", "W4.2", "Metrics and Targets", self.lm.tr('cdp_w4_2', "What is your organization's total water consumption?"), "text", 1.0),
                ("W4.3", "W4.3", "Metrics and Targets", self.lm.tr('cdp_w4_3', "Do you have any water-related targets?"), "text", 1.0),
            ]

            for question_id, question_code, category, question_text, response_type, weight in water_questions:
                cursor.execute("""
                    INSERT OR IGNORE INTO cdp_water_security 
                    (company_id, reporting_year, question_id, question_text, question_category, response_type, scoring_weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (0, 2024, question_id, question_text, category, response_type, weight))

            # CDP Forests soruları
            forests_questions = [
                # Governance
                ("F1.1", "F1.1", "Governance", "Does your organization have board-level oversight of forest-related issues?", "text", 1.0),
                ("F1.2", "F1.2", "Governance", "Please provide details of your organization's forest governance structure.", "text", 1.0),
                ("F1.3", "F1.3", "Governance", "Do you provide incentives for the management of forest-related issues?", "text", 1.0),

                # Strategy
                ("F2.1", "F2.1", "Strategy", "Have you identified any forest-related risks with the potential to have a substantive financial or strategic impact on your business?", "text", 1.0),
                ("F2.2", "F2.2", "Strategy", "How do you assess the potential impact of forest-related risks and opportunities on your business?", "text", 1.0),
                ("F2.3", "F2.3", "Strategy", "What forest-related opportunities have you identified?", "text", 1.0),

                # Risk Management
                ("F3.1", "F3.1", "Risk Management", "Do you have a process for identifying, assessing, and managing forest-related risks?", "text", 1.0),
                ("F3.2", "F3.2", "Risk Management", "How do you prioritize forest-related risks?", "text", 1.0),
                ("F3.3", "F3.3", "Risk Management", "How do you monitor forest-related risks?", "text", 1.0),

                # Metrics and Targets
                ("F4.1", "F4.1", "Metrics and Targets", "What is your organization's total forest footprint?", "text", 1.0),
                ("F4.2", "F4.2", "Metrics and Targets", "Do you have any forest-related targets?", "text", 1.0),
                ("F4.3", "F4.3", "Metrics and Targets", "What actions are you taking to address forest-related risks and opportunities?", "text", 1.0),
            ]

            for question_id, question_code, category, question_text, response_type, weight in forests_questions:
                cursor.execute("""
                    INSERT OR IGNORE INTO cdp_forests 
                    (company_id, reporting_year, question_id, question_text, question_category, response_type, scoring_weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (0, 2024, question_id, question_text, category, response_type, weight))

            # Kategori tanımları
            categories = [
                ("Climate Change", "GOV", "Governance", self.lm.tr('cdp_cat_gov_cc', "Board oversight and management of climate issues"), 1.0),
                ("Climate Change", "STR", "Strategy", self.lm.tr('cdp_cat_str_cc', "Climate strategy and risk assessment"), 1.0),
                ("Climate Change", "RISK", "Risk Management", self.lm.tr('cdp_cat_risk_cc', "Climate risk management processes"), 1.0),
                ("Climate Change", "MET", "Metrics and Targets", self.lm.tr('cdp_cat_met_cc', "Climate metrics, targets and performance"), 1.0),
                ("Water Security", "GOV", "Governance", self.lm.tr('cdp_cat_gov_ws', "Board oversight and management of water issues"), 1.0),
                ("Water Security", "STR", "Strategy", self.lm.tr('cdp_cat_str_ws', "Water strategy and risk assessment"), 1.0),
                ("Water Security", "RISK", "Risk Management", self.lm.tr('cdp_cat_risk_ws', "Water risk management processes"), 1.0),
                ("Water Security", "MET", "Metrics and Targets", self.lm.tr('cdp_cat_met_ws', "Water metrics, targets and performance"), 1.0),
                ("Forests", "GOV", "Governance", self.lm.tr('cdp_cat_gov_f', "Board oversight and management of forest issues"), 1.0),
                ("Forests", "STR", "Strategy", self.lm.tr('cdp_cat_str_f', "Forest strategy and risk assessment"), 1.0),
                ("Forests", "RISK", "Risk Management", self.lm.tr('cdp_cat_risk_f', "Forest risk management processes"), 1.0),
                ("Forests", "MET", "Metrics and Targets", self.lm.tr('cdp_cat_met_f', "Forest metrics, targets and performance"), 1.0),
            ]

            for questionnaire_type, category_code, category_name, description, weight in categories:
                cursor.execute("""
                    INSERT OR IGNORE INTO cdp_question_categories 
                    (questionnaire_type, category_code, category_name, category_description, weight)
                    VALUES (?, ?, ?, ?, ?)
                """, (questionnaire_type, category_code, category_name, description, weight))

            conn.commit()
            logging.info("[OK] CDP anketleri dolduruldu")

        except Exception as e:
            logging.error(f"[ERROR] CDP anketleri doldurulurken hata: {e}")
        finally:
            conn.close()

    def get_questions(self, questionnaire_type: str, company_id: int, reporting_year: int = 2024) -> List[Dict]:
        """Belirli bir anket türü için soruları getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            table_mapping = {
                "Climate Change": "cdp_climate_change",
                "Water Security": "cdp_water_security",
                "Forests": "cdp_forests"
            }

            table_name = table_mapping.get(questionnaire_type)
            if not table_name:
                return []

            cursor.execute(f"""
                SELECT * FROM {table_name}
                WHERE (company_id = ? OR company_id = 0) AND reporting_year = ?
                ORDER BY question_id
            """, (company_id, reporting_year))

            columns = [col[0] for col in cursor.description]
            questions = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return questions

        except Exception as e:
            logging.error(f"Sorular getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def save_response(self, questionnaire_type: str, company_id: int, question_id: str,
                     response: str, evidence: str = "", reporting_year: int = 2024) -> bool:
        """Soru yanıtını kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            table_mapping = {
                "Climate Change": "cdp_climate_change",
                "Water Security": "cdp_water_security",
                "Forests": "cdp_forests"
            }

            table_name = table_mapping.get(questionnaire_type)
            if not table_name:
                return False

            cursor.execute(f"""
                UPDATE {table_name}
                SET response = ?, evidence = ?, last_updated = CURRENT_TIMESTAMP
                WHERE company_id = ? AND question_id = ? AND reporting_year = ?
            """, (response, evidence, company_id, question_id, reporting_year))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Yanıt kaydedilirken hata: {e}")
            return False
        finally:
            conn.close()

    def get_company_responses(self, questionnaire_type: str, company_id: int,
                             reporting_year: int = 2024) -> List[Dict]:
        """Şirket yanıtlarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            table_mapping = {
                "Climate Change": "cdp_climate_change",
                "Water Security": "cdp_water_security",
                "Forests": "cdp_forests"
            }

            table_name = table_mapping.get(questionnaire_type)
            if not table_name:
                return []

            cursor.execute(f"""
                SELECT * FROM {table_name}
                WHERE company_id = ? AND reporting_year = ?
                ORDER BY question_id
            """, (company_id, reporting_year))

            columns = [col[0] for col in cursor.description]
            responses = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return responses

        except Exception as e:
            logging.error(f"Yanıtlar getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def calculate_scores(self, questionnaire_type: str, company_id: int,
                        reporting_year: int = 2024) -> Dict:
        """CDP skorlarını hesapla"""
        try:
            responses = self.get_company_responses(questionnaire_type, company_id, reporting_year)

            if not responses:
                return {
                    "total_score": 0.0,
                    "grade": "D",
                    "disclosure_score": 0.0,
                    "awareness_score": 0.0,
                    "management_score": 0.0,
                    "leadership_score": 0.0,
                    "completion_rate": 0.0
                }

            # Kategori bazında skorlar
            category_scores = {}
            total_weight = 0.0
            total_score = 0.0

            for response in responses:
                category = response.get('question_category', '')
                weight = response.get('scoring_weight', 1.0)
                has_response = bool(response.get('response', '').strip())

                if category not in category_scores:
                    category_scores[category] = {'score': 0.0, 'weight': 0.0, 'questions': 0}

                category_scores[category]['weight'] += weight
                category_scores[category]['questions'] += 1
                total_weight += weight

                if has_response:
                    category_scores[category]['score'] += weight
                    total_score += weight

            # Kategori skorlarını hesapla
            for category in category_scores:
                if category_scores[category]['weight'] > 0:
                    category_scores[category]['percentage'] = (
                        category_scores[category]['score'] / category_scores[category]['weight'] * 100
                    )
                else:
                    category_scores[category]['percentage'] = 0.0

            # Genel skor
            overall_percentage = (total_score / total_weight * 100) if total_weight > 0 else 0.0

            # CDP Grade hesaplama (A, B, C, D)
            if overall_percentage >= 90:
                grade = "A"
            elif overall_percentage >= 70:
                grade = "B"
            elif overall_percentage >= 50:
                grade = "C"
            else:
                grade = "D"

            # Skorları kaydet
            self._save_scoring(questionnaire_type, company_id, reporting_year, {
                "total_score": overall_percentage,
                "grade": grade,
                "disclosure_score": overall_percentage,
                "awareness_score": overall_percentage,
                "management_score": overall_percentage,
                "leadership_score": overall_percentage,
                "completion_rate": overall_percentage
            })

            return {
                "total_score": overall_percentage,
                "grade": grade,
                "disclosure_score": overall_percentage,
                "awareness_score": overall_percentage,
                "management_score": overall_percentage,
                "leadership_score": overall_percentage,
                "completion_rate": overall_percentage,
                "category_scores": category_scores
            }

        except Exception as e:
            logging.error(f"Skor hesaplanırken hata: {e}")
            return {
                "total_score": 0.0,
                "grade": "D",
                "disclosure_score": 0.0,
                "awareness_score": 0.0,
                "management_score": 0.0,
                "leadership_score": 0.0,
                "completion_rate": 0.0
            }

    def _save_scoring(self, questionnaire_type: str, company_id: int,
                     reporting_year: int, scores: Dict) -> None:
        """Skorları veritabanına kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO cdp_scoring 
                (company_id, reporting_year, questionnaire_type, total_score, grade,
                 disclosure_score, awareness_score, management_score, leadership_score,
                 submission_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, reporting_year, questionnaire_type,
                  scores['total_score'], scores['grade'],
                  scores['disclosure_score'], scores['awareness_score'],
                  scores['management_score'], scores['leadership_score'],
                  datetime.now().isoformat(), 'Completed'))

            conn.commit()

        except Exception as e:
            logging.error(f"Skorlar kaydedilirken hata: {e}")
        finally:
            conn.close()

    def get_company_summary(self, company_id: int, reporting_year: int = 2024) -> Dict:
        """Şirket CDP özeti"""
        try:
            questionnaires = ["Climate Change", "Water Security", "Forests"]
            summary = {
                "total_questionnaires": len(questionnaires),
                "completed_questionnaires": 0,
                "average_score": 0.0,
                "average_grade": "D",
                "questionnaire_scores": {}
            }

            total_score = 0.0
            completed_count = 0

            for questionnaire in questionnaires:
                scores = self.calculate_scores(questionnaire, company_id, reporting_year)
                summary["questionnaire_scores"][questionnaire] = scores  # type: ignore

                if scores['total_score'] > 0:
                    completed_count += 1
                    total_score += scores['total_score']

            summary["completed_questionnaires"] = completed_count
            summary["average_score"] = total_score / completed_count if completed_count > 0 else 0.0

            # Ortalama grade hesaplama
            avg_score = float(summary["average_score"])
            if avg_score >= 90:
                summary["average_grade"] = "A"
            elif avg_score >= 70:
                summary["average_grade"] = "B"
            elif avg_score >= 50:
                summary["average_grade"] = "C"
            else:
                summary["average_grade"] = "D"

            return summary

        except Exception as e:
            logging.error(f"Özet hesaplanırken hata: {e}")
            return {
                "total_questionnaires": 0,
                "completed_questionnaires": 0,
                "average_score": 0.0,
                "average_grade": "D",
                "questionnaire_scores": {}
            }
