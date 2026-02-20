#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ekonomik Performans Metrikleri
GRI 201 - Ekonomik değer üretimi ve dağıtımı
"""

import logging
import os
from typing import Dict, Optional
from backend.core.base_manager import BaseTenantManager
from backend.config.database import DB_PATH
from utils.language_manager import LanguageManager


class EconomicMetrics(BaseTenantManager):
    """Ekonomik performans metrikleri"""

    def __init__(self, db_path: Optional[str] = None, company_id: Optional[int] = None) -> None:
        if db_path is None:
            db_path = DB_PATH
        super().__init__(db_path, company_id)
        self.lm = LanguageManager()
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Ekonomik tablolar"""
        try:
            self.execute_update("""
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
        except Exception as e:
            logging.error(f"{self.lm.tr('economic_table_error', '[HATA] Ekonomik tablo')}: {e}")

    def set_economic_value(self, company_id: int, year: int, **kwargs) -> bool:
        """
        Ekonomik değer kaydet
        """
        try:
            self.execute_update("""
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
            return True
        except Exception as e:
            logging.error(f"[HATA] Ekonomik veri: {e}")
            return False

    def get_summary(self, company_id: int, year: int) -> Dict:
        """GRI 201-1: Ekonomik değer özeti"""
        try:
            rows = self.execute_query("""
                SELECT revenue, operating_costs, employee_wages,
                       payments_capital, payments_government, community_investments
                FROM economic_value
                WHERE company_id=? AND year=?
            """, (company_id, year))

            if not rows:
                return {}
            
            row = rows[0]

            # Üretilen ekonomik değer
            generated = row['revenue']

            # Dağıtılan ekonomik değer
            distributed = row['operating_costs'] + row['employee_wages'] + row['payments_capital'] + row['payments_government'] + row['community_investments']

            # Elde tutulan
            retained = generated - distributed

            return {
                'generated_value': round(generated, 2),
                'distributed_value': round(distributed, 2),
                'retained_value': round(retained, 2),
                'operating_costs': round(row['operating_costs'], 2),
                'employee_wages': round(row['employee_wages'], 2),
                'payments_capital': round(row['payments_capital'], 2),
                'payments_government': round(row['payments_government'], 2),
                'community_investments': round(row['community_investments'], 2),
                'year': year
            }
        except Exception as e:
            logging.error(f"[HATA] Ekonomik özet: {e}")
            return {}

