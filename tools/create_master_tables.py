#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
SDG Master Tabloları Oluşturma
docs/SDG_16_169_232.xlsx için gerekli tabloları oluşturur
"""

import logging
import os
import sqlite3
import sys

# Add project root to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.config.database import DB_PATH
except ImportError:
    try:
        from config.database import DB_PATH
    except ImportError:
        # Fallback for standalone execution
        DB_PATH = '/var/www/sustainage/sustainage.db'
        print(f"Warning: Could not import DB_PATH, using default: {DB_PATH}")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SDGMasterTableCreator:
    """SDG Master tabloları oluşturucu"""
    
    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.db_path = os.path.join(base_dir, db_path)
        else:
            self.db_path = db_path
    
    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self) -> None:
        """Tüm tabloları oluştur"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # SDG hedefleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sdg_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code INTEGER UNIQUE NOT NULL,
                    title_tr TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # SDG alt hedefleri tablosu
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
            
            # SDG göstergeleri tablosu (genişletilmiş)
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
            
            # SDG soru tipleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sdg_question_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type_name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    input_type TEXT NOT NULL,
                    validation_rules TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # SDG soru bankası tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sdg_question_bank (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sdg_no INTEGER NOT NULL,
                    indicator_code TEXT NOT NULL,
                    question_text TEXT NOT NULL,
                    question_type_id INTEGER NOT NULL,
                    difficulty_level TEXT DEFAULT 'medium',
                    is_required BOOLEAN DEFAULT 1,
                    points INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (question_type_id) REFERENCES sdg_question_types(id)
                )
            """)
            
            # SDG soru cevapları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sdg_question_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    question_id INTEGER NOT NULL,
                    response_value TEXT,
                    response_text TEXT,
                    response_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_validated BOOLEAN DEFAULT 0,
                    validation_notes TEXT,
                    FOREIGN KEY (question_id) REFERENCES sdg_question_bank(id),
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            # SDG-GRI eşleştirme tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS map_sdg_gri (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sdg_indicator_code TEXT NOT NULL,
                    gri_standard TEXT NOT NULL,
                    gri_disclosure TEXT,
                    relation_type TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # SDG-TSRS eşleştirme tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS map_sdg_tsrs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sdg_indicator_code TEXT NOT NULL,
                    tsrs_section TEXT,
                    tsrs_metric TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # GRI-TSRS eşleştirme tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS map_gri_tsrs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    gri_standard TEXT NOT NULL,
                    gri_disclosure TEXT,
                    tsrs_section TEXT,
                    tsrs_metric TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # SDG KPI/Metrikler tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sdg_kpi_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sdg_no INTEGER NOT NULL,
                    indicator_code TEXT NOT NULL,
                    kpi_name TEXT NOT NULL,
                    metric_description TEXT,
                    measurement_frequency TEXT,
                    data_source TEXT,
                    target_value REAL,
                    current_value REAL,
                    unit TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # SDG performans metrikleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sdg_performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    sdg_no INTEGER NOT NULL,
                    indicator_code TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_unit TEXT,
                    measurement_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    target_value REAL,
                    actual_vs_target REAL,
                    improvement_rate REAL,
                    benchmark_value REAL,
                    industry_percentile REAL,
                    calculation_method TEXT,
                    data_source TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            # SDG veri doğrulama kuralları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sdg_validation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_name TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    rule_description TEXT,
                    validation_expression TEXT NOT NULL,
                    error_message TEXT,
                    severity_level TEXT DEFAULT 'warning',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # SDG veri doğrulama sonuçları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sdg_validation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    validation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    rule_id INTEGER NOT NULL,
                    sdg_no INTEGER,
                    indicator_code TEXT,
                    validation_status TEXT NOT NULL,
                    error_message TEXT,
                    suggested_fix TEXT,
                    severity_level TEXT,
                    FOREIGN KEY (rule_id) REFERENCES sdg_validation_rules(id),
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            # SDG veri kalite skorları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sdg_data_quality_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    sdg_no INTEGER,
                    indicator_code TEXT,
                    completeness_score REAL DEFAULT 0.0,
                    accuracy_score REAL DEFAULT 0.0,
                    consistency_score REAL DEFAULT 0.0,
                    timeliness_score REAL DEFAULT 0.0,
                    overall_quality_score REAL DEFAULT 0.0,
                    validation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            logging.info("Tum tablolar basariyla olusturuldu!")
            return True
            
        except Exception as e:
            logging.error(f"Tablo olusturulurken hata: {e}")
            return False

if __name__ == "__main__":
    creator = SDGMasterTableCreator()
    success = creator.create_tables()
    if success:
        logging.info("Tablolar hazır!")
    else:
        logging.info("Tablo oluşturma başarısız!")
