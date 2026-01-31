#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MATERYAL KONU DEĞERLENDİRME MODÜLÜ
- Materyal konu belirleme süreci
- Stakeholder etki analizi
- Öncelik skorlaması
"""

import sqlite3
from typing import Dict, List


class MaterialityAssessment:
    """Materyal konu değerlendirme sınıfı"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.stakeholder_categories = {
            'investors': {'weight': 0.25, 'influence': 'high'},
            'customers': {'weight': 0.20, 'influence': 'high'},
            'employees': {'weight': 0.15, 'influence': 'medium'},
            'suppliers': {'weight': 0.15, 'influence': 'medium'},
            'community': {'weight': 0.10, 'influence': 'medium'},
            'regulators': {'weight': 0.10, 'influence': 'high'},
            'ngos': {'weight': 0.05, 'influence': 'low'}
        }

    def create_materiality_tables(self) -> None:
        """Materyal konu değerlendirme tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Materyal konular tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materiality_topics (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                topic_name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                sdg_mapping TEXT,
                priority_score REAL DEFAULT 0,
                stakeholder_impact REAL DEFAULT 0,
                business_impact REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Stakeholder anketleri tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stakeholder_surveys (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                survey_name TEXT NOT NULL,
                stakeholder_category TEXT NOT NULL,
                survey_data TEXT, -- JSON format
                total_responses INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
        """)

        # Anket şablonları tablosu
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS survey_templates (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'Genel',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
            """
        )

        # Anket soruları tablosu (şablon bazlı)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS survey_questions (
                id INTEGER PRIMARY KEY,
                template_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL, -- multiple_choice, scale, text, boolean
                weight REAL DEFAULT 1.0,
                category TEXT,
                sdg_mapping TEXT,
                FOREIGN KEY(template_id) REFERENCES survey_templates(id) ON DELETE CASCADE
            )
            """
        )

        # Anket cevapları tablosu (şirket bazlı)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS survey_responses (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                response_value TEXT,
                score REAL DEFAULT 0,
                response_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY(question_id) REFERENCES survey_questions(id) ON DELETE CASCADE
            )
            """
        )

        # Önceliklendirme sonuçları tablosu (kategori bazlı)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prioritization_results (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                total_score REAL NOT NULL,
                priority_level TEXT NOT NULL, -- high, medium, low
                calculation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
            )
            """
        )

        conn.commit()
        conn.close()

    def calculate_priority_score(self, responses: List[Dict], weights: Dict) -> float:
        """
        Öncelik skoru hesaplama
        
        Formül: Σ(Cevap_Değeri × Soru_Ağırlığı × Stakeholder_Etkisi × İş_Etkisi)
        """
        total_score = 0
        max_possible_score = 0

        for response in responses:
            question_weight = response.get('weight', 1.0)
            stakeholder_impact = response.get('stakeholder_impact', 1.0)  # 1-5 skala
            business_impact = response.get('business_impact', 1.0)        # 1-5 skala
            response_value = response.get('normalized_value', 0.0)        # 0-1 arası

            score = response_value * question_weight * stakeholder_impact * business_impact
            total_score += score
            max_possible_score += question_weight * 5 * 5  # Maksimum değer

        # Normalize et (0-100 arası)
        if max_possible_score > 0:
            normalized_score = (total_score / max_possible_score) * 100
        else:
            normalized_score = 0

        return round(normalized_score, 2)

    def determine_priority_level(self, score: float) -> str:
        """Öncelik seviyesi belirleme"""
        if score >= 75:
            return "high"
        elif score >= 50:
            return "medium"
        else:
            return "low"

    def create_survey_template(self, company_id: int, survey_name: str,
                             stakeholder_category: str) -> int:
        """Anket şablonu oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO stakeholder_surveys 
            (company_id, survey_name, stakeholder_category, survey_data)
            VALUES (?, ?, ?, ?)
        """, (company_id, survey_name, stakeholder_category, "{}"))

        survey_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return survey_id

    def add_survey_question(self, survey_id: int, question_text: str,
                           question_type: str, weight: float = 1.0,
                           category: str = None, sdg_mapping: str = None) -> int:
        """Anket sorusu ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO survey_questions 
            (survey_id, question_text, question_type, weight, category, sdg_mapping)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (survey_id, question_text, question_type, weight, category, sdg_mapping))

        question_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return question_id

    def submit_survey_response(self, survey_id: int, question_id: int,
                              response_value: str, score: float,
                              stakeholder_type: str = None) -> int:
        """Anket cevabı gönder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO survey_responses 
            (survey_id, question_id, response_value, score, stakeholder_type)
            VALUES (?, ?, ?, ?, ?)
        """, (survey_id, question_id, response_value, score, stakeholder_type))

        response_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return response_id

    def get_prioritization_results(self, company_id: int) -> List[Dict]:
        """Önceliklendirme sonuçlarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT mt.topic_name, mt.category, pr.total_score, pr.priority_level,
                   pr.calculation_date
            FROM prioritization_results pr
            JOIN materiality_topics mt ON pr.topic_id = mt.id
            WHERE pr.company_id = ?
            ORDER BY pr.total_score DESC
        """, (company_id,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'topic_name': row[0],
                'category': row[1],
                'total_score': row[2],
                'priority_level': row[3],
                'calculation_date': row[4]
            })

        conn.close()
        return results
