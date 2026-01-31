#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ekonomik Performans Metrikleri
GRI 201 - Ekonomik değer üretimi ve dağıtımı
"""

import logging
import os
import sqlite3
from typing import Dict


from utils.language_manager import LanguageManager


class EconomicMetrics:
    """Ekonomik performans metrikleri"""

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')
        self.lm = LanguageManager()
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Ekonomik tablolar"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS economic_value (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    revenue REAL DEFAULT 0,
                    operating_costs REAL DEFAULT 0,
                    employee_wages REAL DEFAULT 0,
                    payments_capital REAL DEFAULT 0,
                    payments_government REAL DEFAULT 0,
                    community_investments REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, year)
                )
            """)
            conn.commit()
        except Exception as e:
            logging.error(f"{self.lm.tr('economic_table_error', '[HATA] Ekonomik tablo')}: {e}")
        finally:
            conn.close()

    def set_economic_value(self, company_id: int, year: int, **kwargs) -> bool:
        """
        Ekonomik değer kaydet
        
        Args:
            revenue: Gelir
            operating_costs: İşletme maliyetleri
            employee_wages: Çalışan ücretleri
            payments_capital: Sermaye ödemeleri
            payments_government: Devlete ödemeler (vergi)
            community_investments: Toplum yatırımları
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO economic_value 
                (company_id, year, revenue, operating_costs, employee_wages,
                 payments_capital, payments_government, community_investments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id, year) DO UPDATE SET
                    revenue=excluded.revenue,
                    operating_costs=excluded.operating_costs,
                    employee_wages=excluded.employee_wages,
                    payments_capital=excluded.payments_capital,
                    payments_government=excluded.payments_government,
                    community_investments=excluded.community_investments
            """, (company_id, year,
                  kwargs.get('revenue', 0),
                  kwargs.get('operating_costs', 0),
                  kwargs.get('employee_wages', 0),
                  kwargs.get('payments_capital', 0),
                  kwargs.get('payments_government', 0),
                  kwargs.get('community_investments', 0)))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"[HATA] Ekonomik veri: {e}")
            return False
        finally:
            conn.close()

    def get_summary(self, company_id: int, year: int) -> Dict:
        """GRI 201-1: Ekonomik değer özeti"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT revenue, operating_costs, employee_wages,
                       payments_capital, payments_government, community_investments
                FROM economic_value
                WHERE company_id=? AND year=?
            """, (company_id, year))

            row = cursor.fetchone()
            if not row:
                return {}

            # Üretilen ekonomik değer
            generated = row[0]

            # Dağıtılan ekonomik değer
            distributed = row[1] + row[2] + row[3] + row[4] + row[5]

            # Elde tutulan
            retained = generated - distributed

            return {
                'generated_value': round(generated, 2),
                'distributed_value': round(distributed, 2),
                'retained_value': round(retained, 2),
                'operating_costs': round(row[1], 2),
                'employee_wages': round(row[2], 2),
                'payments_capital': round(row[3], 2),
                'payments_government': round(row[4], 2),
                'community_investments': round(row[5], 2),
                'year': year
            }
        finally:
            conn.close()

