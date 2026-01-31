#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STAKEHOLDER ANKET MODÜLÜ
- Dinamik anket oluşturma
- Çok paydaşlı değerlendirme
- Otomatik skorlama
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List


class StakeholderSurvey:
    """Stakeholder anket yönetimi sınıfı"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.question_types = {
            'multiple_choice': 'Çoktan Seçmeli',
            'scale': 'Ölçek (1-5)',
            'text': 'Açık Uçlu Metin',
            'boolean': 'Evet/Hayır'
        }

    def create_survey(self, company_id: int, survey_name: str,
                     stakeholder_category: str, description: str = "") -> int:
        """Yeni anket oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        survey_data = {
            'description': description,
            'created_at': datetime.now().isoformat(),
            'status': 'draft'
        }

        cursor.execute("""
            INSERT INTO stakeholder_surveys 
            (company_id, survey_name, stakeholder_category, survey_data)
            VALUES (?, ?, ?, ?)
        """, (company_id, survey_name, stakeholder_category, json.dumps(survey_data)))

        survey_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return survey_id

    def add_question(self, survey_id: int, question_text: str,
                    question_type: str, weight: float = 1.0,
                    category: str = None, sdg_mapping: str = None,
                    options: List[str] = None) -> int:
        """Anket sorusu ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Çoktan seçmeli sorular için seçenekleri JSON olarak sakla
        question_data = {}
        if options and question_type == 'multiple_choice':
            question_data['options'] = options

        cursor.execute("""
            INSERT INTO survey_questions 
            (survey_id, question_text, question_type, weight, category, sdg_mapping)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (survey_id, question_text, question_type, weight, category, sdg_mapping))

        question_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return question_id

    def get_survey_questions(self, survey_id: int) -> List[Dict]:
        """Anket sorularını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, question_text, question_type, weight, category, sdg_mapping
            FROM survey_questions
            WHERE survey_id = ?
            ORDER BY id
        """, (survey_id,))

        questions = []
        for row in cursor.fetchall():
            questions.append({
                'id': row[0],
                'question_text': row[1],
                'question_type': row[2],
                'weight': row[3],
                'category': row[4],
                'sdg_mapping': row[5]
            })

        conn.close()
        return questions

    def submit_response(self, survey_id: int, question_id: int,
                       response_value: str, stakeholder_type: str = None) -> int:
        """Anket cevabı gönder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Cevabı skorla
        score = self._calculate_response_score(question_id, response_value)

        cursor.execute("""
            INSERT INTO survey_responses 
            (survey_id, question_id, response_value, score, stakeholder_type)
            VALUES (?, ?, ?, ?, ?)
        """, (survey_id, question_id, response_value, score, stakeholder_type))

        response_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return response_id

    def _calculate_response_score(self, question_id: int, response_value: str) -> float:
        """Cevap skorunu hesapla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT question_type, weight FROM survey_questions WHERE id = ?
        """, (question_id,))

        result = cursor.fetchone()
        if not result:
            return 0.0

        question_type, weight = result
        conn.close()

        if question_type == 'boolean':
            return 5.0 if response_value.lower() in ['evet', 'yes', 'true', '1'] else 0.0
        elif question_type == 'scale':
            try:
                score = float(response_value)
                return min(max(score, 0), 5) * weight
            except ValueError:
                return 0.0
        elif question_type == 'multiple_choice':
            # Çoktan seçmeli sorular için varsayılan skorlama
            return 3.0 * weight
        else:  # text
            # Açık uçlu sorular için uzunluk bazlı skorlama
            return min(len(response_value) / 50, 5) * weight

    def get_survey_results(self, survey_id: int) -> Dict:
        """Anket sonuçlarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Anket bilgileri
        cursor.execute("""
            SELECT survey_name, stakeholder_category, survey_data
            FROM stakeholder_surveys WHERE id = ?
        """, (survey_id,))

        survey_info = cursor.fetchone()
        if not survey_info:
            return {}

        # Sorular ve cevaplar
        cursor.execute("""
            SELECT q.question_text, q.question_type, q.weight,
                   AVG(sr.score) as avg_score, COUNT(sr.id) as response_count
            FROM survey_questions q
            LEFT JOIN survey_responses sr ON q.id = sr.question_id
            WHERE q.survey_id = ?
            GROUP BY q.id, q.question_text, q.question_type, q.weight
            ORDER BY q.id
        """, (survey_id,))

        questions = []
        total_score = 0
        total_weight = 0

        for row in cursor.fetchall():
            question_text, question_type, weight, avg_score, response_count = row
            avg_score = avg_score or 0
            response_count = response_count or 0

            questions.append({
                'question_text': question_text,
                'question_type': question_type,
                'weight': weight,
                'avg_score': round(avg_score, 2),
                'response_count': response_count
            })

            total_score += avg_score * weight
            total_weight += weight

        # Genel skor hesapla
        overall_score = (total_score / total_weight) if total_weight > 0 else 0

        conn.close()

        return {
            'survey_name': survey_info[0],
            'stakeholder_category': survey_info[1],
            'overall_score': round(overall_score, 2),
            'total_responses': sum(q['response_count'] for q in questions),
            'questions': questions
        }

    def get_company_surveys(self, company_id: int) -> List[Dict]:
        """Şirketin tüm anketlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, survey_name, stakeholder_category, 
                   total_responses, created_at
            FROM stakeholder_surveys
            WHERE company_id = ?
            ORDER BY created_at DESC
        """, (company_id,))

        surveys = []
        for row in cursor.fetchall():
            surveys.append({
                'id': row[0],
                'survey_name': row[1],
                'stakeholder_category': row[2],
                'total_responses': row[3],
                'created_at': row[4]
            })

        conn.close()
        return surveys
