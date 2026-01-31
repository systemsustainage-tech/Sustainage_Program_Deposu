#!/usr/bin/env python3
"""
SDG seçimleri tablosunu ekle
"""

import logging
import os
import sqlite3
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def add_sdg_selections_table() -> None:
    """SDG seçimleri tablosunu ekle"""
    db_path = DB_PATH
    
    # data klasörünün var olduğundan emin ol
    if not os.path.exists("data"):
        os.makedirs("data")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # SDG seçimleri tablosunu oluştur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sdg_selections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                goal_id INTEGER NOT NULL,
                selected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                FOREIGN KEY (goal_id) REFERENCES sdg_goals(id) ON DELETE CASCADE,
                UNIQUE(company_id, goal_id)
            )
        """)
        
        conn.commit()
        logging.info("user_sdg_selections tablosu basariyla olusturuldu")
        
    except Exception as e:
        logging.error(f"Tablo olusturulurken hata: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_sdg_selections_table()
