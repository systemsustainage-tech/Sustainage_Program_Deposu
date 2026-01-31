#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Materialite Analizi
İşletme ve paydaş perspektifinden önemlilik analizi
"""

import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class MaterialityAnalyzer:
    """Materialite analizi yöneticisi"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Veritabanı tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Materialite konuları
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materiality_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                topic_name TEXT NOT NULL,
                topic_category TEXT,
                description TEXT,
                created_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Materialite değerlendirmeleri
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materiality_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                assessment_year INTEGER NOT NULL,
                assessment_name TEXT,
                created_by INTEGER,
                created_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Konu skorları
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materiality_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL,
                topic_id INTEGER NOT NULL,
                stakeholder_importance REAL DEFAULT 0,
                business_impact REAL DEFAULT 0,
                final_score REAL DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (assessment_id) REFERENCES materiality_assessments(id),
                FOREIGN KEY (topic_id) REFERENCES materiality_topics(id)
            )
        """)

        # Paydaş anketleri
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stakeholder_surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL,
                stakeholder_group TEXT NOT NULL,
                stakeholder_name TEXT,
                survey_date TEXT,
                responses TEXT,
                FOREIGN KEY (assessment_id) REFERENCES materiality_assessments(id)
            )
        """)

        conn.commit()
        conn.close()

    def create_assessment(self, company_id: int, year: int, assessment_name: str,
                         created_by: Optional[int] = None) -> Optional[int]:
        """Yeni materialite değerlendirmesi oluştur"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO materiality_assessments 
                (company_id, assessment_year, assessment_name, created_by, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, year, assessment_name, created_by, datetime.now().isoformat()))

            assessment_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return assessment_id

        except Exception as e:
            logging.error(f"Değerlendirme oluşturma hatası: {e}")
            return None

    def add_topic(self, company_id: int, topic_name: str, category: str = "",
                 description: str = "") -> Optional[int]:
        """Materialite konusu ekle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO materiality_topics 
                (company_id, topic_name, topic_category, description, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, topic_name, category, description, datetime.now().isoformat()))

            topic_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return topic_id

        except Exception as e:
            logging.error(f"Konu ekleme hatası: {e}")
            return None

    def score_topic(self, assessment_id: int, topic_id: int,
                   stakeholder_importance: float, business_impact: float,
                   notes: str = "") -> bool:
        """Konuyu skorla"""
        try:
            # Final skor: Ortalama veya ağırlıklı ortalama
            final_score = (stakeholder_importance + business_impact) / 2

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO materiality_scores 
                (assessment_id, topic_id, stakeholder_importance, business_impact, final_score, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (assessment_id, topic_id, stakeholder_importance, business_impact, final_score, notes))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            logging.error(f"Skorlama hatası: {e}")
            return False

    def get_materiality_matrix(self, assessment_id: int) -> List[Dict]:
        """Materialite matrisini al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT mt.topic_name, mt.topic_category, 
                       ms.stakeholder_importance, ms.business_impact, ms.final_score
                FROM materiality_scores ms
                JOIN materiality_topics mt ON ms.topic_id = mt.id
                WHERE ms.assessment_id = ?
                ORDER BY ms.final_score DESC
            """, (assessment_id,))

            matrix_data = []
            for row in cursor.fetchall():
                matrix_data.append({
                    'topic': row[0],
                    'category': row[1],
                    'stakeholder_importance': row[2],
                    'business_impact': row[3],
                    'final_score': row[4]
                })

            conn.close()
            return matrix_data

        except Exception as e:
            logging.error(f"Matris alma hatası: {e}")
            return []

    def categorize_topics(self, matrix_data: List[Dict]) -> Dict[str, List[Dict]]:
        """Konuları öneme göre kategorize et"""
        high_priority = []  # Yüksek önem (her iki boyutta da yüksek)
        medium_priority = []  # Orta önem
        low_priority = []  # Düşük önem

        for item in matrix_data:
            stakeholder = item['stakeholder_importance']
            business = item['business_impact']

            # Yüksek: Her ikisi de > 7
            if stakeholder >= 7 and business >= 7:
                high_priority.append(item)
            # Düşük: Her ikisi de < 4
            elif stakeholder < 4 and business < 4:
                low_priority.append(item)
            # Orta: Diğerleri
            else:
                medium_priority.append(item)

        return {
            'high': high_priority,
            'medium': medium_priority,
            'low': low_priority
        }

    def add_stakeholder_survey(self, assessment_id: int, stakeholder_group: str,
                              stakeholder_name: str, responses: Dict) -> bool:
        """Paydaş anketi ekle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO stakeholder_surveys 
                (assessment_id, stakeholder_group, stakeholder_name, survey_date, responses)
                VALUES (?, ?, ?, ?, ?)
            """, (
                assessment_id, stakeholder_group, stakeholder_name,
                datetime.now().isoformat(),
                json.dumps(responses, ensure_ascii=False)
            ))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            logging.error(f"Anket ekleme hatası: {e}")
            return False

    def get_default_topics(self) -> List[Dict]:
        """Varsayılan materialite konuları"""
        return [
            {'name': 'İklim Değişikliği', 'category': 'Çevresel'},
            {'name': 'Enerji Verimliliği', 'category': 'Çevresel'},
            {'name': 'Su Yönetimi', 'category': 'Çevresel'},
            {'name': 'Atık Yönetimi', 'category': 'Çevresel'},
            {'name': 'Biyoçeşitlilik', 'category': 'Çevresel'},
            {'name': 'İş Sağlığı ve Güvenliği', 'category': 'Sosyal'},
            {'name': 'Çalışan Hakları', 'category': 'Sosyal'},
            {'name': 'Çeşitlilik ve Kapsayıcılık', 'category': 'Sosyal'},
            {'name': 'Toplum İlişkileri', 'category': 'Sosyal'},
            {'name': 'Etik ve Uyum', 'category': 'Yönetişim'},
            {'name': 'Veri Güvenliği', 'category': 'Yönetişim'},
            {'name': 'Tedarik Zinciri Yönetimi', 'category': 'Ekonomik'},
            {'name': 'İnovasyon', 'category': 'Ekonomik'}
        ]

