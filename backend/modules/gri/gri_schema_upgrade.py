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
            logging.info("\nTüm ek tablolar başarıyla oluşturuldu!")
            return True

        except Exception as e:
            logging.error(f"Şema genişletme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def populate_initial_data(self) -> None:
        """Başlangıç verilerini ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Kategoriler
            categories = [
                ('Universal', 'Universal', 'GRI Universal Standards', 1),
                ('Economic', 'Economic', 'GRI Economic Standards', 2),
                ('Environmental', 'Environmental', 'GRI Environmental Standards', 3),
                ('Social', 'Social', 'GRI Social Standards', 4),
                ('Sector-Specific', 'Sector', 'GRI Sector-Specific Standards', 5)
            ]

            for name, group, desc, sort_order in categories:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_categories (name, group_name, description, sort_order)
                    VALUES (?, ?, ?, ?)
                """, (name, group, desc, sort_order))

            # Dijital Araçlar
            digital_tools = [
                ('GRI Software', 'Software', 'GRI raporlama yazılımı', 'Raporlama'),
                ('ERP Sistemi', 'System', 'Kurumsal kaynak planlama sistemi', 'Operasyonel'),
                ('HRIS Sistemi', 'System', 'İnsan kaynakları bilgi sistemi', 'Sosyal'),
                ('Enerji Yönetim Sistemi', 'System', 'Enerji tüketim takip sistemi', 'Çevresel'),
                ('Karbon Hesaplama Yazılımı', 'Software', 'Karbon ayak izi hesaplama', 'Çevresel'),
                ('İSG Yazılımı', 'Software', 'İş sağlığı ve güvenliği yönetimi', 'Sosyal'),
                ('Sürdürülebilirlik Yazılımı', 'Software', 'Sürdürülebilirlik raporlama', 'Universal')
            ]

            for name, type_tool, desc, category in digital_tools:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_digital_tools (name, type, description, category)
                    VALUES (?, ?, ?, ?)
                """, (name, type_tool, desc, category))

            # Raporlama Formatları
            reporting_formats = [
                ('GRI Content Index', 'xlsx', 'GRI İçerik İndeksi', None),
                ('GRI Core Report', 'docx', 'GRI Core Raporu', None),
                ('GRI Comprehensive Report', 'docx', 'GRI Comprehensive Raporu', None),
                ('KPI Dashboard', 'xlsx', 'KPI Dashboard Raporu', None),
                ('Risk Assessment', 'pdf', 'Risk Değerlendirme Raporu', None),
                ('Target Progress', 'xlsx', 'Hedef İlerleme Raporu', None)
            ]

            for name, ext, desc, template in reporting_formats:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_reporting_formats (name, extension, description, template_path)
                    VALUES (?, ?, ?, ?)
                """, (name, ext, desc, template))

            # Birim Sözlüğü
            units = [
                ('Text', 'Metin', 'Text', 'Qualitative', 'Kalitatif veri'),
                ('Number', 'Sayı', 'Number', 'Quantitative', 'Sayısal veri'),
                ('Currency', 'Para Birimi', 'Currency', 'Financial', 'Finansal veri'),
                ('Percentage', 'Yüzde', 'Percentage', 'Ratio', 'Oran verisi'),
                ('Ratio', 'Oran', 'Ratio', 'Ratio', 'Oran verisi'),
                ('MWh', 'Megawatt Saat', 'Megawatt Hour', 'Energy', 'Enerji birimi'),
                ('tCO2e', 'Ton CO2 Eşdeğeri', 'Ton CO2 Equivalent', 'Emission', 'Emisyon birimi'),
                ('Ton', 'Ton', 'Ton', 'Weight', 'Ağırlık birimi'),
                ('m³', 'Metreküp', 'Cubic Meter', 'Volume', 'Hacim birimi'),
                ('kg', 'Kilogram', 'Kilogram', 'Weight', 'Ağırlık birimi')
            ]

            for code, name_tr, name_en, category, desc in units:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_units (code, name_tr, name_en, category, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (code, name_tr, name_en, category, desc))

            # Veri Kaynakları
            sources = [
                ('Raporlama Departmanı', 'Manual', 'Manuel raporlama', 'Universal'),
                ('İnsan Kaynakları', 'HRIS', 'İK bilgi sistemi', 'Social'),
                ('Finans', 'ERP', 'Finansal sistem', 'Economic'),
                ('Operasyonlar', 'MES', 'Üretim yönetim sistemi', 'Environmental'),
                ('İş Güvenliği', 'EHS', 'Çevre sağlık güvenlik', 'Social'),
                ('Sürdürülebilirlik', 'Sustainability', 'Sürdürülebilirlik yazılımı', 'Universal')
            ]

            for name, system, desc, category in sources:
                cursor.execute("""
                    INSERT OR IGNORE INTO gri_sources (name, system, description, category)
                    VALUES (?, ?, ?, ?)
                """, (name, system, desc, category))

            conn.commit()
            logging.info("Başlangıç verileri başarıyla eklendi!")
            return True

        except Exception as e:
            logging.error(f"Başlangıç veri ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def verify_schema(self) -> None:
        """Şema doğrulaması"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Ek tabloları kontrol et
            expected_tables = [
                'gri_categories', 'gri_kpis', 'gri_targets', 'gri_benchmarks',
                'gri_digital_tools', 'gri_reporting_formats', 'gri_validation_rules',
                'gri_units', 'gri_sources', 'gri_risks'
            ]

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'gri_%'")
            existing_tables = [row[0] for row in cursor.fetchall()]

            logging.info("\n=== ŞEMA DOĞRULAMA ===")
            logging.info(f"Mevcut GRI tabloları: {len(existing_tables)}")

            for table in expected_tables:
                if table in existing_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    logging.info(f"OK {table}: {count} kayıt")
                else:
                    logging.info(f"EKSIK {table}: EKSIK")

            # Ana tabloları kontrol et
            main_tables = ['gri_standards', 'gri_indicators', 'gri_responses', 'gri_selections']
            for table in main_tables:
                if table in existing_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    logging.info(f"OK {table}: {count} kayıt")
                else:
                    logging.info(f"EKSIK {table}: EKSIK")

            return True

        except Exception as e:
            logging.error(f"Şema doğrulama hatası: {e}")
            return False
        finally:
            conn.close()

def upgrade_gri_schema() -> None:
    """GRI şemasını genişlet"""
    logging.info("GRI Şema Genişletme Başlıyor...")

    upgrade = GRISchemaUpgrade()

    # 1. Ek tabloları oluştur
    logging.info("\n1. Ek tabloları oluşturuluyor...")
    if not upgrade.create_extension_tables():
        return False

    # 2. Başlangıç verilerini ekle
    logging.info("\n2. Başlangıç verileri ekleniyor...")
    if not upgrade.populate_initial_data():
        return False

    # 3. Şema doğrulaması
    logging.info("\n3. Şema doğrulaması...")
    if not upgrade.verify_schema():
        return False

    logging.info("\nGRI şema genişletme başarıyla tamamlandı!")
    return True

if __name__ == "__main__":
    upgrade_gri_schema()
