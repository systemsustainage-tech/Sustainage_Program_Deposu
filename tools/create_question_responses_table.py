#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Soru yanıtları tablosunu oluştur
"""

import logging
import sqlite3
import sys
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_question_responses_table(db_path: str) -> None:
    """Soru yanıtları tablosunu oluştur"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Soru yanıtları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                question_number INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                answer_text TEXT,
                answered_at TEXT,
                gri_connection TEXT,
                tsrs_connection TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """)
        
        # İndeksler
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_question_responses_company 
            ON question_responses (company_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_question_responses_sdg 
            ON question_responses (company_id, sdg_no)
        """)
        
        conn.commit()
        logging.info("Soru yanıtları tablosu başarıyla oluşturuldu")
        
    except Exception as e:
        logging.error(f"Tablo oluşturulurken hata: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = DB_PATH
    
    create_question_responses_table(db_path)
