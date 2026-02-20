#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Çeşitlilik Yönetimi Modülü
Çeşitlilik ve kapsayıcılık metrikleri
"""

import logging
import os
import sqlite3
from typing import Dict, List, Optional

try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    try:
        from core.base_manager import BaseTenantManager
    except ImportError:
        import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from backend.core.base_manager import BaseTenantManager

class DiversityManager(BaseTenantManager):
    """Çeşitlilik ve kapsayıcılık yönetimi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Çeşitlilik yönetimi tablolarını oluştur"""
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS diversity_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    metric_category TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    target_value REAL,
                    benchmark_value REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)

            self.execute_update("""
                CREATE TABLE IF NOT EXISTS inclusion_initiatives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    initiative_name TEXT NOT NULL,
                    description TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    status TEXT DEFAULT 'Planned',
                    budget REAL DEFAULT 0.0,
                    impact_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)
            
        except Exception as e:
            logging.error(f"Çeşitlilik tabloları oluşturulamadı: {e}")
