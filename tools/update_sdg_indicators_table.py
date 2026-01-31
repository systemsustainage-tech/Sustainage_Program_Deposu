#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Indicators Tablosunu Güncelleme
Eksik sütunları ekler
"""

import logging
import os
import sqlite3
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SDGIndicatorsTableUpdater:
    """SDG Indicators tablosu güncelleyici"""
    
    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.db_path = os.path.join(base_dir, db_path)
        else:
            self.db_path = db_path
    
    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)
    
    def update_table(self) -> None:
        """Tabloyu güncelle"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Eksik sütunları ekle
            new_columns = [
                "data_source TEXT",
                "measurement_frequency TEXT",
                "related_sectors TEXT",
                "related_funds TEXT",
                "kpi_metric TEXT",
                "implementation_requirement TEXT",
                "notes TEXT",
                "request_status TEXT",
                "status TEXT",
                "progress_percentage REAL",
                "completeness_percentage REAL",
                "policy_document_exists TEXT",
                "data_quality TEXT",
                "incentive_readiness_score REAL",
                "readiness_level TEXT"
            ]
            
            for column in new_columns:
                try:
                    cursor.execute(f"ALTER TABLE sdg_indicators ADD COLUMN {column}")
                    logging.info(f"Sutun eklendi: {column}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        logging.info(f"Sutun zaten mevcut: {column}")
                    else:
                        logging.error(f"Sutun eklenirken hata: {e}")
            
            conn.commit()
            conn.close()
            
            logging.info("Tablo basariyla guncellendi!")
            return True
            
        except Exception as e:
            logging.error(f"Tablo guncellenirken hata: {e}")
            return False

if __name__ == "__main__":
    updater = SDGIndicatorsTableUpdater()
    success = updater.update_table()
    if success:
        logging.info("Tablo hazir!")
    else:
        logging.info("Tablo guncelleme basarisiz!")
