#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SASB Manager - Sustainability Accounting Standards Board
"""

import logging
import os
from typing import Dict, List, Optional

try:
    from backend.config.database import DB_PATH
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    from config.database import DB_PATH
    from core.base_manager import BaseTenantManager

class SASBManager(BaseTenantManager):
    """SASB Standartları yönetimi"""

    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
            db_path = os.path.join(base_dir, db_path)
        
        super().__init__(db_path, company_id)
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """SASB tablolarını oluştur"""
        try:
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS sasb_disclosures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER,
                    topic TEXT,
                    metric TEXT,
                    value TEXT,
                    unit TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """, skip_tenant_filter=True)
        except Exception as e:
            logging.error(f"SASB table init error: {e}")

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard istatistiklerini getir"""
        stats = {
            'total_metrics': 0,
            'topics_covered': 0,
            'completion_rate': 0
        }
        try:
            # BaseTenantManager handles filtering automatically if we don't pass company_id explicitly
            # But get_dashboard_stats takes company_id as arg.
            # We can use execute_query with explicit company_id or set context.
            # Assuming execute_query uses self.company_id if set, or we can pass it.
            # Since method arg is company_id, let's use it.
            
            # Using execute_query which handles connection
            rows = self.execute_query("SELECT topic FROM sasb_disclosures WHERE company_id = ?", (company_id,), company_id=company_id)
            stats['total_metrics'] = len(rows)
            stats['topics_covered'] = len(set([r['topic'] for r in rows]))
            # Mock completion (assuming ~10 key metrics per sector)
            stats['completion_rate'] = min(100, int((stats['total_metrics'] / 10) * 100))
        except Exception as e:
            logging.error(f"SASB stats error: {e}")
        return stats

    def get_disclosures(self, company_id: int) -> List[Dict]:
        """Tüm açıklamaları getir"""
        disclosures = []
        try:
            rows = self.execute_query("SELECT * FROM sasb_disclosures WHERE company_id = ? ORDER BY created_at DESC", (company_id,), company_id=company_id)
            disclosures = [dict(r) for r in rows]
        except Exception as e:
            logging.error(f"SASB disclosures error: {e}")
        return disclosures

    def add_disclosure(self, company_id: int, year: int, topic: str, metric: str, value: str, unit: str) -> bool:
        """Yeni açıklama ekle"""
        try:
            self.execute_update("""
                INSERT INTO sasb_disclosures (company_id, year, topic, metric, value, unit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, year, topic, metric, value, unit), company_id=company_id)
            return True
        except Exception as e:
            logging.error(f"SASB add disclosure error: {e}")
            return False
