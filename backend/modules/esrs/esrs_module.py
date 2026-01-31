#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ESRS (European Sustainability Reporting Standards) Modulu
Avrupa Surdurulebilirlik Raporlama Standartlari
"""

import logging
import os
import sqlite3
from typing import Dict, List

from utils.language_manager import LanguageManager
from config.database import DB_PATH


class ESRSModule:
    """ESRS modulu yonetimi"""

    def __init__(self, db_path: str = DB_PATH):
        self.lm = LanguageManager()
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)

        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        """ESRS tablolarini olustur"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            # ESRS konulari
            cur.execute("""
                CREATE TABLE IF NOT EXISTS esrs_topics (
                    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    code TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    UNIQUE(code)
                )
            """)

            # ESRS veri noktalari
            cur.execute("""
                CREATE TABLE IF NOT EXISTS esrs_datapoints (
                    datapoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_code TEXT,
                    datapoint_code TEXT,
                    datapoint_name TEXT,
                    datapoint_type TEXT,
                    FOREIGN KEY (topic_code) REFERENCES esrs_topics(code)
                )
            """)

            # ESRS sirket verileri
            cur.execute("""
                CREATE TABLE IF NOT EXISTS esrs_company_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    topic_code TEXT,
                    datapoint_code TEXT,
                    value TEXT,
                    year INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Varsayılan konuları ekle
            topics = [
                (self.lm.tr('environment', 'Cevre'), 'E1', self.lm.tr('climate_change', 'Iklim Degisikligi'), self.lm.tr('e1_desc', 'Sera gazi emisyonlari ve iklim eylemi')),
                (self.lm.tr('social', 'Sosyal'), 'S1', self.lm.tr('own_workforce', 'Kendi Isgucu'), self.lm.tr('s1_desc', 'Calisanlar ve calisma kosullari')),
                (self.lm.tr('governance', 'Yonetisim'), 'G1', self.lm.tr('corporate_governance', 'Kurumsal Yonetisim'), self.lm.tr('g1_desc', 'Yonetim yapisi ve uygulamalari'))
            ]

            for category, code, title, desc in topics:
                cur.execute("""
                    INSERT OR IGNORE INTO esrs_topics (category, code, title, description)
                    VALUES (?, ?, ?, ?)
                """, (category, code, title, desc))

            conn.commit()
            logging.info(f"[OK] {self.lm.tr('esrs_tables_ready', 'ESRS tablolari hazir')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('esrs_tables_create_error', 'ESRS tablolari olusturulamadi')}: {e}")
        finally:
            conn.close()

    def get_all_topics(self) -> List[Dict]:
        """Tum ESRS konularini getir"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            cur.execute("SELECT * FROM esrs_topics ORDER BY code")
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('esrs_topics_fetch_error', 'ESRS konulari alinamadi')}: {e}")
            return []
        finally:
            conn.close()

    def get_company_data(self, company_id: int, topic_code: str, year: int) -> List[Dict]:
        """Sirket verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT * FROM esrs_company_data 
                WHERE company_id = ? AND topic_code = ? AND year = ?
            """, (company_id, topic_code, year))
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('esrs_data_fetch_error', 'ESRS verileri alinamadi')}: {e}")
            return []
        finally:
            conn.close()

    def save_data(self, company_id: int, topic_code: str, datapoint_code: str, value: str, year: int) -> bool:
        """ESRS veri kaydet"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO esrs_company_data (company_id, topic_code, datapoint_code, value, year)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, topic_code, datapoint_code, value, year))

            conn.commit()
            return True
        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('esrs_data_save_error', 'ESRS veri kaydedilemedi')}: {e}")
            return False
        finally:
            conn.close()

