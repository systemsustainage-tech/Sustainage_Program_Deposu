#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDP (Carbon Disclosure Project) Manager
CDP Climate Change, Water Security ve Forests anketleri için yönetim
"""

import logging
import os
import sqlite3
import json
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
        self._populate_cdp_categories()

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
                    weighting_scheme TEXT DEFAULT 'Standard',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, reporting_year, questionnaire_type)
                )
            """)
            
            # Check for weighting_scheme column in cdp_scoring (Migration)
            cursor.execute("PRAGMA table_info(cdp_scoring)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'weighting_scheme' not in columns:
                cursor.execute("ALTER TABLE cdp_scoring ADD COLUMN weighting_scheme TEXT DEFAULT 'Standard'")


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
        """CDP anketlerini JSON dosyasından doldur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        json_path = os.path.join(os.path.dirname(__file__), 'cdp_questions.json')
        
        try:
            if not os.path.exists(json_path):
                logging.warning(f"CDP questions JSON not found at {json_path}")
                return

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Climate Change
            if 'climate_change' in data:
                for q in data['climate_change']:
                    # Tercihen Türkçe metni kullan, yoksa İngilizce
                    text = q.get('text_tr') if q.get('text_tr') else q.get('text_en')
                    cursor.execute("""
                        INSERT OR IGNORE INTO cdp_climate_change 
                        (company_id, reporting_year, question_id, question_text, question_category, response_type, scoring_weight)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (0, 2024, q['id'], text, q['category'], q['type'], q.get('weight', 1.0)))

            # Water Security
            if 'water_security' in data:
                for q in data['water_security']:
                    text = q.get('text_tr') if q.get('text_tr') else q.get('text_en')
                    cursor.execute("""
                        INSERT OR IGNORE INTO cdp_water_security 
                        (company_id, reporting_year, question_id, question_text, question_category, response_type, scoring_weight)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (0, 2024, q['id'], text, q['category'], q['type'], q.get('weight', 1.0)))

            # Forests
            if 'forests' in data:
                for q in data['forests']:
                    text = q.get('text_tr') if q.get('text_tr') else q.get('text_en')
                    cursor.execute("""
                        INSERT OR IGNORE INTO cdp_forests 
                        (company_id, reporting_year, question_id, question_text, question_category, response_type, scoring_weight)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (0, 2024, q['id'], text, q['category'], q['type'], q.get('weight', 1.0)))
            
            conn.commit()
            logging.info("CDP questionnaires populated from JSON")
            
        except Exception as e:
            logging.error(f"Error populating CDP questionnaires: {e}")
        finally:
            conn.close()

    def get_weighting_scheme(self, company_id: int, reporting_year: int = 2024) -> str:
        """Şirketin puanlama ağırlıklandırma şemasını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Check for any existing record first
            cursor.execute("""
                SELECT weighting_scheme FROM cdp_scoring 
                WHERE company_id = ? AND reporting_year = ?
                LIMIT 1
            """, (company_id, reporting_year))
            row = cursor.fetchone()
            return row[0] if row else 'Standard'
        except Exception as e:
            logging.error(f"Error getting weighting scheme: {e}")
            return 'Standard'
        finally:
            conn.close()

    def update_weighting_scheme(self, company_id: int, scheme: str, reporting_year: int = 2024) -> bool:
        """Puanlama ağırlıklandırma şemasını güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Update all scoring records for this year
            cursor.execute("""
                UPDATE cdp_scoring 
                SET weighting_scheme = ? 
                WHERE company_id = ? AND reporting_year = ?
            """, (scheme, company_id, reporting_year))
            
            # If no record exists, insert a default one for Climate Change (as a placeholder)
            if cursor.rowcount == 0:
                 cursor.execute("""
                    INSERT INTO cdp_scoring (company_id, reporting_year, questionnaire_type, weighting_scheme)
                    VALUES (?, ?, 'Climate Change', ?)
                """, (company_id, reporting_year, scheme))
            
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error updating weighting scheme: {e}")
            return False
        finally:
            conn.close()

    def update_question_weight(self, questionnaire_type: str, company_id: int, question_id: str, weight: float, reporting_year: int = 2024) -> bool:
        """Soru puanlama ağırlığını güncelle"""
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
                SET scoring_weight = ? 
                WHERE company_id = ? AND reporting_year = ? AND question_id = ?
            """, (weight, company_id, reporting_year, question_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error updating question weight: {e}")
            return False
        finally:
            conn.close()

    def reset_weights_to_standard(self, company_id: int, reporting_year: int = 2024) -> bool:
        """Ağırlıkları standart (JSON) değerlerine sıfırla"""
        # First set scheme to Standard
        if not self.update_weighting_scheme(company_id, 'Standard', reporting_year):
            return False
            
        # Then reload weights from template (company_id=0)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            table_mapping = {
                "Climate Change": "cdp_climate_change",
                "Water Security": "cdp_water_security",
                "Forests": "cdp_forests"
            }
            
            for q_type, table_name in table_mapping.items():
                # Update weights from template questions
                cursor.execute(f"""
                    UPDATE {table_name}
                    SET scoring_weight = (
                        SELECT t.scoring_weight 
                        FROM {table_name} t 
                        WHERE t.company_id = 0 AND t.reporting_year = ? AND t.question_id = {table_name}.question_id
                    )
                    WHERE company_id = ? AND reporting_year = ?
                """, (reporting_year, company_id, reporting_year))
                
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error resetting weights: {e}")
            return False
        finally:
            conn.close()

    def _populate_cdp_categories(self) -> None:
        """CDP kategorilerini doldur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
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
            logging.info("[OK] CDP kategorileri dolduruldu")

        except Exception as e:
            logging.error(f"[ERROR] CDP kategorileri doldurulurken hata: {e}")
        finally:
            conn.close()

    def ensure_company_questions(self, company_id: int, reporting_year: int = 2024) -> None:
        """Şirket için soru kayıtlarının oluşturulduğundan emin ol"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            table_mapping = {
                "Climate Change": "cdp_climate_change",
                "Water Security": "cdp_water_security",
                "Forests": "cdp_forests"
            }

            for q_type, table_name in table_mapping.items():
                # Check if company has questions
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE company_id = ? AND reporting_year = ?", (company_id, reporting_year))
                count = cursor.fetchone()[0]
                
                if count == 0:
                    # Copy from template (company_id=0)
                    cursor.execute(f"""
                        INSERT INTO {table_name} 
                        (company_id, reporting_year, question_id, question_text, question_category, response_type, scoring_weight)
                        SELECT ?, ?, question_id, question_text, question_category, response_type, scoring_weight
                        FROM {table_name}
                        WHERE company_id = 0 AND reporting_year = ?
                    """, (company_id, reporting_year, reporting_year))
                    logging.info(f"Initialized {q_type} questions for company {company_id}")

            conn.commit()
        except Exception as e:
            logging.error(f"Error ensuring company questions: {e}")
        finally:
            conn.close()

    def get_questions(self, questionnaire_type: str, company_id: int, reporting_year: int = 2024) -> List[Dict]:
        """Belirli bir anket türü için soruları getir"""
        # Ensure questions exist first
        self.ensure_company_questions(company_id, reporting_year)
        
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

            # Only fetch company's questions now
            cursor.execute(f"""
                SELECT * FROM {table_name}
                WHERE company_id = ? AND reporting_year = ?
                ORDER BY question_id
            """, (company_id, reporting_year))

            columns = [col[0] for col in cursor.description]
            raw_rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

            questions = []
            for q in raw_rows:
                translated = self._translate_question_record(questionnaire_type, q)
                questions.append(translated)
            return questions

        except Exception as e:
            logging.error(f"Sorular getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def _get_translation_key(self, questionnaire_type: str, question_id: str) -> str:
        if not question_id:
            return ""
        prefix = question_id[0].upper()
        parts = question_id[1:].split(".")
        if len(parts) != 2:
            return ""
        section, sub = parts
        if prefix == "C":
            return f"cdp_c{section}_{sub}"
        if prefix == "W":
            return f"cdp_w{section}_{sub}"
        if prefix == "F":
            return f"cdp_f{section}_{sub}"
        return ""

    def _translate_question_record(self, questionnaire_type: str, question: Dict) -> Dict:
        qid = question.get("question_id", "")
        key = self._get_translation_key(questionnaire_type, qid)
        if key:
            question_text = question.get("question_text", "")
            question["question_text"] = self.lm.tr(key, question_text or key)

        category = question.get("question_category", "")
        if category:
            cat_key_map = {
                "Governance": "cdp_cat_name_governance",
                "Strategy": "cdp_cat_name_strategy",
                "Risk Management": "cdp_cat_name_risk_management",
                "Metrics and Targets": "cdp_cat_name_metrics_targets",
            }
            cat_key = cat_key_map.get(category)
            if cat_key:
                question["question_category"] = self.lm.tr(cat_key, category)

        return question

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
