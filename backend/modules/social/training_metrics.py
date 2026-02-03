#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eğitim ve Geliştirme Modülü
Çalışan eğitimleri, geliştirme programları ve performans yönetimi
GRI 404
"""

import logging
import os
import sqlite3
from typing import Dict


try:
    from utils.language_manager import LanguageManager
except ImportError:
    from backend.utils.language_manager import LanguageManager


class TrainingMetrics:
    """Eğitim ve geliştirme metrikleri"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self.lm = LanguageManager()
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Eğitim tabloları"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_programs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    program_name TEXT NOT NULL,
                    category TEXT,
                    participants INTEGER DEFAULT 0,
                    hours_per_person REAL DEFAULT 0,
                    total_hours REAL,
                    cost REAL,
                    gender TEXT,
                    position_level TEXT,
                    supplier TEXT,
                    invoice_date TEXT,
                    payment_due_date TEXT,
                    currency TEXT DEFAULT 'TRY',
                    total_cost REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER NOT NULL,
                    reviewed_employees INTEGER DEFAULT 0,
                    total_employees INTEGER,
                    gender TEXT,
                    position_level TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            # print(self.lm.tr('training_tables_ready', "[OK] Egitim tablolari hazir"))
        except Exception as e:
            logging.error(f"{self.lm.tr('training_table_error', '[HATA] Egitim tablo')}: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_training(self, company_id: int, year: int, program_name: str,
                    participants: int, hours_per_person: float, **kwargs) -> int:
        """Eğitim programı kaydı"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            total_hours = participants * hours_per_person
            cursor.execute("""
                INSERT INTO training_programs 
                (company_id, period_year, program_name, category, participants,
                 hours_per_person, total_hours, cost, gender, position_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, program_name, kwargs.get('category'),
                  participants, hours_per_person, total_hours, kwargs.get('cost'),
                  kwargs.get('gender'), kwargs.get('position_level')))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def add_performance_review(self, company_id: int, year: int, reviewed: int,
                              total: int, **kwargs) -> int:
        """Performans değerlendirme kaydı"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO performance_reviews 
                (company_id, period_year, reviewed_employees, total_employees,
                 gender, position_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, year, reviewed, total,
                  kwargs.get('gender'), kwargs.get('position_level')))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def get_summary(self, company_id: int, year: int) -> Dict:
        """Yıllık eğitim özeti"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            # Eğitim istatistikleri
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT program_name) as programs,
                    SUM(participants) as total_participants,
                    SUM(total_hours) as total_hours,
                    AVG(hours_per_person) as avg_hours
                FROM training_programs
                WHERE company_id=? AND period_year=?
            """, (company_id, year))
            row = cursor.fetchone()

            # Performans değerlendirme
            cursor.execute("""
                SELECT SUM(reviewed_employees), SUM(total_employees)
                FROM performance_reviews
                WHERE company_id=? AND period_year=?
            """, (company_id, year))
            perf = cursor.fetchone()

            review_rate = 0
            if perf[1] and perf[1] > 0:
                review_rate = (perf[0] / perf[1] * 100)

            return {
                'training_programs': int(row[0] or 0),
                'total_participants': int(row[1] or 0),
                'total_hours': round(row[2] or 0, 2),
                'avg_hours_per_employee': round(row[3] or 0, 2),
                'reviewed_employees': int(perf[0] or 0),
                'review_rate_percent': round(review_rate, 2),
                'year': year
            }
        finally:
            conn.close()

