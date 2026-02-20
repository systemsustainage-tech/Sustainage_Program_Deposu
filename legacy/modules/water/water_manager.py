#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SU YÖNETİMİ ANA SINIFI
Su ayak izi hesaplama, tüketim takibi ve verimlilik analizi
"""

import logging
import os
import sqlite3
from datetime import date, datetime
from typing import Dict, List, Optional

from .water_calculator import WaterCalculator
from .water_factors import WaterFactors


class WaterManager:
    """Su yönetimi ana sınıfı - SDG 6 uyumlu"""

    def __init__(self, db_path: str = None) -> None:
        if db_path is None:
            # Default to sustainage.db in project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, 'sustainage.db')
        
        self.db_path = db_path
        self.calculator = WaterCalculator(self.db_path)
        self.water_factors = WaterFactors(self.db_path)
        self.create_tables()

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_tables(self) -> None:
        """Su yönetimi tablolarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Su tüketimi kayıtları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS water_consumption (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,                    -- 2024, 2024-Q1, etc.
                    consumption_type TEXT NOT NULL,          -- industrial, agricultural, domestic, process
                    water_source TEXT NOT NULL,              -- groundwater, surface_water, municipal, recycled
                    blue_water REAL,                         -- Mavi su (m³)
                    green_water REAL,                        -- Yeşil su (m³)
                    grey_water REAL,                         -- Gri su (m³)
                    total_water REAL NOT NULL,               -- Toplam su (m³)
                    unit TEXT DEFAULT 'm3',
                    water_quality_parameters TEXT,           -- JSON: pH, TDS, BOD, etc.
                    efficiency_ratio REAL,                   -- Verimlilik oranı (0-1)
                    recycling_rate REAL,                     -- Geri dönüşüm oranı (0-1)
                    location TEXT,                           -- Tüketim lokasyonu
                    process_description TEXT,                -- Süreç açıklaması
                    responsible_person TEXT,
                    measurement_method TEXT,                 -- ölçüm, tahmin, hesaplama
                    data_quality TEXT,                       -- high, medium, low
                    source TEXT,                             -- Veri kaynağı
                    evidence_file TEXT,                      -- Destekleyici dosya
                    notes TEXT,
                    invoice_date TEXT,                       -- Fatura tarihi (YYYY-MM-DD)
                    due_date TEXT,                           -- Son ödeme tarihi (YYYY-MM-DD)
                    supplier TEXT,                           -- Tedarikçi firma
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # Migration: eksik sütunları ekle
            cursor.execute("PRAGMA table_info(water_consumption)")
            cols = [c[1] for c in cursor.fetchall()]
            if 'period' not in cols:
                cursor.execute("ALTER TABLE water_consumption ADD COLUMN period TEXT")
                try:
                    if 'year' in cols:
                        cursor.execute("UPDATE water_consumption SET period = CAST(year AS TEXT)")
                except Exception:
                    pass
            if 'invoice_date' not in cols:
                cursor.execute("ALTER TABLE water_consumption ADD COLUMN invoice_date TEXT")
            if 'due_date' not in cols:
                cursor.execute("ALTER TABLE water_consumption ADD COLUMN due_date TEXT")
            if 'supplier' not in cols:
                cursor.execute("ALTER TABLE water_consumption ADD COLUMN supplier TEXT")

            # 2. Su hedefleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS water_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    -- consumption_reduction, efficiency_improvement, recycling_increase
                    target_name TEXT NOT NULL,
                    base_year INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    base_value REAL NOT NULL,                -- Başlangıç değeri
                    target_value REAL NOT NULL,              -- Hedef değer
                    target_unit TEXT NOT NULL,               -- m3, percentage, ratio
                    water_type TEXT,                         -- blue, green, grey, total
                    target_scope TEXT,                       -- process, facility, company
                    sdg_alignment TEXT,                      -- SDG 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
                    description TEXT,
                    responsible_person TEXT,
                    status TEXT DEFAULT 'active',            -- active, achieved, cancelled
                    progress_percentage REAL DEFAULT 0,      -- İlerleme yüzdesi
                    achievement_date DATE,
                    verification_method TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 3. Su verimliliği projeleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS water_efficiency_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    project_name TEXT NOT NULL,
                    project_type TEXT NOT NULL,              -- recycling, reuse, reduction, treatment
                    project_description TEXT,
                    implementation_date DATE,
                    completion_date DATE,
                    investment_amount REAL,                  -- Yatırım tutarı
                    currency TEXT DEFAULT 'TRY',
                    expected_savings_m3 REAL,                -- Beklenen tasarruf (m³/yıl)
                    actual_savings_m3 REAL,                  -- Gerçekleşen tasarruf
                    expected_efficiency_gain REAL,           -- Beklenen verimlilik artışı (%)
                    actual_efficiency_gain REAL,             -- Gerçekleşen verimlilik artışı
                    water_quality_improvement TEXT,          -- Su kalitesi iyileştirmesi
                    roi_period REAL,                         -- Yatırım geri dönüş süresi (yıl)
                    status TEXT DEFAULT 'planned',           -- planned, ongoing, completed, cancelled
                    responsible_person TEXT,
                    sdg_contribution TEXT,                   -- SDG katkıları (JSON)
                    environmental_impact TEXT,               -- Çevresel etki
                    social_impact TEXT,                      -- Sosyal etki
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 4. Su kalitesi izleme
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS water_quality_monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    monitoring_date DATE NOT NULL,
                    water_source TEXT NOT NULL,              -- intake, discharge, process
                    location TEXT NOT NULL,                  -- Ölçüm noktası
                    parameter_name TEXT NOT NULL,            -- pH, TDS, BOD, COD, etc.
                    parameter_value REAL NOT NULL,
                    parameter_unit TEXT NOT NULL,            -- mg/L, pH, NTU, etc.
                    measurement_method TEXT,                 -- Ölçüm metodu
                    standard_limit REAL,                     -- Standart limit değer
                    compliance_status TEXT,                  -- compliant, non_compliant, warning
                    responsible_lab TEXT,                    -- Sorumlu laboratuvar
                    certification TEXT,                      -- Laboratuvar sertifikası
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 5. Su raporları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS water_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    report_period TEXT NOT NULL,
                    report_type TEXT,                        -- annual, quarterly, water_footprint
                    total_blue_water REAL,
                    total_green_water REAL,
                    total_grey_water REAL,
                    total_water_footprint REAL NOT NULL,     -- Toplam su ayak izi (m³)
                    water_intensity REAL,                    -- Su yoğunluğu (m³/ürün birimi)
                    recycling_rate REAL,                     -- Geri dönüşüm oranı
                    efficiency_ratio REAL,                   -- Verimlilik oranı
                    water_stress_level TEXT,                 -- low, medium, high, critical
                    sdg_6_progress REAL,                     -- SDG 6 ilerleme skoru (0-100)
                    boundary_description TEXT,               -- Sistem sınırları
                    methodology TEXT,                        -- Hesaplama metodolojisi
                    verification_status TEXT,                -- unverified, third_party, internal
                    verifier_name TEXT,
                    verification_date DATE,
                    report_file_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # İndeksler
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_water_consumption_company_period 
                ON water_consumption(company_id, period)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_water_targets_company_status 
                ON water_targets(company_id, status)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_water_quality_company_date 
                ON water_quality_monitoring(company_id, monitoring_date)
            """)

            conn.commit()
            logging.info("[OK] Su yonetimi tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Su yonetimi tablolari olusturulamadi: {e}")
            conn.rollback()
        finally:
            conn.close()

    # ==================== SU TÜKETİMİ KAYITLARI (CRUD) ====================

    def add_water_consumption(
        self,
        company_id: int,
        period: str,
        consumption_type: str,
        water_source: str,
        blue_water: float = 0,
        green_water: float = 0,
        grey_water: float = 0,
        total_water: float = 0,
        unit: str = 'm3',
        water_quality_parameters: Optional[str] = None,
        efficiency_ratio: float = 0,
        recycling_rate: float = 0,
        location: Optional[str] = None,
        process_description: Optional[str] = None,
        responsible_person: Optional[str] = None,
        measurement_method: str = 'calculation',
        data_quality: str = 'medium',
        source: Optional[str] = None,
        evidence_file: Optional[str] = None,
        notes: Optional[str] = None,
        invoice_date: Optional[str] = None,
        due_date: Optional[str] = None,
        supplier: Optional[str] = None,
    ) -> Optional[int]:
        """Yeni su tüketimi kaydı ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Toplam su hesapla (eğer verilmemişse)
            if total_water == 0:
                total_water = blue_water + green_water + grey_water

            # Yil bilgisini cikar
            try:
                year_val = int(str(period).split('-')[0]) if '-' in str(period) else int(period)
            except:
                year_val = datetime.now().year

            cursor.execute("""
                INSERT INTO water_consumption 
                (company_id, period, consumption_type, water_source, blue_water, green_water, 
                 grey_water, total_water, unit, water_quality_parameters, efficiency_ratio,
                 recycling_rate, location, process_description, responsible_person,
                 measurement_method, data_quality, source, evidence_file, notes,
                 invoice_date, due_date, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, period, consumption_type, water_source, blue_water, green_water,
                grey_water, total_water, unit, water_quality_parameters, efficiency_ratio,
                recycling_rate, location, process_description, responsible_person,
                measurement_method, data_quality, source, evidence_file, notes or '',
                invoice_date, due_date, supplier
            ))

            consumption_id = cursor.lastrowid
            conn.commit()
            return consumption_id

        except Exception as e:
            logging.error(f"Su tüketimi kaydetme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_water_consumption(self, company_id: int, period: Optional[str] = None,
                             consumption_type: Optional[str] = None) -> List[Dict]:
        """Su tüketimi kayıtlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, period, consumption_type, water_source, blue_water, green_water,
                   grey_water, total_water, unit, water_quality_parameters, efficiency_ratio,
                   recycling_rate, location, process_description, responsible_person,
                   measurement_method, data_quality, source, notes, invoice_date, due_date, supplier, created_at
            FROM water_consumption 
            WHERE company_id = ?
        """
        params: list[object] = [company_id]

        if period:
            query += " AND period = ?"
            params.append(period)

        if consumption_type:
            query += " AND consumption_type = ?"
            params.append(consumption_type)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)

        records = []
        for row in cursor.fetchall():
            records.append({
                'id': row[0],
                'period': row[1],
                'consumption_type': row[2],
                'water_source': row[3],
                'blue_water': row[4] or 0,
                'green_water': row[5] or 0,
                'grey_water': row[6] or 0,
                'total_water': row[7] if isinstance(row[7], (int, float)) else (row[7] or 0),
                'unit': row[8],
                'water_quality_parameters': row[9],
                'efficiency_ratio': row[10] or 0,
                'recycling_rate': row[11] or 0,
                'location': row[12],
                'process_description': row[13],
                'responsible_person': row[14],
                'measurement_method': row[15],
                'data_quality': row[16],
                'source': row[17],
                'notes': row[18],
                'invoice_date': row[19],
                'due_date': row[20],
                'supplier': row[21],
                'created_at': row[22]
            })

        conn.close()
        return records

    def update_water_consumption(self, consumption_id: int, **updates) -> bool:
        """Su tüketimi kaydını güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Güncellenebilir alanlar
            allowed_fields = ['period', 'consumption_type', 'water_source', 'blue_water',
                            'green_water', 'grey_water', 'total_water', 'unit',
                            'water_quality_parameters', 'efficiency_ratio', 'recycling_rate',
                            'location', 'process_description', 'responsible_person',
                            'measurement_method', 'data_quality', 'source', 'notes',
                            'invoice_date', 'due_date', 'supplier']

            update_fields = []
            values = []

            for field, value in updates.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = ?")
                    values.append(value)

            if not update_fields:
                return False

            values.append(consumption_id)

            query = f"""
                UPDATE water_consumption 
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """

            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logging.error(f"Su tüketimi güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_water_consumption(self, consumption_id: int) -> bool:
        """Su tüketimi kaydını sil"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM water_consumption WHERE id = ?", (consumption_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Su tüketimi silme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==================== SU HEDEFLERİ ====================

    def add_water_target(self, company_id: int, target_type: str, target_name: str,
                        base_year: int, target_year: int, base_value: float,
                        target_value: float, target_unit: str, water_type: Optional[str] = None,
                        target_scope: Optional[str] = None, sdg_alignment: Optional[str] = None,
                        description: Optional[str] = None, responsible_person: Optional[str] = None,
                        verification_method: Optional[str] = None, notes: Optional[str] = None) -> Optional[int]:
        """Yeni su hedefi ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO water_targets 
                (company_id, target_type, target_name, base_year, target_year, base_value,
                 target_value, target_unit, water_type, target_scope, sdg_alignment,
                 description, responsible_person, verification_method, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, target_type, target_name, base_year, target_year, base_value,
                target_value, target_unit, water_type, target_scope, sdg_alignment,
                description, responsible_person, verification_method, notes or ''
            ))

            target_id = cursor.lastrowid
            conn.commit()
            return target_id

        except Exception as e:
            logging.error(f"Su hedefi kaydetme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_water_targets(self, company_id: int, status: str = 'active') -> List[Dict]:
        """Su hedeflerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, target_type, target_name, base_year, target_year, base_value,
                   target_value, target_unit, water_type, target_scope, sdg_alignment,
                   description, responsible_person, status, progress_percentage,
                   achievement_date, verification_method, notes, created_at
            FROM water_targets 
            WHERE company_id = ? AND status = ?
            ORDER BY target_year, created_at DESC
        """, (company_id, status))

        targets = []
        for row in cursor.fetchall():
            targets.append({
                'id': row[0],
                'target_type': row[1],
                'target_name': row[2],
                'base_year': row[3],
                'target_year': row[4],
                'base_value': row[5],
                'target_value': row[6],
                'target_unit': row[7],
                'water_type': row[8],
                'target_scope': row[9],
                'sdg_alignment': row[10],
                'description': row[11],
                'responsible_person': row[12],
                'status': row[13],
                'progress_percentage': row[14] or 0,
                'achievement_date': row[15],
                'verification_method': row[16],
                'notes': row[17],
                'created_at': row[18]
            })

        conn.close()
        return targets

    def update_water_target(self, target_id: int, **updates) -> bool:
        """Su hedefini güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            allowed = [
                'target_type', 'target_name', 'base_year', 'target_year', 'base_value',
                'target_value', 'target_unit', 'water_type', 'target_scope', 'sdg_alignment',
                'description', 'responsible_person', 'status', 'progress_percentage',
                'achievement_date', 'verification_method', 'notes'
            ]
            fields = []
            values = []
            for k, v in updates.items():
                if k in allowed:
                    fields.append(f"{k} = ?")
                    values.append(v)
            if not fields:
                return False
            values.append(target_id)
            q = f"UPDATE water_targets SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(q, values)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Su hedefi güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_water_target(self, target_id: int) -> bool:
        """Su hedefini sil"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM water_targets WHERE id = ?", (target_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Su hedefi silme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==================== SU VERİMLİLİĞİ PROJELERİ ====================

    def add_efficiency_project(
        self,
        company_id: int,
        project_name: str,
        project_type: str,
        project_description: Optional[str] = None,
        implementation_date: Optional[date] = None,
        completion_date: Optional[date] = None,
        investment_amount: Optional[float] = None,
        currency: str = 'TRY',
        expected_savings_m3: Optional[float] = None,
        actual_savings_m3: Optional[float] = None,
        expected_efficiency_gain: Optional[float] = None,
        actual_efficiency_gain: Optional[float] = None,
        water_quality_improvement: Optional[str] = None,
        roi_period: Optional[float] = None,
        responsible_person: Optional[str] = None,
        sdg_contribution: Optional[str] = None,
        environmental_impact: Optional[str] = None,
        social_impact: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[int]:
        """Yeni su verimliliği projesi ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO water_efficiency_projects 
                (company_id, project_name, project_type, project_description, implementation_date,
                 completion_date, investment_amount, currency, expected_savings_m3, actual_savings_m3,
                 expected_efficiency_gain, actual_efficiency_gain, water_quality_improvement,
                 roi_period, responsible_person, sdg_contribution, environmental_impact,
                 social_impact, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, project_name, project_type, project_description, implementation_date,
                completion_date, investment_amount, currency, expected_savings_m3, actual_savings_m3,
                expected_efficiency_gain, actual_efficiency_gain, water_quality_improvement,
                roi_period, responsible_person, sdg_contribution, environmental_impact,
                social_impact, notes or ''
            ))

            project_id = cursor.lastrowid
            conn.commit()
            return project_id

        except Exception as e:
            logging.error(f"Su verimliliği projesi kaydetme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_efficiency_projects(self, company_id: int, status: Optional[str] = None) -> List[Dict]:
        """Su verimliliği projelerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, project_name, project_type, project_description, implementation_date,
                   completion_date, investment_amount, currency, expected_savings_m3, actual_savings_m3,
                   expected_efficiency_gain, actual_efficiency_gain, water_quality_improvement,
                   roi_period, status, responsible_person, sdg_contribution, environmental_impact,
                   social_impact, notes, created_at
            FROM water_efficiency_projects 
            WHERE company_id = ?
        """
        params: list[object] = [company_id]

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)

        projects = []
        for row in cursor.fetchall():
            projects.append({
                'id': row[0],
                'project_name': row[1],
                'project_type': row[2],
                'project_description': row[3],
                'implementation_date': row[4],
                'completion_date': row[5],
                'investment_amount': row[6],
                'currency': row[7],
                'expected_savings_m3': row[8],
                'actual_savings_m3': row[9],
                'expected_efficiency_gain': row[10],
                'actual_efficiency_gain': row[11],
                'water_quality_improvement': row[12],
                'roi_period': row[13],
                'status': row[14],
                'responsible_person': row[15],
                'sdg_contribution': row[16],
                'environmental_impact': row[17],
                'social_impact': row[18],
                'notes': row[19],
                'created_at': row[20]
            })

        conn.close()
        return projects

    def update_efficiency_project(self, project_id: int, **updates) -> bool:
        """Su verimliliği projesini güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            allowed = [
                'project_name', 'project_type', 'project_description', 'implementation_date',
                'completion_date', 'investment_amount', 'currency', 'expected_savings_m3',
                'actual_savings_m3', 'expected_efficiency_gain', 'actual_efficiency_gain',
                'water_quality_improvement', 'roi_period', 'status', 'responsible_person',
                'sdg_contribution', 'environmental_impact', 'social_impact', 'notes'
            ]
            fields = []
            values = []
            for k, v in updates.items():
                if k in allowed:
                    fields.append(f"{k} = ?")
                    values.append(v)
            if not fields:
                return False
            values.append(project_id)
            q = f"UPDATE water_efficiency_projects SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(q, values)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Su verimliliği projesi güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_efficiency_project(self, project_id: int) -> bool:
        """Su verimliliği projesini sil"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM water_efficiency_projects WHERE id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Su verimliliği projesi silme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==================== SU KALİTESİ İZLEME ====================

    def add_quality_measurement(self, company_id: int, monitoring_date: date, water_source: str,
                               location: str, parameter_name: str, parameter_value: float,
                               parameter_unit: str, measurement_method: Optional[str] = None,
                               standard_limit: Optional[float] = None, compliance_status: Optional[str] = None,
                               responsible_lab: Optional[str] = None, certification: Optional[str] = None,
                               notes: Optional[str] = None) -> Optional[int]:
        """Yeni su kalitesi ölçümü ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO water_quality_monitoring 
                (company_id, monitoring_date, water_source, location, parameter_name,
                 parameter_value, parameter_unit, measurement_method, standard_limit,
                 compliance_status, responsible_lab, certification, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, monitoring_date, water_source, location, parameter_name,
                parameter_value, parameter_unit, measurement_method, standard_limit,
                compliance_status, responsible_lab, certification, notes or ''
            ))

            measurement_id = cursor.lastrowid
            conn.commit()
            return measurement_id

        except Exception as e:
            logging.error(f"Su kalitesi ölçümü kaydetme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_quality_measurements(self, company_id: int, water_source: Optional[str] = None,
                                start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict]:
        """Su kalitesi ölçümlerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, monitoring_date, water_source, location, parameter_name,
                   parameter_value, parameter_unit, measurement_method, standard_limit,
                   compliance_status, responsible_lab, certification, notes, created_at
            FROM water_quality_monitoring 
            WHERE company_id = ?
        """
        params: list[object] = [company_id]

        if water_source:
            query += " AND water_source = ?"
            params.append(water_source)

        if start_date:
            query += " AND monitoring_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND monitoring_date <= ?"
            params.append(end_date)

        query += " ORDER BY monitoring_date DESC, parameter_name"

        cursor.execute(query, params)

        measurements = []
        for row in cursor.fetchall():
            measurements.append({
                'id': row[0],
                'monitoring_date': row[1],
                'water_source': row[2],
                'location': row[3],
                'parameter_name': row[4],
                'parameter_value': row[5],
                'parameter_unit': row[6],
                'measurement_method': row[7],
                'standard_limit': row[8],
                'compliance_status': row[9],
                'responsible_lab': row[10],
                'certification': row[11],
                'notes': row[12],
                'created_at': row[13]
            })

        conn.close()
        return measurements

    def update_quality_measurement(self, measurement_id: int, **updates) -> bool:
        """Su kalitesi ölçümünü güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            allowed = [
                'monitoring_date', 'water_source', 'location', 'parameter_name',
                'parameter_value', 'parameter_unit', 'measurement_method', 'standard_limit',
                'compliance_status', 'responsible_lab', 'certification', 'notes'
            ]
            fields = []
            values = []
            for k, v in updates.items():
                if k in allowed:
                    fields.append(f"{k} = ?")
                    values.append(v)
            if not fields:
                return False
            values.append(measurement_id)
            q = f"UPDATE water_quality_monitoring SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(q, values)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Su kalitesi ölçümü güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_quality_measurement(self, measurement_id: int) -> bool:
        """Su kalitesi ölçümünü sil"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM water_quality_monitoring WHERE id = ?", (measurement_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Su kalitesi ölçümü silme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==================== SU AYAK İZİ HESAPLAMA ====================

    def calculate_water_footprint(self, company_id: int, period: str) -> Dict:
        """Su ayak izi hesapla"""
        try:
            # Tüketim verilerini getir
            consumption_data = self.get_water_consumption(company_id, period)

            if not consumption_data:
                return {
                    'total_blue_water': 0,
                    'total_green_water': 0,
                    'total_grey_water': 0,
                    'total_water_footprint': 0,
                    'breakdown_by_type': {},
                    'breakdown_by_source': {},
                    'efficiency_metrics': {},
                    'calculated_at': datetime.now().isoformat()
                }

            # Toplam hesaplamalar
            total_blue = sum(record['blue_water'] for record in consumption_data)
            total_green = sum(record['green_water'] for record in consumption_data)
            total_grey = sum(record['grey_water'] for record in consumption_data)
            total_footprint = total_blue + total_green + total_grey

            # Tüketim türüne göre dağılım
            breakdown_by_type = {}
            for record in consumption_data:
                consumption_type = record['consumption_type']
                if consumption_type not in breakdown_by_type:
                    breakdown_by_type[consumption_type] = {
                        'blue_water': 0, 'green_water': 0, 'grey_water': 0, 'total': 0
                    }

                breakdown_by_type[consumption_type]['blue_water'] += record['blue_water']
                breakdown_by_type[consumption_type]['green_water'] += record['green_water']
                breakdown_by_type[consumption_type]['grey_water'] += record['grey_water']
                breakdown_by_type[consumption_type]['total'] += record['total_water']

            # Su kaynağına göre dağılım
            breakdown_by_source = {}
            for record in consumption_data:
                water_source = record['water_source']
                if water_source not in breakdown_by_source:
                    breakdown_by_source[water_source] = {
                        'blue_water': 0, 'green_water': 0, 'grey_water': 0, 'total': 0
                    }

                breakdown_by_source[water_source]['blue_water'] += record['blue_water']
                breakdown_by_source[water_source]['green_water'] += record['green_water']
                breakdown_by_source[water_source]['grey_water'] += record['grey_water']
                breakdown_by_source[water_source]['total'] += record['total_water']

            # Verimlilik metrikleri
            avg_efficiency = (
                sum(record['efficiency_ratio'] for record in consumption_data)
                / len(consumption_data)
                if consumption_data
                else 0
            )
            avg_recycling = (
                sum(record['recycling_rate'] for record in consumption_data)
                / len(consumption_data)
                if consumption_data
                else 0
            )

            efficiency_metrics = {
                'average_efficiency_ratio': round(avg_efficiency, 3),
                'average_recycling_rate': round(avg_recycling, 3),
                'total_records': len(consumption_data),
                'high_quality_data': len([r for r in consumption_data if r['data_quality'] == 'high']),
                'medium_quality_data': len([r for r in consumption_data if r['data_quality'] == 'medium']),
                'low_quality_data': len([r for r in consumption_data if r['data_quality'] == 'low'])
            }

            return {
                'total_blue_water': round(total_blue, 2),
                'total_green_water': round(total_green, 2),
                'total_grey_water': round(total_grey, 2),
                'total_water_footprint': round(total_footprint, 2),
                'breakdown_by_type': breakdown_by_type,
                'breakdown_by_source': breakdown_by_source,
                'efficiency_metrics': efficiency_metrics,
                'period': period,
                'calculated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"Su ayak izi hesaplama hatası: {e}")
            return {}

    # ==================== SU RAPORLARI ====================

    def save_water_report(self, company_id: int, period: str, report_type: str,
                         total_blue_water: float, total_green_water: float,
                         total_grey_water: float, total_water_footprint: float,
                         water_intensity: Optional[float] = None, recycling_rate: Optional[float] = None,
                         efficiency_ratio: Optional[float] = None, water_stress_level: Optional[str] = None,
                         sdg_6_progress: Optional[float] = None, boundary_description: Optional[str] = None,
                         methodology: Optional[str] = None, verification_status: Optional[str] = None,
                         verifier_name: Optional[str] = None, verification_date: Optional[date] = None,
                         report_file_path: Optional[str] = None) -> Optional[int]:
        """Su raporu kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO water_reports 
                (company_id, report_period, report_type, total_blue_water, total_green_water,
                 total_grey_water, total_water_footprint, water_intensity, recycling_rate,
                 efficiency_ratio, water_stress_level, sdg_6_progress, boundary_description,
                 methodology, verification_status, verifier_name, verification_date, report_file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, period, report_type, total_blue_water, total_green_water,
                total_grey_water, total_water_footprint, water_intensity, recycling_rate,
                efficiency_ratio, water_stress_level, sdg_6_progress, boundary_description,
                methodology, verification_status, verifier_name, verification_date, report_file_path
            ))

            report_id = cursor.lastrowid
            conn.commit()
            return report_id

        except Exception as e:
            logging.error(f"Su raporu kaydetme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_water_reports(self, company_id: int) -> List[Dict]:
        """Su raporlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, report_period, report_type, total_blue_water, total_green_water,
                   total_grey_water, total_water_footprint, water_intensity, recycling_rate,
                   efficiency_ratio, water_stress_level, sdg_6_progress, boundary_description,
                   methodology, verification_status, verifier_name, verification_date,
                   report_file_path, created_at
            FROM water_reports 
            WHERE company_id = ?
            ORDER BY report_period DESC, created_at DESC
        """, (company_id,))

        reports = []
        for row in cursor.fetchall():
            reports.append({
                'id': row[0],
                'report_period': row[1],
                'report_type': row[2],
                'total_blue_water': row[3] or 0,
                'total_green_water': row[4] or 0,
                'total_grey_water': row[5] or 0,
                'total_water_footprint': row[6] or 0,
                'water_intensity': row[7],
                'recycling_rate': row[8],
                'efficiency_ratio': row[9],
                'water_stress_level': row[10],
                'sdg_6_progress': row[11],
                'boundary_description': row[12],
                'methodology': row[13],
                'verification_status': row[14],
                'verifier_name': row[15],
                'verification_date': row[16],
                'report_file_path': row[17],
                'created_at': row[18]
            })

        conn.close()
        return reports
