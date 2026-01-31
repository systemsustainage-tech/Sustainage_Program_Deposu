#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Kalite Yönetimi Modülü
Veri kalite skorlama ve iyileştirme
"""

import logging
import os
import sqlite3
from typing import Dict
from config.database import DB_PATH


class DataQualityManager:
    """Veri kalite yönetimi ve skorlama"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Veri kalite tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_quality_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assessment_date TEXT NOT NULL,
                    data_category TEXT NOT NULL,
                    completeness_score REAL,
                    accuracy_score REAL,
                    consistency_score REAL,
                    timeliness_score REAL,
                    validity_score REAL,
                    overall_score REAL,
                    improvement_areas TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_validation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    rule_name TEXT NOT NULL,
                    rule_description TEXT NOT NULL,
                    rule_category TEXT NOT NULL,
                    validation_query TEXT,
                    error_threshold REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Veri kalite yonetimi modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Veri kalite yonetimi modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def calculate_data_quality_score(self, company_id: int, data_category: str) -> Dict:
        """Veri kalite skoru hesapla"""
        # Bu fonksiyon gerçek veri analizi yaparak kalite skorlarını hesaplar
        # Şimdilik örnek değerler döndürüyor

        completeness_score = 85.0
        accuracy_score = 92.0
        consistency_score = 88.0
        timeliness_score = 90.0
        validity_score = 94.0

        overall_score = (completeness_score + accuracy_score + consistency_score +
                        timeliness_score + validity_score) / 5

        improvement_areas = []
        if completeness_score < 90:
            improvement_areas.append("Veri eksikliği giderilmeli")
        if accuracy_score < 95:
            improvement_areas.append("Veri doğruluğu artırılmalı")
        if consistency_score < 90:
            improvement_areas.append("Veri tutarlılığı iyileştirilmeli")

        return {
            'completeness_score': completeness_score,
            'accuracy_score': accuracy_score,
            'consistency_score': consistency_score,
            'timeliness_score': timeliness_score,
            'validity_score': validity_score,
            'overall_score': overall_score,
            'improvement_areas': improvement_areas,
            'data_category': data_category,
            'company_id': company_id
        }

    def add_data_quality_assessment(self, company_id: int, assessment_date: str,
                                  data_category: str, completeness_score: float,
                                  accuracy_score: float, consistency_score: float,
                                  timeliness_score: float, validity_score: float,
                                  improvement_areas: str = None) -> bool:
        """Veri kalite değerlendirmesi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            overall_score = (completeness_score + accuracy_score + consistency_score +
                           timeliness_score + validity_score) / 5

            cursor.execute("""
                INSERT INTO data_quality_scores 
                (company_id, assessment_date, data_category, completeness_score,
                 accuracy_score, consistency_score, timeliness_score, validity_score,
                 overall_score, improvement_areas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, assessment_date, data_category, completeness_score,
                  accuracy_score, consistency_score, timeliness_score, validity_score,
                  overall_score, improvement_areas))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Veri kalite değerlendirmesi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_data_quality_summary(self, company_id: int) -> Dict:
        """Veri kalite özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT data_category, AVG(overall_score), COUNT(*), MAX(assessment_date)
                FROM data_quality_scores 
                WHERE company_id = ?
                GROUP BY data_category
                ORDER BY AVG(overall_score) DESC
            """, (company_id,))

            quality_summary = {}
            for row in cursor.fetchall():
                category, avg_score, count, last_assessment = row
                quality_summary[category] = {
                    'average_score': avg_score,
                    'assessment_count': count,
                    'last_assessment': last_assessment
                }

            return {
                'quality_summary': quality_summary,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"Veri kalite özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()
