#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Çeşitlilik Yönetimi Modülü
Çeşitlilik ve kapsayıcılık metrikleri
"""

import logging
import os
import sqlite3
from typing import Dict
from config.database import DB_PATH


class DiversityManager:
    """Çeşitlilik ve kapsayıcılık yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Çeşitlilik yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
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
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inclusion_initiatives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    initiative_name TEXT NOT NULL,
                    initiative_type TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    budget REAL,
                    participants INTEGER,
                    success_metrics TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Cesitlilik yonetimi modulu tablolari basariyla olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Cesitlilik yonetimi modulu tablo olusturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_diversity_metric(self, company_id: int, year: int, metric_category: str,
                           metric_name: str, metric_value: float, target_value: float = None,
                           benchmark_value: float = None) -> bool:
        """Çeşitlilik metrik ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO diversity_metrics 
                (company_id, year, metric_category, metric_name, metric_value, target_value, benchmark_value)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, metric_category, metric_name, metric_value, target_value, benchmark_value))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Çeşitlilik metrik ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_inclusion_initiative(self, company_id: int, initiative_name: str, initiative_type: str,
                               start_date: str = None, end_date: str = None, budget: float = None,
                               participants: int = None, success_metrics: str = None) -> bool:
        """Kapsayıcılık girişimi ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO inclusion_initiatives 
                (company_id, initiative_name, initiative_type, start_date, end_date,
                 budget, participants, success_metrics)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, initiative_name, initiative_type, start_date, end_date,
                  budget, participants, success_metrics))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Kapsayıcılık girişimi ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_diversity_summary(self, company_id: int, year: int) -> Dict:
        """Çeşitlilik özeti getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT metric_category, metric_name, metric_value, target_value, benchmark_value
                FROM diversity_metrics 
                WHERE company_id = ? AND year = ?
                ORDER BY metric_category, metric_name
            """, (company_id, year))

            diversity_metrics = {}
            for row in cursor.fetchall():
                category, name, value, target, benchmark = row
                if category not in diversity_metrics:
                    diversity_metrics[category] = {}
                diversity_metrics[category][name] = {
                    'value': value,
                    'target': target,
                    'benchmark': benchmark
                }

            cursor.execute("""
                SELECT initiative_type, COUNT(*), SUM(budget), SUM(participants)
                FROM inclusion_initiatives 
                WHERE company_id = ? AND status = 'active'
                GROUP BY initiative_type
            """, (company_id,))

            initiatives_summary = {}
            for row in cursor.fetchall():
                init_type, count, total_budget, total_participants = row
                initiatives_summary[init_type] = {
                    'count': count,
                    'total_budget': total_budget,
                    'total_participants': total_participants
                }

            return {
                'diversity_metrics': diversity_metrics,
                'initiatives_summary': initiatives_summary,
                'year': year,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"Çeşitlilik özeti getirme hatası: {e}")
            return {}
        finally:
            conn.close()
