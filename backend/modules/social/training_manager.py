#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eğitim Yönetimi Modülü
Çalışan eğitimleri, sertifikasyonlar ve gelişim programları
Refactored for Multi-tenancy using BaseTenantManager
"""

import logging
from typing import Dict, Optional, List
from datetime import datetime

from config.settings import ensure_directories, get_db_path
try:
    from utils.language_manager import LanguageManager
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    from backend.utils.language_manager import LanguageManager
    from backend.core.base_manager import BaseTenantManager


class TrainingManager(BaseTenantManager):
    """Eğitim yönetimi ve gelişim programları"""

    def __init__(self, db_path: str | None = None, company_id: Optional[int] = None) -> None:
        if db_path:
            final_db_path = db_path
        else:
            ensure_directories()
            final_db_path = get_db_path()
            
        super().__init__(final_db_path, company_id)
        self.lm = LanguageManager()
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Eğitim yönetimi tablolarını oluştur"""
        try:
            # Mevcut şema:
            # company_id, period_year, program_name, category, participants, 
            # hours_per_person, total_hours, cost, gender, position_level, created_at
            
            self.execute_update("""
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
                    self.execute_update(f"ALTER TABLE training_programs ADD COLUMN {col_name} {col_type}")
                except Exception:
                    pass # Sütun zaten var

            self.execute_update("""
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

        except Exception as e:
            logging.error(f"{self.lm.tr('training_manager_table_error', '[HATA] Egitim yonetimi modulu tablo olusturma')}: {e}")

    def check_program_exists(self, company_id: int, program_name: str, period_year: int) -> bool:
        """Check if a training program already exists"""
        try:
            count = self.count(
                'training_programs', 
                company_id=company_id,
                where="program_name = ? AND period_year = ?",
                params=(program_name, period_year)
            )
            return count > 0
        except Exception:
            return False

    def add_training_program(self, company_id: int, program_name: str, program_type: str,
                           target_audience: str = None, duration_hours: float = None,
                           cost_per_participant: float = None, max_participants: int = None,
                           supplier: str = None, invoice_date: str = None, 
                           payment_due_date: str = None, currency: str = 'TRY',
                           total_cost: float = None, period_year: int = None) -> bool:
        """Eğitim programı ekle"""
        if period_year is None:
            period_year = datetime.now().year

        try:
            # Mapping:
            # program_type -> category
            # duration_hours -> hours_per_person
            # cost_per_participant -> cost
            # max_participants -> participants
            
            data = {
                'program_name': program_name,
                'category': program_type,
                'position_level': target_audience,
                'hours_per_person': duration_hours,
                'cost': cost_per_participant,
                'participants': max_participants,
                'supplier': supplier,
                'invoice_date': invoice_date,
                'payment_due_date': payment_due_date,
                'currency': currency,
                'total_cost': total_cost,
                'period_year': period_year
            }
            
            self.insert('training_programs', data, company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('training_program_add_error', 'Eğitim programı ekleme hatası')}: {e}")
            return False

    def add_certification(self, company_id: int, employee_id: int, certification_name: str,
                         issuing_authority: str = None, issue_date: str = None,
                         expiry_date: str = None, renewal_required: str = None) -> bool:
        """Sertifika ekle"""
        try:
            data = {
                'employee_id': employee_id,
                'certification_name': certification_name,
                'issuing_authority': issuing_authority,
                'issue_date': issue_date,
                'expiry_date': expiry_date,
                'renewal_required': renewal_required
            }
            
            self.insert('employee_certifications', data, company_id=company_id)
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('certification_add_error', 'Sertifika ekleme hatası')}: {e}")
            return False

    def get_training_summary(self, company_id: int) -> Dict:
        """Eğitim özeti getir"""
        try:
            # Not: execute_query direkt SQL çalıştırır, company_id filtresini manuel eklemeliyiz.
            rows = self.execute_query("""
                SELECT category, COUNT(*), AVG(hours_per_person), AVG(cost)
                FROM training_programs 
                WHERE company_id = ? 
                GROUP BY category
            """, (company_id,))

            training_summary = {}
            for row in rows:
                program_type, count, avg_duration, avg_cost = row
                training_summary[program_type] = {
                    'program_count': count,
                    'average_duration': avg_duration if avg_duration else 0,
                    'average_cost': avg_cost if avg_cost else 0
                }

            cert_rows = self.execute_query("""
                SELECT COUNT(*), COUNT(DISTINCT employee_id)
                FROM employee_certifications 
                WHERE company_id = ? AND status = 'active'
            """, (company_id,))

            if cert_rows:
                total_certifications = cert_rows[0]['COUNT(*)'] if isinstance(cert_rows[0], dict) else cert_rows[0][0]
                certified_employees = cert_rows[0]['COUNT(DISTINCT employee_id)'] if isinstance(cert_rows[0], dict) else cert_rows[0][1]
            else:
                total_certifications = 0
                certified_employees = 0

            return {
                'training_summary': training_summary,
                'total_certifications': total_certifications,
                'certified_employees': certified_employees,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"{self.lm.tr('training_summary_error', 'Eğitim özeti getirme hatası')}: {e}")
            return {}
