#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SASB Manager - Sustainability Accounting Standards Board
"""

import logging
import os
import sqlite3
from typing import Dict, List, Optional

from config.database import DB_PATH

class SASBManager:
    """SASB Standartları yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """SASB tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
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
            """)
            conn.commit()
        except Exception as e:
            logging.error(f"SASB table init error: {e}")
        finally:
            conn.close()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard istatistiklerini getir"""
        stats = {
            'total_metrics': 0,
            'topics_covered': 0,
            'completion_rate': 0
        }
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute("SELECT topic FROM sasb_disclosures WHERE company_id = ?", (company_id,)).fetchall()
            stats['total_metrics'] = len(rows)
            stats['topics_covered'] = len(set([r[0] for r in rows]))
            # Mock completion (assuming ~10 key metrics per sector)
            stats['completion_rate'] = min(100, int((stats['total_metrics'] / 10) * 100))
        except Exception as e:
            logging.error(f"SASB stats error: {e}")
        finally:
            conn.close()
        return stats

    def get_disclosures(self, company_id: int) -> List[Dict]:
        """Tüm açıklamaları getir"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        disclosures = []
        try:
            rows = conn.execute("SELECT * FROM sasb_disclosures WHERE company_id = ? ORDER BY created_at DESC", (company_id,)).fetchall()
            disclosures = [dict(r) for r in rows]
        except Exception as e:
            logging.error(f"SASB disclosures error: {e}")
        finally:
            conn.close()
        return disclosures

    def add_disclosure(self, company_id: int, year: int, topic: str, metric: str, value: str, unit: str) -> bool:
        """Yeni açıklama ekle"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                INSERT INTO sasb_disclosures (company_id, year, topic, metric, value, unit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, year, topic, metric, value, unit))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"SASB add disclosure error: {e}")
            return False
        finally:
            conn.close()
