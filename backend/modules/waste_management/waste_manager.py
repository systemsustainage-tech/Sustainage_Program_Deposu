#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATIK YÖNETİMİ YÖNETİCİSİ
Atık verilerini yönetir, hedefleri takip eder ve raporlar oluşturur
"""

import logging
import os
import sqlite3
from typing import Dict, List
from config.database import DB_PATH


class WasteManager:
    """Atık Yönetimi Modülü Yöneticisi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        # db_path göreli ise proje köküne göre mutlak hale getir
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.company_id = 1  # Varsayılan company_id

        # Tabloları oluştur
        self.create_waste_tables()

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_waste_tables(self) -> None:
        """Atık yönetimi tablolarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Atık türleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_types (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    waste_code TEXT UNIQUE NOT NULL,
                    waste_name TEXT NOT NULL,
                    waste_category TEXT NOT NULL,
                    hazard_level TEXT DEFAULT 'Non-hazardous',
                    recycling_potential TEXT DEFAULT 'Medium',
                    disposal_method TEXT,
                    environmental_impact TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Atık kayıtları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    waste_type_id INTEGER NOT NULL,
                    waste_code TEXT NOT NULL,
                    waste_name TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    source_location TEXT,
                    generation_source TEXT,
                    disposal_method TEXT,
                    recycling_rate REAL DEFAULT 0.0,
                    disposal_cost REAL DEFAULT 0.0,
                    carbon_footprint REAL DEFAULT 0.0,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    data_quality TEXT DEFAULT 'Estimated',
                    evidence_file TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (waste_type_id) REFERENCES waste_types(id),
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Migration: eksik sütunları ekle
            cursor.execute("PRAGMA table_info(waste_records)")
            cols = [c[1] for c in cursor.fetchall()]
            if 'invoice_date' not in cols:
                cursor.execute("ALTER TABLE waste_records ADD COLUMN invoice_date TEXT")
            if 'due_date' not in cols:
                cursor.execute("ALTER TABLE waste_records ADD COLUMN due_date TEXT")
            if 'supplier' not in cols:
                cursor.execute("ALTER TABLE waste_records ADD COLUMN supplier TEXT")

            # Atık azaltma hedefleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_reduction_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_name TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    waste_category TEXT,
                    waste_type_id INTEGER,
                    base_year INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    base_quantity REAL NOT NULL,
                    target_quantity REAL NOT NULL,
                    reduction_percentage REAL,
                    target_unit TEXT NOT NULL,
                    status TEXT DEFAULT 'Active',
                    progress REAL DEFAULT 0.0,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (waste_type_id) REFERENCES waste_types(id),
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Geri dönüşüm projeleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recycling_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,
                    waste_types TEXT,
                    start_date DATE,
                    end_date DATE,
                    status TEXT DEFAULT 'Planning',
                    investment_amount REAL DEFAULT 0.0,
                    expected_savings REAL DEFAULT 0.0,
                    recycling_rate_before REAL DEFAULT 0.0,
                    recycling_rate_target REAL DEFAULT 0.0,
                    current_recycling_rate REAL DEFAULT 0.0,
                    environmental_impact TEXT,
                    economic_benefits TEXT,
                    challenges TEXT,
                    lessons_learned TEXT,
                    next_steps TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Atık yönetimi metrikleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    total_waste_generated REAL DEFAULT 0.0,
                    total_waste_disposed REAL DEFAULT 0.0,
                    total_waste_recycled REAL DEFAULT 0.0,
                    recycling_rate REAL DEFAULT 0.0,
                    waste_reduction_rate REAL DEFAULT 0.0,
                    circular_economy_index REAL DEFAULT 0.0,
                    waste_cost REAL DEFAULT 0.0,
                    waste_revenue REAL DEFAULT 0.0,
                    carbon_footprint REAL DEFAULT 0.0,
                    hazardous_waste_ratio REAL DEFAULT 0.0,
                    organic_waste_ratio REAL DEFAULT 0.0,
                    recyclable_waste_ratio REAL DEFAULT 0.0,
                    data_quality_score REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Atık yönetimi raporları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS waste_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    report_name TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    period TEXT NOT NULL,
                    report_data TEXT,
                    file_path TEXT,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # İndeksler
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_waste_records_company_period ON waste_records(company_id, period)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_waste_targets_company ON waste_reduction_targets(company_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_recycling_projects_company ON recycling_projects(company_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_waste_metrics_company_period ON waste_metrics(company_id, period)")

            conn.commit()
            logging.info("[OK] Atik yonetimi tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Atik yonetimi tablolari olusturulamadi: {e}")
            conn.rollback()
        finally:
            conn.close()

    def populate_waste_types(self) -> None:
        """Atık türlerini doldur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            waste_types_data = [
                # Organik Atıklar
                ("ORGANIC-001", "Organik Mutfak Atığı", "Organik", "Non-hazardous", "High", "Kompost", "Low", "Mutfak ve yemek atıkları"),
                ("ORGANIC-002", "Bahçe Atığı", "Organik", "Non-hazardous", "High", "Kompost", "Low", "Bahçe ve park atıkları"),
                ("ORGANIC-003", "Tarımsal Atık", "Organik", "Non-hazardous", "High", "Kompost/Biyogaz", "Low", "Tarım faaliyetlerinden kaynaklanan atıklar"),

                # Geri Dönüşüm Atıkları
                ("RECYCLE-001", "Kağıt ve Karton", "Geri Dönüşüm", "Non-hazardous", "High", "Geri Dönüşüm", "Low", "Ofis kağıtları, kartonlar"),
                ("RECYCLE-002", "Plastik", "Geri Dönüşüm", "Non-hazardous", "Medium", "Geri Dönüşüm", "Medium", "Plastik ambalaj ve ürünler"),
                ("RECYCLE-003", "Metal", "Geri Dönüşüm", "Non-hazardous", "High", "Geri Dönüşüm", "Low", "Demir, alüminyum, bakır vb."),
                ("RECYCLE-004", "Cam", "Geri Dönüşüm", "Non-hazardous", "High", "Geri Dönüşüm", "Low", "Cam şişe ve kavanozlar"),
                ("RECYCLE-005", "Elektronik Atık", "Geri Dönüşüm", "Hazardous", "Medium", "Özel İşlem", "High", "Bilgisayar, telefon, elektronik cihazlar"),

                # Tehlikeli Atıklar
                ("HAZARD-001", "Kimyasal Atık", "Tehlikeli", "Hazardous", "Low", "Özel İşlem", "High", "Endüstriyel kimyasallar"),
                ("HAZARD-002", "Yağ Atığı", "Tehlikeli", "Hazardous", "Medium", "Özel İşlem", "High", "Motor yağı, endüstriyel yağlar"),
                ("HAZARD-003", "Boyar Madde Atığı", "Tehlikeli", "Hazardous", "Low", "Özel İşlem", "High", "Boya ve vernik atıkları"),
                ("HAZARD-004", "Pil ve Batarya", "Tehlikeli", "Hazardous", "Medium", "Özel İşlem", "High", "Kullanılmış piller"),

                # İnşaat ve Yıkım Atıkları
                ("CONSTRUCTION-001", "Beton Atığı", "İnşaat", "Non-hazardous", "High", "Geri Dönüşüm", "Low", "Beton ve betonarme atıkları"),
                ("CONSTRUCTION-002", "Ahşap Atık", "İnşaat", "Non-hazardous", "Medium", "Geri Dönüşüm", "Low", "İnşaat ahşap atıkları"),
                ("CONSTRUCTION-003", "Metal İnşaat Atığı", "İnşaat", "Non-hazardous", "High", "Geri Dönüşüm", "Low", "İnşaat metal atıkları"),

                # Tekstil Atıkları
                ("TEXTILE-001", "Tekstil Atığı", "Tekstil", "Non-hazardous", "Medium", "Geri Dönüşüm", "Medium", "Kullanılmış tekstil ürünleri"),
                ("TEXTILE-002", "Deri Atığı", "Tekstil", "Non-hazardous", "Low", "Özel İşlem", "Medium", "Deri üretim atıkları"),

                # Tıbbi Atıklar
                ("MEDICAL-001", "Tıbbi Atık", "Tıbbi", "Hazardous", "Low", "Özel İşlem", "High", "Hastane ve sağlık atıkları"),
                ("MEDICAL-002", "İlaç Atığı", "Tıbbi", "Hazardous", "Low", "Özel İşlem", "High", "Son kullanma tarihi geçmiş ilaçlar"),

                # Genel Atıklar
                ("GENERAL-001", "Karışık Atık", "Genel", "Non-hazardous", "Low", "Depolama", "Medium", "Ayrıştırılmamış atıklar"),
                ("GENERAL-002", "Ambalaj Atığı", "Genel", "Non-hazardous", "High", "Geri Dönüşüm", "Low", "Çeşitli ambalaj atıkları")
            ]

            for waste_code, waste_name, waste_category, hazard_level, recycling_potential, disposal_method, environmental_impact, description in waste_types_data:
                cursor.execute("""
                    INSERT OR IGNORE INTO waste_types 
                    (waste_code, waste_name, waste_category, hazard_level, recycling_potential, 
                     disposal_method, environmental_impact, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (waste_code, waste_name, waste_category, hazard_level, recycling_potential,
                      disposal_method, environmental_impact, description))

            conn.commit()
            logging.info("[OK] Atik turleri dolduruldu")

        except Exception as e:
            logging.error(f"[HATA] Atik turleri doldurulurken hata: {e}")
            conn.rollback()
        finally:
            conn.close()

    def add_waste_record(self, company_id: int, form_data: dict) -> bool:
        """Yeni atık kaydı ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Form verilerini al
            waste_code = form_data.get('waste_code', '')
            waste_name = form_data.get('waste_name', '')
            waste_category = form_data.get('waste_category', '')
            quantity = form_data.get('quantity', 0.0)
            unit = form_data.get('unit', 'kg')
            hazard_level = form_data.get('hazard_level', 'Non-hazardous')
            recycling_rate = form_data.get('recycling_rate', 0.0)
            disposal_method = form_data.get('disposal_method', '')
            disposal_cost = form_data.get('disposal_cost', 0.0)
            carbon_footprint = form_data.get('carbon_footprint', 0.0)
            record_date = form_data.get('record_date', '')
            form_data.get('responsible_person', '')
            invoice_date = form_data.get('invoice_date') or None
            due_date = form_data.get('due_date') or None
            supplier = form_data.get('supplier') or None
            notes = form_data.get('notes', '')

            # Dönem bilgisini tarihten çıkar
            period = record_date[:4] if record_date else '2024'

            # Atık türü ID'sini bul veya oluştur
            cursor.execute("SELECT id FROM waste_types WHERE waste_code = ?", (waste_code,))
            result = cursor.fetchone()

            if not result:
                # Yeni atık türü oluştur
                cursor.execute("""
                    INSERT INTO waste_types 
                    (waste_code, waste_name, waste_category, hazard_level, recycling_potential, disposal_method)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (waste_code, waste_name, waste_category, hazard_level, 'Medium', disposal_method))
                waste_type_id = cursor.lastrowid
            else:
                waste_type_id = result[0]

            # Atık kaydını ekle
            cursor.execute("""
                INSERT INTO waste_records 
                (company_id, period, waste_type_id, waste_code, waste_name, quantity, unit,
                 disposal_method, recycling_rate, disposal_cost, carbon_footprint,
                 invoice_date, due_date, supplier,
                 data_quality, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, period, waste_type_id, waste_code, waste_name, quantity, unit,
                  disposal_method, recycling_rate, disposal_cost, carbon_footprint,
                  invoice_date, due_date, supplier,
                  'Estimated', notes, record_date))

            conn.commit()
            logging.info(f"[OK] Atik kaydi eklendi: {waste_name} - {quantity} {unit}")
            return True

        except Exception as e:
            logging.error(f"[HATA] Atik kaydi eklenirken hata: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_waste_records(self, company_id: int, period: str = None) -> List[Dict]:
        """Atık kayıtlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if period:
                cursor.execute("""
                    SELECT wr.*, wt.waste_category, wt.hazard_level, wt.recycling_potential
                    FROM waste_records wr
                    JOIN waste_types wt ON wr.waste_type_id = wt.id
                    WHERE wr.company_id = ? AND wr.period = ?
                    ORDER BY wr.created_at DESC
                """, (company_id, period))
            else:
                cursor.execute("""
                    SELECT wr.*, wt.waste_category, wt.hazard_level, wt.recycling_potential
                    FROM waste_records wr
                    JOIN waste_types wt ON wr.waste_type_id = wt.id
                    WHERE wr.company_id = ?
                    ORDER BY wr.created_at DESC
                """, (company_id,))

            columns = [description[0] for description in cursor.description]
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            return results

        except Exception as e:
            logging.error(f"[HATA] Atik kayitlari getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def add_waste_target(self, company_id: int, target_name: str, target_type: str,
                        waste_category: str = None, waste_type_id: int = None,
                        base_year: int = 2023, target_year: int = 2025,
                        base_quantity: float = 0.0, target_quantity: float = 0.0,
                        reduction_percentage: float = None, target_unit: str = "kg",
                        description: str = None) -> bool:
        """Atık azaltma hedefi ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Azaltma yüzdesini hesapla
            if reduction_percentage is None and base_quantity > 0:
                reduction_percentage = ((base_quantity - target_quantity) / base_quantity) * 100

            cursor.execute("""
                INSERT INTO waste_reduction_targets 
                (company_id, target_name, target_type, waste_category, waste_type_id,
                 base_year, target_year, base_quantity, target_quantity, reduction_percentage,
                 target_unit, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, target_name, target_type, waste_category, waste_type_id,
                  base_year, target_year, base_quantity, target_quantity, reduction_percentage,
                  target_unit, description))

            conn.commit()
            logging.info(f"[OK] Atik azaltma hedefi eklendi: {target_name}")
            return True

        except Exception as e:
            logging.error(f"[HATA] Atik azaltma hedefi eklenirken hata: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_waste_targets(self, company_id: int) -> List[Dict]:
        """Atık azaltma hedeflerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM waste_reduction_targets 
                WHERE company_id = ?
                ORDER BY target_year DESC, created_at DESC
            """, (company_id,))

            columns = [description[0] for description in cursor.description]
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            return results

        except Exception as e:
            logging.error(f"[HATA] Atik azaltma hedefleri getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def add_recycling_project(self, company_id: int, project_name: str, project_type: str,
                            waste_types: str = None, start_date: str = None, end_date: str = None,
                            investment_amount: float = 0.0, expected_savings: float = 0.0,
                            recycling_rate_before: float = 0.0, recycling_rate_target: float = 0.0,
                            environmental_impact: str = None, economic_benefits: str = None,
                            challenges: str = None, lessons_learned: str = None,
                            next_steps: str = None) -> bool:
        """Geri dönüşüm projesi ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO recycling_projects 
                (company_id, project_name, project_type, waste_types, start_date, end_date,
                 investment_amount, expected_savings, recycling_rate_before, recycling_rate_target,
                 environmental_impact, economic_benefits, challenges, lessons_learned, next_steps)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, project_name, project_type, waste_types, start_date, end_date,
                  investment_amount, expected_savings, recycling_rate_before, recycling_rate_target,
                  environmental_impact, economic_benefits, challenges, lessons_learned, next_steps))

            conn.commit()
            logging.info(f"[OK] Geri donusum projesi eklendi: {project_name}")
            return True

        except Exception as e:
            logging.error(f"[HATA] Geri donusum projesi eklenirken hata: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_recycling_projects(self, company_id: int) -> List[Dict]:
        """Geri dönüşüm projelerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM recycling_projects 
                WHERE company_id = ?
                ORDER BY created_at DESC
            """, (company_id,))

            columns = [description[0] for description in cursor.description]
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            return results

        except Exception as e:
            logging.error(f"[HATA] Geri donusum projeleri getirilirken hata: {e}")
            return []
        finally:
            conn.close()

    def calculate_waste_metrics(self, company_id: int, period: str) -> Dict:
        """Atık yönetimi metriklerini hesapla"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Toplam atık üretimi
            cursor.execute("""
                SELECT SUM(quantity) as total_generated
                FROM waste_records 
                WHERE company_id = ? AND period = ?
            """, (company_id, period))
            total_generated = cursor.fetchone()[0] or 0.0

            # Toplam atık bertarafı
            cursor.execute("""
                SELECT SUM(quantity) as total_disposed
                FROM waste_records 
                WHERE company_id = ? AND period = ? AND disposal_method != 'Geri Dönüşüm'
            """, (company_id, period))
            total_disposed = cursor.fetchone()[0] or 0.0

            # Toplam geri dönüşüm
            cursor.execute("""
                SELECT SUM(quantity * recycling_rate / 100) as total_recycled
                FROM waste_records 
                WHERE company_id = ? AND period = ?
            """, (company_id, period))
            total_recycled = cursor.fetchone()[0] or 0.0

            # Geri dönüşüm oranı
            recycling_rate = (total_recycled / total_generated * 100) if total_generated > 0 else 0.0

            # Atık azaltma oranı (önceki yıla göre)
            cursor.execute("""
                SELECT SUM(quantity) as prev_total
                FROM waste_records 
                WHERE company_id = ? AND period = ?
            """, (company_id, str(int(period) - 1)))
            prev_total = cursor.fetchone()[0] or 0.0

            waste_reduction_rate = ((prev_total - total_generated) / prev_total * 100) if prev_total > 0 else 0.0

            # Döngüsel ekonomi indeksi (basit hesaplama)
            circular_economy_index = (recycling_rate + (100 - waste_reduction_rate)) / 2

            # Toplam atık maliyeti
            cursor.execute("""
                SELECT SUM(disposal_cost) as total_cost
                FROM waste_records 
                WHERE company_id = ? AND period = ?
            """, (company_id, period))
            total_cost = cursor.fetchone()[0] or 0.0

            # Toplam karbon ayak izi
            cursor.execute("""
                SELECT SUM(carbon_footprint) as total_carbon
                FROM waste_records 
                WHERE company_id = ? AND period = ?
            """, (company_id, period))
            total_carbon = cursor.fetchone()[0] or 0.0

            # Atık kategorisi dağılımları
            cursor.execute("""
                SELECT wt.waste_category, SUM(wr.quantity) as category_total
                FROM waste_records wr
                JOIN waste_types wt ON wr.waste_type_id = wt.id
                WHERE wr.company_id = ? AND wr.period = ?
                GROUP BY wt.waste_category
            """, (company_id, period))

            category_totals = dict(cursor.fetchall())
            total_waste = sum(category_totals.values()) if category_totals else 1.0

            hazardous_ratio = (category_totals.get('Tehlikeli', 0) / total_waste * 100) if total_waste > 0 else 0.0
            organic_ratio = (category_totals.get('Organik', 0) / total_waste * 100) if total_waste > 0 else 0.0
            recyclable_ratio = (category_totals.get('Geri Dönüşüm', 0) / total_waste * 100) if total_waste > 0 else 0.0

            # Veri kalitesi skoru (basit hesaplama)
            cursor.execute("""
                SELECT AVG(CASE 
                    WHEN data_quality = 'Measured' THEN 100
                    WHEN data_quality = 'Estimated' THEN 75
                    WHEN data_quality = 'Calculated' THEN 50
                    ELSE 25
                END) as quality_score
                FROM waste_records 
                WHERE company_id = ? AND period = ?
            """, (company_id, period))
            data_quality_score = cursor.fetchone()[0] or 0.0

            metrics = {
                'total_waste_generated': round(total_generated, 2),
                'total_waste_disposed': round(total_disposed, 2),
                'total_waste_recycled': round(total_recycled, 2),
                'recycling_rate': round(recycling_rate, 2),
                'waste_reduction_rate': round(waste_reduction_rate, 2),
                'circular_economy_index': round(circular_economy_index, 2),
                'waste_cost': round(total_cost, 2),
                'waste_revenue': 0.0,  # Geri dönüşüm geliri hesaplanabilir
                'carbon_footprint': round(total_carbon, 2),
                'hazardous_waste_ratio': round(hazardous_ratio, 2),
                'organic_waste_ratio': round(organic_ratio, 2),
                'recyclable_waste_ratio': round(recyclable_ratio, 2),
                'data_quality_score': round(data_quality_score, 2)
            }

            return metrics

        except Exception as e:
            logging.error(f"[HATA] Atik metrikleri hesaplanirken hata: {e}")
            return {}
        finally:
            conn.close()

    def save_waste_metrics(self, company_id: int, period: str, metrics: Dict) -> int:
        """Atık metriklerini kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO waste_metrics 
                (company_id, period, total_waste_generated, total_waste_disposed, total_waste_recycled,
                 recycling_rate, waste_reduction_rate, circular_economy_index, waste_cost, waste_revenue,
                 carbon_footprint, hazardous_waste_ratio, organic_waste_ratio, recyclable_waste_ratio,
                 data_quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, period, metrics.get('total_waste_generated', 0.0),
                  metrics.get('total_waste_disposed', 0.0), metrics.get('total_waste_recycled', 0.0),
                  metrics.get('recycling_rate', 0.0), metrics.get('waste_reduction_rate', 0.0),
                  metrics.get('circular_economy_index', 0.0), metrics.get('waste_cost', 0.0),
                  metrics.get('waste_revenue', 0.0), metrics.get('carbon_footprint', 0.0),
                  metrics.get('hazardous_waste_ratio', 0.0), metrics.get('organic_waste_ratio', 0.0),
                  metrics.get('recyclable_waste_ratio', 0.0), metrics.get('data_quality_score', 0.0)))

            metric_id = cursor.lastrowid
            conn.commit()
            logging.info(f"[OK] Atik metrikleri kaydedildi: {period}")
            return metric_id

        except Exception as e:
            logging.error(f"[HATA] Atik metrikleri kaydedilirken hata: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_waste_statistics(self, company_id: int) -> Dict:
        """Atık istatistiklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Toplam atık kayıt sayısı
            cursor.execute("SELECT COUNT(*) FROM waste_records WHERE company_id = ?", (company_id,))
            total_records = cursor.fetchone()[0]

            # Toplam atık türü sayısı
            cursor.execute("SELECT COUNT(DISTINCT waste_code) FROM waste_records WHERE company_id = ?", (company_id,))
            total_waste_types = cursor.fetchone()[0]

            # Aktif hedef sayısı
            cursor.execute("SELECT COUNT(*) FROM waste_reduction_targets WHERE company_id = ? AND status = 'Active'", (company_id,))
            active_targets = cursor.fetchone()[0]

            # Aktif proje sayısı
            cursor.execute("SELECT COUNT(*) FROM recycling_projects WHERE company_id = ? AND status IN ('Planning', 'Active')", (company_id,))
            active_projects = cursor.fetchone()[0]

            return {
                'total_records': total_records,
                'total_waste_types': total_waste_types,
                'active_targets': active_targets,
                'active_projects': active_projects
            }

        except Exception as e:
            logging.error(f"[HATA] Atik istatistikleri getirilirken hata: {e}")
            return {}
        finally:
            conn.close()
