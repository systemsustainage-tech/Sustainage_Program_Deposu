#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eğitim Yönetimi Modülü
Çalışan eğitimleri, sertifikasyonlar ve gelişim programları
"""

import logging
import sqlite3
from typing import Dict
from datetime import datetime

from config.settings import ensure_directories, get_db_path
try:
    from utils.language_manager import LanguageManager
except ImportError:
    from backend.utils.language_manager import LanguageManager


class TrainingManager:
    """Eğitim yönetimi ve gelişim programları"""

    def __init__(self, db_path: str | None = None) -> None:
        if db_path:
            self.db_path = db_path
        else:
            ensure_directories()
            self.db_path = get_db_path()
        self.lm = LanguageManager()
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Eğitim yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Mevcut şema:
            # company_id, period_year, program_name, category, participants, 
            # hours_per_person, total_hours, cost, gender, position_level, created_at
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_programs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period_year INTEGER,
                    program_name TEXT NOT NULL,
                    category TEXT,
                    participants INTEGER DEFAULT 0,
                    hours_per_person REAL DEFAULT 0,
                    total_hours REAL,
                    cost REAL,
                    gender TEXT,
                    position_level TEXT,
                    status TEXT DEFAULT 'active',
                    supplier TEXT,
                    invoice_date TEXT,
                    payment_due_date TEXT,
                    currency TEXT DEFAULT 'TRY',
                    total_cost REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Mevcut tabloya yeni sütunları ekle (Migration)
            columns_to_add = [
                ("supplier", "TEXT"),
                ("invoice_date", "TEXT"),
                ("payment_due_date", "TEXT"),
                ("currency", "TEXT DEFAULT 'TRY'"),
                ("total_cost", "REAL"),
                ("status", "TEXT DEFAULT 'active'")
            ]
            
            for col_name, col_type in columns_to_add:
                try:
                    cursor.execute(f"ALTER TABLE training_programs ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError:
                    pass # Sütun zaten var

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee_certifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    employee_id INTEGER NOT NULL,
                    certification_name TEXT NOT NULL,
                    issuing_authority TEXT,
                    issue_date TEXT,
                    expiry_date TEXT,
                    renewal_required TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            # print(self.lm.tr('training_manager_tables_success', "[OK] Egitim yonetimi modulu tablolari basariyla olusturuldu"))

        except Exception as e:
            logging.error(f"{self.lm.tr('training_manager_table_error', '[HATA] Egitim yonetimi modulu tablo olusturma')}: {e}")
            conn.rollback()
        finally:
            conn.close()

    def check_program_exists(self, company_id: int, program_name: str, period_year: int) -> bool:
        """Check if a training program already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT 1 FROM training_programs 
                WHERE company_id = ? AND program_name = ? AND period_year = ?
            """, (company_id, program_name, period_year))
            return cursor.fetchone() is not None
        except Exception:
            return False
        finally:
            conn.close()

    def add_training_program(self, company_id: int, program_name: str, program_type: str,
                           target_audience: str = None, duration_hours: float = None,
                           cost_per_participant: float = None, max_participants: int = None,
                           supplier: str = None, invoice_date: str = None, 
                           payment_due_date: str = None, currency: str = 'TRY',
                           total_cost: float = None, period_year: int = None) -> bool:
        """Eğitim programı ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if period_year is None:
            period_year = datetime.now().year

        try:
            # Mapping:
            # program_type -> category
            # duration_hours -> hours_per_person
            # cost_per_participant -> cost
            # max_participants -> participants
            
            cursor.execute("""
                INSERT INTO training_programs 
                (company_id, program_name, category, position_level,
                 hours_per_person, cost, participants,
                 supplier, invoice_date, payment_due_date, currency, total_cost, period_year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, program_name, program_type, target_audience,
                  duration_hours, cost_per_participant, max_participants,
                  supplier, invoice_date, payment_due_date, currency, total_cost, period_year))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('training_program_add_error', 'Eğitim programı ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_certification(self, company_id: int, employee_id: int, certification_name: str,
                         issuing_authority: str = None, issue_date: str = None,
                         expiry_date: str = None, renewal_required: str = None) -> bool:
        """Sertifika ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO employee_certifications 
                (company_id, employee_id, certification_name, issuing_authority,
                 issue_date, expiry_date, renewal_required)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, employee_id, certification_name, issuing_authority,
                  issue_date, expiry_date, renewal_required))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('certification_add_error', 'Sertifika ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_training_summary(self, company_id: int) -> Dict:
        """Eğitim özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT category, COUNT(*), AVG(hours_per_person), AVG(cost)
                FROM training_programs 
                WHERE company_id = ? 
                GROUP BY category
            """, (company_id,))

            training_summary = {}
            for row in cursor.fetchall():
                program_type, count, avg_duration, avg_cost = row
                training_summary[program_type] = {
                    'program_count': count,
                    'average_duration': avg_duration if avg_duration else 0,
                    'average_cost': avg_cost if avg_cost else 0
                }

            cursor.execute("""
                SELECT COUNT(*), COUNT(DISTINCT employee_id)
                FROM employee_certifications 
                WHERE company_id = ? AND status = 'active'
            """, (company_id,))

            cert_result = cursor.fetchone()
            total_certifications = cert_result[0] or 0
            certified_employees = cert_result[1] or 0

            return {
                'training_summary': training_summary,
                'total_certifications': total_certifications,
                'certified_employees': certified_employees,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"{self.lm.tr('training_summary_error', 'Eğitim özeti getirme hatası')}: {e}")
            return {}
        finally:
            conn.close()
