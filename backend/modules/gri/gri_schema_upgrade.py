#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Şema Genişletme - Sprint 1
Mevcut şemayı koruyarak ek tablolar ekler
"""

import logging
import os
import sqlite3
from config.database import DB_PATH


class GRISchemaUpgrade:
    """GRI şema genişletme sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        # db_path göreli ise proje köküne göre mutlak hale getir
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_extension_tables(self) -> None:
        """Ek tabloları oluştur - mevcut şemayı bozmadan"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 0. Temel Tablolar (Eksikse Oluştur)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_standards (
                    id INTEGER PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_indicators (
                    id INTEGER PRIMARY KEY,
                    standard_id INTEGER,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    unit TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (standard_id) REFERENCES gri_standards(id)
                )
            """)

            # 1. GRI Kategorileri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    group_name TEXT NOT NULL,
                    description TEXT,
                    sort_order INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. GRI KPIs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_kpis (
                    id INTEGER PRIMARY KEY,
                    indicator_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    formula TEXT,
                    unit TEXT,
                    frequency TEXT,
                    owner TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                )
            """)

            # 3. GRI Hedefler (2024-2025)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_targets (
                    id INTEGER PRIMARY KEY,
                    indicator_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    target_value TEXT,
                    unit TEXT,
                    method TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                )
            """)

            # 4. GRI Benchmarks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_benchmarks (
                    id INTEGER PRIMARY KEY,
                    indicator_id INTEGER NOT NULL,
                    scope TEXT,
                    value TEXT,
                    unit TEXT,
                    source TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                )
            """)

            # 5. Dijital Araçlar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_digital_tools (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT,
                    description TEXT,
                    category TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 6. Raporlama Formatları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_reporting_formats (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    extension TEXT NOT NULL,
                    description TEXT,
                    template_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 7. Doğrulama Kuralları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_validation_rules (
                    id INTEGER PRIMARY KEY,
                    indicator_id INTEGER,
                    rule_type TEXT NOT NULL,
                    rule_expression TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                )
            """)

            # 8. Birim Sözlüğü
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_units (
                    id INTEGER PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    name_tr TEXT NOT NULL,
                    name_en TEXT,
                    category TEXT,
                    description TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 9. Veri Kaynakları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_sources (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    system TEXT,
                    description TEXT,
                    category TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 10. Risk Değerlendirmesi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gri_risks (
                    id INTEGER PRIMARY KEY,
                    indicator_id INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    impact TEXT,
                    likelihood TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (indicator_id) REFERENCES gri_indicators(id)
                )
            """)

            # 11. GRI Standartları - Type alanı ekleme (mevcut tabloya)
            try:
                cursor.execute("ALTER TABLE gri_standards ADD COLUMN type TEXT")
                logging.info("gri_standards tablosuna 'type' alanı eklendi")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logging.info("gri_standards tablosunda 'type' alanı zaten mevcut")
                else:
                    raise e

            # 12. GRI Standartları - Alt kategori alanı ekleme
            try:
                cursor.execute("ALTER TABLE gri_standards ADD COLUMN sub_category TEXT")
                logging.info("gri_standards tablosuna 'sub_category' alanı eklendi")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    logging.info("gri_standards tablosunda 'sub_category' alanı zaten mevcut")
                else:
                    raise e

            # 13. GRI Göstergeleri - Ek alanlar
            additional_indicator_fields = [
                ('priority', 'TEXT'),
                ('requirement_level', 'TEXT'),
                ('reporting_frequency', 'TEXT'),
                ('data_quality', 'TEXT'),
                ('audit_required', 'TEXT'),
                ('validation_required', 'TEXT'),
                ('digitalization_status', 'TEXT'),
                ('cost_level', 'TEXT'),
                ('time_requirement', 'TEXT'),
                ('expertise_requirement', 'TEXT'),
                ('sustainability_impact', 'TEXT'),
                ('legal_compliance', 'TEXT'),
                ('sector_specific', 'TEXT'),
                ('international_standard', 'TEXT'),
                ('metric_type', 'TEXT'),
                ('scale_unit', 'TEXT'),
                ('data_source_system', 'TEXT'),
                ('reporting_format', 'TEXT'),
                ('tsrs_esrs_mapping', 'TEXT'),
                ('un_sdg_mapping', 'TEXT'),
                ('gri_3_3_reference', 'TEXT'),
                ('impact_area', 'TEXT'),
                ('stakeholder_group', 'TEXT')
            ]

            for field_name, field_type in additional_indicator_fields:
                try:
                    cursor.execute(f"ALTER TABLE gri_indicators ADD COLUMN {field_name} TEXT")
                    logging.info(f"gri_indicators tablosuna '{field_name}' alanı eklendi")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        logging.info(f"gri_indicators tablosunda '{field_name}' alanı zaten mevcut")
                    else:
                        raise e
            
            conn.commit()
            print("GRI Schema Upgrade successful")
        except Exception as e:
            print(f"Schema upgrade error: {e}")
            conn.rollback()
            raise e
        finally:
            conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    upgrader = GRISchemaUpgrade()
    upgrader.create_extension_tables()
