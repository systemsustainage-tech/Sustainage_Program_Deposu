#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remote SDG Initialization Script
Creates tables and loads data from SDG_232.xlsx
"""

import logging
import os
import sqlite3
import pandas as pd
from datetime import datetime

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Match web_app.py DB_PATH: backend/data/sdg_desktop.sqlite
DB_PATH = os.path.join(BASE_DIR, 'backend', 'data', 'sdg_desktop.sqlite')
EXCEL_PATH = os.path.join(BASE_DIR, 'SDG_232.xlsx')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def create_tables():
    logging.info("Creating tables...")
    conn = get_connection()
    cursor = conn.cursor()
    
    # SDG Goals
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sdg_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code INTEGER UNIQUE NOT NULL,
            title_tr TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # SDG Targets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sdg_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            title_tr TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (goal_id) REFERENCES sdg_goals(id)
        )
    """)
    
    # SDG Indicators
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sdg_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            title_tr TEXT NOT NULL,
            data_source TEXT,
            measurement_frequency TEXT,
            related_sectors TEXT,
            related_funds TEXT,
            kpi_metric TEXT,
            implementation_requirement TEXT,
            notes TEXT,
            request_status TEXT,
            status TEXT,
            progress_percentage REAL,
            completeness_percentage REAL,
            policy_document_exists TEXT,
            data_quality TEXT,
            incentive_readiness_score REAL,
            readiness_level TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_id) REFERENCES sdg_targets(id)
        )
    """)
    
    # SDG Question Bank
    cursor.execute("DROP TABLE IF EXISTS sdg_question_bank")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sdg_question_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_id INTEGER,
            question_text TEXT NOT NULL,
            question_type TEXT,
            options TEXT,
            required INTEGER DEFAULT 0,
            order_num INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (indicator_id) REFERENCES sdg_indicators(id)
        )
    """)
    
    # Map SDG-GRI
    cursor.execute("DROP TABLE IF EXISTS map_sdg_gri")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS map_sdg_gri (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sdg_indicator_code TEXT,
            gri_disclosure TEXT,
            relation_type TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User Selections (from SDGManager)
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
    
    # Responses (from SDGManager)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY,
            company_id INTEGER NOT NULL,
            indicator_id INTEGER NOT NULL,
            period TEXT NOT NULL,
            answer_json TEXT,
            value_num REAL,
            progress_pct INTEGER DEFAULT 0,
            request_status TEXT DEFAULT 'Gönderilmedi',
            policy_flag TEXT DEFAULT 'Hayır',
            evidence_url TEXT,
            approved_by_owner TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY(indicator_id) REFERENCES sdg_indicators(id) ON DELETE CASCADE,
            UNIQUE(company_id, indicator_id, period)
        )
    """)

    conn.commit()
    conn.close()
    logging.info("Tables created.")

def load_data():
    if not os.path.exists(EXCEL_PATH):
        logging.error(f"Excel file not found at {EXCEL_PATH}")
        return

    logging.info(f"Loading data from {EXCEL_PATH}...")
    try:
        # Read the MASTER_232 sheet
        df = pd.read_excel(EXCEL_PATH, sheet_name='MASTER_232')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        logging.info(f"Columns: {df.columns.tolist()}")

        # Rename column for easier access
        # Check if the column exists before renaming
        if 'Sürdürülebilir Kalkınma Hedefi No:' in df.columns:
            df.rename(columns={'Sürdürülebilir Kalkınma Hedefi No:': 'SDG No'}, inplace=True)
        elif 'Sürdürülebilir Kalkınma Hedefi No' in df.columns:
             df.rename(columns={'Sürdürülebilir Kalkınma Hedefi No': 'SDG No'}, inplace=True)
        
        if 'SDG No' not in df.columns:
            logging.error(f"Required column 'SDG No' (or variant) not found. Available: {df.columns.tolist()}")
            return
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Goals
        goals = df[['SDG No', 'SDG Başlık']].drop_duplicates()
        for _, row in goals.iterrows():
            try:
                cursor.execute("INSERT OR REPLACE INTO sdg_goals (code, title_tr) VALUES (?, ?)", 
                               (int(row['SDG No']), row['SDG Başlık']))
            except Exception as e:
                logging.error(f"Error inserting goal {row}: {e}")

        # 2. Targets
        targets = df[['SDG No', 'Alt Hedef Kodu', 'Alt Hedef Tanımı (TR)']].drop_duplicates()
        for _, row in targets.iterrows():
            try:
                # Find goal id
                cur = cursor.execute("SELECT id FROM sdg_goals WHERE code = ?", (int(row['SDG No']),))
                res = cur.fetchone()
                if res:
                    goal_id = res[0]
                    cursor.execute("INSERT OR IGNORE INTO sdg_targets (goal_id, code, title_tr) VALUES (?, ?, ?)",
                                   (goal_id, row['Alt Hedef Kodu'], row['Alt Hedef Tanımı (TR)']))
            except Exception as e:
                logging.error(f"Error inserting target {row}: {e}")

        # 3. Indicators & Questions
        # Columns in Excel: 
        # 'Veri Kaynağı', 'Ölçüm Sıklığı', 'İlgili Sektörler (Öneri)', 'İlgili Teşvik / Fon (Örnek)', 
        # 'KPI / Metrik', 'Uygulama Zorunluluğu', 'Notlar / Kalanlıklar', 'Talep Durumu', 'Durum', 
        # 'İlerleme (%)', 'Doluluk (%)', 'Politika/Belge Var mı?', 'Veri Kalitesi', 
        # 'Teşvik Hazırlık Skoru', 'Hazırlık Seviyesi', 'Soru 1', 'Soru 2', 'Soru 3'
        
        # We iterate over the full dataframe to get all details for indicators
        for _, row in df.iterrows():
            try:
                # Find target id
                cur = cursor.execute("SELECT id FROM sdg_targets WHERE code = ?", (row['Alt Hedef Kodu'],))
                res = cur.fetchone()
                if res:
                    target_id = res[0]
                    
                    # Insert Indicator
                    cursor.execute("""
                        INSERT OR IGNORE INTO sdg_indicators (
                            target_id, code, title_tr, 
                            data_source, measurement_frequency, related_sectors, related_funds, 
                            kpi_metric, implementation_requirement, notes, request_status, 
                            status, progress_percentage, completeness_percentage, policy_document_exists, 
                            data_quality, incentive_readiness_score, readiness_level
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        target_id, row['Gösterge Kodu'], row['Gösterge Tanımı (TR)'],
                        row.get('Veri Kaynağı'), row.get('Ölçüm Sıklığı'), row.get('İlgili Sektörler (Öneri)'), row.get('İlgili Teşvik / Fon (Örnek)'),
                        row.get('KPI / Metrik'), row.get('Uygulama Zorunluluğu'), row.get('Notlar / Kalanlıklar'), row.get('Talep Durumu'),
                        row.get('Durum'), row.get('İlerleme (%)'), row.get('Doluluk (%)'), row.get('Politika/Belge Var mı?'),
                        row.get('Veri Kalitesi'), row.get('Teşvik Hazırlık Skoru'), row.get('Hazırlık Seviyesi')
                    ))
                    
                    # Get the inserted/existing indicator ID
                    cur = cursor.execute("SELECT id FROM sdg_indicators WHERE code = ?", (row['Gösterge Kodu'],))
                    ind_res = cur.fetchone()
                    if ind_res:
                        indicator_id = ind_res[0]
                        
                        # Insert Questions (Soru 1, Soru 2, Soru 3)
                        for q_col, order in [('Soru 1', 1), ('Soru 2', 2), ('Soru 3', 3)]:
                            if pd.notna(row.get(q_col)):
                                cursor.execute("""
                                    INSERT OR IGNORE INTO sdg_question_bank (
                                        indicator_id, question_text, question_type, order_num
                                    ) VALUES (?, ?, ?, ?)
                                """, (indicator_id, row[q_col], 'text', order))
                                
                        # Insert GRI Mapping if exists
                        if pd.notna(row.get('GRI Bağlantısı')):
                             cursor.execute("""
                                INSERT OR IGNORE INTO map_sdg_gri (
                                    sdg_indicator_code, gri_disclosure, relation_type
                                ) VALUES (?, ?, ?)
                            """, (row['Gösterge Kodu'], row['GRI Bağlantısı'], 'direct'))

            except Exception as e:
                logging.error(f"Error inserting indicator/questions for row {row.get('Gösterge Kodu')}: {e}")

        conn.commit()
        conn.close()
        logging.info("Data loaded successfully.")

    except Exception as e:
        logging.error(f"Error loading data: {e}")

if __name__ == "__main__":
    create_tables()
    load_data()
