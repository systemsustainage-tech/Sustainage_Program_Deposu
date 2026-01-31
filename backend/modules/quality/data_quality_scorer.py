#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Kalitesi Skorlama
ESG veri kalitesini 0-100 arası puanlar
"""

import logging
import os
import sqlite3
from typing import Dict


class DataQualityScorer:
    """Veri kalitesi değerlendirme"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Kalite skoru tablosu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_quality_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    completeness_score REAL DEFAULT 0,
                    accuracy_score REAL DEFAULT 0,
                    timeliness_score REAL DEFAULT 0,
                    consistency_score REAL DEFAULT 0,
                    overall_score REAL DEFAULT 0,
                    summary_score REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, year, category)
                )
            """)
            
            # Tasks tablosu (Veri kalitesi hesaplaması için gerekli)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    task_name TEXT NOT NULL,
                    status TEXT DEFAULT 'Bekliyor', -- Tamamlandı, Bekliyor, Devam Ediyor
                    due_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Survey Assignments tablosu (Veri kalitesi hesaplaması için gerekli)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS survey_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    survey_id INTEGER,
                    status TEXT DEFAULT 'Atandı', -- Tamamlandi, Atandı
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
        except Exception as e:
            logging.error(f"[HATA] Kalite tablo: {e}")
        finally:
            conn.close()

    def calculate_score(self, company_id: int, year: int, category: str = 'ESG') -> Dict:
        """
        Veri kalitesi skoru hesapla (0-100)
        
        Kriterler:
        - Completeness (Eksiksizlik): Gerekli alanlar dolu mu?
        - Accuracy (Doğruluk): Değerler mantıklı mı?
        - Timeliness (Güncellik): Veriler güncel mi?
        - Consistency (Tutarlılık): Veriler tutarlı mı?
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 1. Completeness (Eksiksizlik %40)
            completeness = self._calculate_completeness(cursor, company_id, year)

            # 2. Accuracy (Doğruluk %30)
            accuracy = self._calculate_accuracy(cursor, company_id, year)

            # 3. Timeliness (Güncellik %20)
            timeliness = self._calculate_timeliness(cursor, company_id, year)

            # 4. Consistency (Tutarlılık %10)
            consistency = self._calculate_consistency(cursor, company_id, year)

            # Genel skor
            overall = (completeness * 0.4 + accuracy * 0.3 +
                      timeliness * 0.2 + consistency * 0.1)

            # Summary score (ESG genel puanına katkı)
            summary = overall  # Şimdilik aynı, ileride ağırlıklı ortalama

            # Kaydet
            cursor.execute("""
                INSERT INTO data_quality_scores 
                (company_id, year, category, completeness_score, accuracy_score,
                 timeliness_score, consistency_score, overall_score, summary_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id, year, category) DO UPDATE SET
                    completeness_score=excluded.completeness_score,
                    accuracy_score=excluded.accuracy_score,
                    timeliness_score=excluded.timeliness_score,
                    consistency_score=excluded.consistency_score,
                    overall_score=excluded.overall_score,
                    summary_score=excluded.summary_score
            """, (company_id, year, category, completeness, accuracy,
                  timeliness, consistency, overall, summary))

            conn.commit()

            return {
                'completeness': round(completeness, 2),
                'accuracy': round(accuracy, 2),
                'timeliness': round(timeliness, 2),
                'consistency': round(consistency, 2),
                'overall': round(overall, 2),
                'summary_score': round(summary, 2),
                'grade': self._get_grade(overall)
            }

        finally:
            conn.close()

    def _calculate_completeness(self, cursor, company_id: int, year: int) -> float:
        """Eksiksizlik skoru"""
        # Görevlerin tamamlanma oranı
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status='Tamamlandı' THEN 1 END) * 100.0 / COUNT(*)
            FROM tasks WHERE company_id=?
        """, (company_id,))
        task_complete = cursor.fetchone()[0] or 0

        # Anket tamamlanma
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status='Tamamlandi' THEN 1 END) * 100.0 / COUNT(*)
            FROM survey_assignments
        """)
        survey_complete = cursor.fetchone()[0] or 0

        return (task_complete * 0.6 + survey_complete * 0.4)

    def _calculate_accuracy(self, cursor, company_id: int, year: int) -> float:
        """Doğruluk skoru (basitleştirilmiş)"""
        # Şimdilik 80 (gerçekte validasyon kontrolleri yapılır)
        return 80.0

    def _calculate_timeliness(self, cursor, company_id: int, year: int) -> float:
        """Güncellik skoru"""
        # Son 30 günde güncellenen veri oranı
        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE company_id=? AND updated_at > date('now', '-30 days')
        """, (company_id,))
        recent = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM tasks WHERE company_id=?", (company_id,))
        total = cursor.fetchone()[0] or 1

        return min((recent / total * 100), 100)

    def _calculate_consistency(self, cursor, company_id: int, year: int) -> float:
        """Tutarlılık skoru (basitleştirilmiş)"""
        return 85.0

    def _get_grade(self, score: float) -> str:
        """Harf notu"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def get_esg_summary_score(self, company_id: int, year: int) -> float:
        """ESG genel özet skoru"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT AVG(summary_score) FROM data_quality_scores
                WHERE company_id=? AND year=?
            """, (company_id, year))
            score = cursor.fetchone()[0] or 0
            return round(score, 2)
        finally:
            conn.close()

