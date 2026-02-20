#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eğitim ve Geliştirme Modülü
Çalışan eğitimleri, geliştirme programları ve performans yönetimi
GRI 404
"""

import logging
import os
from typing import Dict


try:
    from utils.language_manager import LanguageManager
except ImportError:
    from backend.utils.language_manager import LanguageManager


from backend.core.base_manager import BaseTenantManager

class TrainingMetrics(BaseTenantManager):
    """Eğitim ve geliştirme metrikleri"""

    def __init__(self, db_path: str = None) -> None:
        super().__init__()
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Eğitim tabloları"""
        try:
            self.execute_update("""
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
            """, params=(), company_id=None, skip_filter=True)

            self.execute_update("""
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
            """, params=(), company_id=None, skip_filter=True)

            # print(self.lm.tr('training_tables_ready', "[OK] Egitim tablolari hazir"))
        except Exception as e:
            logging.error(f"{self.lm.tr('training_table_error', '[HATA] Egitim tablo')}: {e}")

    def add_training(self, company_id: int, year: int, program_name: str,
                    participants: int, hours_per_person: float, **kwargs) -> int:
        """Eğitim programı kaydı"""
        try:
            total_hours = participants * hours_per_person
            query = """
                INSERT INTO training_programs 
                (company_id, period_year, program_name, category, participants,
                 hours_per_person, total_hours, cost, gender, position_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (company_id, year, program_name, kwargs.get('category'),
                  participants, hours_per_person, total_hours, kwargs.get('cost'),
                  kwargs.get('gender'), kwargs.get('position_level'))
            
            # execute_update returns rows affected, but we might want lastrowid.
            # BaseTenantManager.execute_update usually returns rows affected.
            # But TenantAwareDB.execute_update returns rows affected.
            # If we need lastrowid, we might need to select it or modify BaseTenantManager.
            # For now, let's just return True/False or check implementation.
            # The original code returns lastrowid.
            # I will use execute_update and then get the last ID if possible, or just return success.
            # Actually, let's stick to the pattern.
            self.execute_update(query, params, company_id=company_id)
            
            # To get last ID, we can query it.
            rows = self.execute_query("SELECT last_insert_rowid() as id", (), company_id=company_id)
            return rows[0]['id'] if rows else 0
            
        except Exception as e:
            logging.error(f"Add training error: {e}")
            return 0

    def add_performance_review(self, company_id: int, year: int, reviewed: int,
                              total: int, **kwargs) -> int:
        """Performans değerlendirme kaydı"""
        try:
            query = """
                INSERT INTO performance_reviews 
                (company_id, period_year, reviewed_employees, total_employees,
                 gender, position_level)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (company_id, year, reviewed, total,
                  kwargs.get('gender'), kwargs.get('position_level'))
            
            self.execute_update(query, params, company_id=company_id)
            
            rows = self.execute_query("SELECT last_insert_rowid() as id", (), company_id=company_id)
            return rows[0]['id'] if rows else 0
        except Exception as e:
            logging.error(f"Add performance review error: {e}")
            return 0

    def get_summary(self, company_id: int, year: int) -> Dict:
        """Yıllık eğitim özeti"""
        try:
            # Eğitim istatistikleri
            rows_training = self.execute_query("""
                SELECT 
                    COUNT(DISTINCT program_name) as programs,
                    SUM(participants) as total_participants,
                    SUM(total_hours) as total_hours,
                    AVG(hours_per_person) as avg_hours
                FROM training_programs
                WHERE company_id=? AND period_year=?
            """, (company_id, year), company_id=company_id)
            
            row = rows_training[0] if rows_training else {}

            # Performans değerlendirme
            rows_perf = self.execute_query("""
                SELECT SUM(reviewed_employees) as reviewed, SUM(total_employees) as total
                FROM performance_reviews
                WHERE company_id=? AND period_year=?
            """, (company_id, year), company_id=company_id)
            
            perf = rows_perf[0] if rows_perf else {}
            
            reviewed = perf.get('reviewed') or 0
            total = perf.get('total') or 0

            review_rate = 0
            if total and total > 0:
                review_rate = (reviewed / total * 100)

            return {
                'training_programs': int(row.get('programs') or 0),
                'total_participants': int(row.get('total_participants') or 0),
                'total_hours': round(row.get('total_hours') or 0, 2),
                'avg_hours_per_employee': round(row.get('avg_hours') or 0, 2),
                'reviewed_employees': int(reviewed),
                'review_rate_percent': round(review_rate, 2),
                'year': year
            }
        except Exception as e:
            logging.error(f"Get summary error: {e}")
            return {}


