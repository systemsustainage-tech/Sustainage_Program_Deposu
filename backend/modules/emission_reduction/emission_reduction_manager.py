#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emisyon Azaltma Projeleri Yöneticisi
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

class EmissionReductionManager(BaseTenantManager):
    """Emisyon azaltma projeleri yönetimi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        super().__init__(db_path, company_id)
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Gerekli tabloları oluştur"""
        try:
            # Emisyon azaltma projeleri tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS emission_reduction_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    expected_reduction REAL DEFAULT 0.0,
                    actual_reduction REAL DEFAULT 0.0,
                    progress_percentage REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'Aktif',
                    budget REAL DEFAULT 0.0,
                    responsible_person TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies (id)
                )
            """, skip_tenant_filter=True)

            # İlerleme kayıtları tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS emission_reduction_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    reduction_amount REAL DEFAULT 0.0,
                    notes TEXT,
                    recorded_by TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES emission_reduction_projects (id)
                )
            """, skip_tenant_filter=True)
            
        except Exception as e:
            logging.error(f"Emisyon azaltma tabloları oluşturulamadı: {e}")
