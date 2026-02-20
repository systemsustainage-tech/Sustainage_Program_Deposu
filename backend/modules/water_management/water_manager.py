#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SU YÖNETİMİ ANA SINIFI
Su ayak izi hesaplama, tüketim takibi ve verimlilik analizi
"""

import logging
import os
from datetime import date, datetime
from typing import Dict, List, Optional

try:
    from backend.config.database import get_db_path
    from backend.core.base_manager import BaseTenantManager
except ImportError as e:
    import logging
    logging.error(f"Failed to import from backend: {e}")
    # Fallback removed for debugging/enforcement
    raise e

try:
    from .water_calculator import WaterCalculator
except ImportError:
    try:
        from modules.water_management.water_calculator import WaterCalculator
    except ImportError:
        try:
            # Last resort for direct execution
            from water_calculator import WaterCalculator
        except ImportError:
             import sys
             sys.path.append(os.path.dirname(os.path.abspath(__file__)))
             from water_calculator import WaterCalculator
try:
    from .water_factors import WaterFactors
except ImportError:
    try:
        from modules.water_management.water_factors import WaterFactors
    except ImportError:
        try:
            from water_factors import WaterFactors
        except ImportError:
            import sys
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from water_factors import WaterFactors


class WaterManager(BaseTenantManager):
    """Su yönetimi ana sınıfı - SDG 6 uyumlu"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        final_db_path = db_path
        if final_db_path is None:
            try:
                final_db_path = get_db_path()
            except Exception:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                final_db_path = os.path.join(base_dir, "data", "sdg_desktop.sqlite")
        
        if final_db_path and not os.path.isabs(final_db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            final_db_path = os.path.join(base_dir, final_db_path)
            
        super().__init__(final_db_path, company_id)
        
        # Legacy support attributes
        self.db_path = final_db_path
        
        self.calculator = WaterCalculator(self.db_path)
        self.water_factors = WaterFactors(self.db_path)
        self.create_tables()

    def create_tables(self) -> None:
        """Su yönetimi tablolarını oluştur"""
        try:
            # 1. Su tüketimi kayıtları
            self.execute_update("""
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
            rows = self.execute_query("PRAGMA table_info(water_consumption)")
            cols = [row['name'] for row in rows]
            
            if 'period' not in cols:
                self.execute_update("ALTER TABLE water_consumption ADD COLUMN period TEXT")
                # Eski şemadan (year/month) türet
                try:
                    if 'year' in cols:
                        self.execute_update("UPDATE water_consumption SET period = CAST(year AS TEXT)")
                except Exception:
                    pass
            if 'invoice_date' not in cols:
                self.execute_update("ALTER TABLE water_consumption ADD COLUMN invoice_date TEXT")
            if 'due_date' not in cols:
                self.execute_update("ALTER TABLE water_consumption ADD COLUMN due_date TEXT")
            if 'supplier' not in cols:
                self.execute_update("ALTER TABLE water_consumption ADD COLUMN supplier TEXT")

            # 2. Su hedefleri
            self.execute_update("""
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
            self.execute_update("""
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
            self.execute_update("""
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
            self.execute_update("""
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
            self.execute_update("""
                CREATE INDEX IF NOT EXISTS idx_water_consumption_company_period 
                ON water_consumption(company_id, period)
            """)

            self.execute_update("""
                CREATE INDEX IF NOT EXISTS idx_water_targets_company_status 
                ON water_targets(company_id, status)
            """)

            self.execute_update("""
                CREATE INDEX IF NOT EXISTS idx_water_quality_company_date 
                ON water_quality_monitoring(company_id, monitoring_date)
            """)

            logging.info("[OK] Su yonetimi tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[HATA] Su yonetimi tablolari olusturulamadi: {e}")

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
        try:
            # Toplam su hesapla (eğer verilmemişse)
            if total_water == 0:
                total_water = blue_water + green_water + grey_water

            self.execute_update("""
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
            
            rows = self.execute_query("SELECT seq FROM sqlite_sequence WHERE name='water_consumption'")
            if rows:
                return rows[0]['seq']
            return 1

        except Exception as e:
            logging.error(f"Su tüketimi kaydetme hatası: {e}")
            return None

    def get_water_consumption(self, company_id: int, period: Optional[str] = None,
                             consumption_type: Optional[str] = None) -> List[Dict]:
        """Su tüketimi kayıtlarını getir"""
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

        try:
            rows = self.execute_query(query, params)
            
            records = []
            for row in rows:
                records.append({
                    'id': row['id'],
                    'period': row['period'],
                    'consumption_type': row['consumption_type'],
                    'water_source': row['water_source'],
                    'blue_water': row['blue_water'] or 0,
                    'green_water': row['green_water'] or 0,
                    'grey_water': row['grey_water'] or 0,
                    'total_water': row['total_water'] if row['total_water'] is not None else 0,
                    'unit': row['unit'],
                    'water_quality_parameters': row['water_quality_parameters'],
                    'efficiency_ratio': row['efficiency_ratio'] or 0,
                    'recycling_rate': row['recycling_rate'] or 0,
                    'location': row['location'],
                    'process_description': row['process_description'],
                    'responsible_person': row['responsible_person'],
                    'measurement_method': row['measurement_method'],
                    'data_quality': row['data_quality'],
                    'source': row['source'],
                    'notes': row['notes'],
                    'invoice_date': row['invoice_date'],
                    'due_date': row['due_date'],
                    'supplier': row['supplier'],
                    'created_at': row['created_at']
                })
            return records
        except Exception as e:
            logging.error(f"Su tüketimi getirme hatası: {e}")
            return []

    def update_water_consumption(self, consumption_id: int, **updates) -> bool:
        """Su tüketimi kaydını güncelle"""
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

            self.execute_update(query, values)
            return True

        except Exception as e:
            logging.error(f"Su tüketimi güncelleme hatası: {e}")
            return False

    def delete_water_consumption(self, consumption_id: int) -> bool:
        """Su tüketimi kaydını sil"""
        try:
            self.execute_update("DELETE FROM water_consumption WHERE id = ?", (consumption_id,))
            return True
        except Exception as e:
            logging.error(f"Su tüketimi silme hatası: {e}")
            return False

    # ==================== SU HEDEFLERİ ====================

    def add_water_target(self, company_id: int, target_type: str, target_name: str,
                        base_year: int, target_year: int, base_value: float,
                        target_value: float, target_unit: str, water_type: Optional[str] = None,
                        target_scope: Optional[str] = None, sdg_alignment: Optional[str] = None,
                        description: Optional[str] = None, responsible_person: Optional[str] = None,
                        verification_method: Optional[str] = None, notes: Optional[str] = None) -> Optional[int]:
        """Yeni su hedefi ekle"""
        try:
            self.execute_update("""
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
            
            rows = self.execute_query("SELECT seq FROM sqlite_sequence WHERE name='water_targets'")
            if rows:
                return rows[0]['seq']
            return 1

        except Exception as e:
            logging.error(f"Su hedefi kaydetme hatası: {e}")
            return None

    def get_water_targets(self, company_id: int, status: str = 'active') -> List[Dict]:
        """Su hedeflerini getir"""
        try:
            rows = self.execute_query("""
                SELECT id, target_type, target_name, base_year, target_year, base_value,
                       target_value, target_unit, water_type, target_scope, sdg_alignment,
                       description, responsible_person, status, progress_percentage,
                       achievement_date, verification_method, notes, created_at
                FROM water_targets 
                WHERE company_id = ? AND status = ?
                ORDER BY target_year, created_at DESC
            """, (company_id, status))

            targets = []
            for row in rows:
                targets.append({
                    'id': row['id'],
                    'target_type': row['target_type'],
                    'target_name': row['target_name'],
                    'base_year': row['base_year'],
                    'target_year': row['target_year'],
                    'base_value': row['base_value'],
                    'target_value': row['target_value'],
                    'target_unit': row['target_unit'],
                    'water_type': row['water_type'],
                    'target_scope': row['target_scope'],
                    'sdg_alignment': row['sdg_alignment'],
                    'description': row['description'],
                    'responsible_person': row['responsible_person'],
                    'status': row['status'],
                    'progress_percentage': row['progress_percentage'] or 0,
                    'achievement_date': row['achievement_date'],
                    'verification_method': row['verification_method'],
                    'notes': row['notes'],
                    'created_at': row['created_at']
                })
            return targets
        except Exception as e:
            logging.error(f"Su hedefleri getirme hatası: {e}")
            return []

    def update_water_target(self, target_id: int, **updates) -> bool:
        """Su hedefini güncelle"""
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
            self.execute_update(q, values)
            return True
        except Exception as e:
            logging.error(f"Su hedefi güncelleme hatası: {e}")
            return False

    def delete_water_target(self, target_id: int) -> bool:
        """Su hedefini sil"""
        try:
            self.execute_update("DELETE FROM water_targets WHERE id = ?", (target_id,))
            return True
        except Exception as e:
            logging.error(f"Su hedefi silme hatası: {e}")
            return False

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
        try:
            self.execute_update("""
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
            
            rows = self.execute_query("SELECT seq FROM sqlite_sequence WHERE name='water_efficiency_projects'")
            if rows:
                return rows[0]['seq']
            return 1

        except Exception as e:
            logging.error(f"Su verimliliği projesi kaydetme hatası: {e}")
            return None

    def get_efficiency_projects(self, company_id: int, status: Optional[str] = None) -> List[Dict]:
        """Su verimliliği projelerini getir"""
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

        try:
            rows = self.execute_query(query, params)

            projects = []
            for row in rows:
                projects.append({
                    'id': row['id'],
                    'project_name': row['project_name'],
                    'project_type': row['project_type'],
                    'project_description': row['project_description'],
                    'implementation_date': row['implementation_date'],
                    'completion_date': row['completion_date'],
                    'investment_amount': row['investment_amount'],
                    'currency': row['currency'],
                    'expected_savings_m3': row['expected_savings_m3'],
                    'actual_savings_m3': row['actual_savings_m3'],
                    'expected_efficiency_gain': row['expected_efficiency_gain'],
                    'actual_efficiency_gain': row['actual_efficiency_gain'],
                    'water_quality_improvement': row['water_quality_improvement'],
                    'roi_period': row['roi_period'],
                    'status': row['status'],
                    'responsible_person': row['responsible_person'],
                    'sdg_contribution': row['sdg_contribution'],
                    'environmental_impact': row['environmental_impact'],
                    'social_impact': row['social_impact'],
                    'notes': row['notes'],
                    'created_at': row['created_at']
                })
            return projects
        except Exception as e:
            logging.error(f"Su verimliliği projeleri getirme hatası: {e}")
            return []

    def update_efficiency_project(self, project_id: int, **updates) -> bool:
        """Su verimliliği projesini güncelle"""
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
            self.execute_update(q, values)
            return True
        except Exception as e:
            logging.error(f"Su verimliliği projesi güncelleme hatası: {e}")
            return False

    def delete_efficiency_project(self, project_id: int) -> bool:
        """Su verimliliği projesini sil"""
        try:
            self.execute_update("DELETE FROM water_efficiency_projects WHERE id = ?", (project_id,))
            return True
        except Exception as e:
            logging.error(f"Su verimliliği projesi silme hatası: {e}")
            return False

    # ==================== SU KALİTESİ İZLEME ====================

    def add_quality_measurement(self, company_id: int, monitoring_date: date, water_source: str,
                               location: str, parameter_name: str, parameter_value: float,
                               parameter_unit: str, measurement_method: Optional[str] = None,
                               standard_limit: Optional[float] = None, compliance_status: Optional[str] = None,
                               responsible_lab: Optional[str] = None, certification: Optional[str] = None,
                               notes: Optional[str] = None) -> Optional[int]:
        """Yeni su kalitesi ölçümü ekle"""
        try:
            self.execute_update("""
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
            
            rows = self.execute_query("SELECT seq FROM sqlite_sequence WHERE name='water_quality_monitoring'")
            if rows:
                return rows[0]['seq']
            return 1

        except Exception as e:
            logging.error(f"Su kalitesi ölçümü kaydetme hatası: {e}")
            return None

    def get_quality_measurements(self, company_id: int, water_source: Optional[str] = None,
                                start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict]:
        """Su kalitesi ölçümlerini getir"""
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

        try:
            rows = self.execute_query(query, params)

            measurements = []
            for row in rows:
                measurements.append({
                    'id': row['id'],
                    'monitoring_date': row['monitoring_date'],
                    'water_source': row['water_source'],
                    'location': row['location'],
                    'parameter_name': row['parameter_name'],
                    'parameter_value': row['parameter_value'],
                    'parameter_unit': row['parameter_unit'],
                    'measurement_method': row['measurement_method'],
                    'standard_limit': row['standard_limit'],
                    'compliance_status': row['compliance_status'],
                    'responsible_lab': row['responsible_lab'],
                    'certification': row['certification'],
                    'notes': row['notes'],
                    'created_at': row['created_at']
                })
            return measurements
        except Exception as e:
            logging.error(f"Su kalitesi ölçümleri getirme hatası: {e}")
            return []

    def update_quality_measurement(self, measurement_id: int, **updates) -> bool:
        """Su kalitesi ölçümünü güncelle"""
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
            self.execute_update(q, values)
            return True
        except Exception as e:
            logging.error(f"Su kalitesi ölçümü güncelleme hatası: {e}")
            return False

    def delete_quality_measurement(self, measurement_id: int) -> bool:
        """Su kalitesi ölçümünü sil"""
        try:
            self.execute_update("DELETE FROM water_quality_monitoring WHERE id = ?", (measurement_id,))
            return True
        except Exception as e:
            logging.error(f"Su kalitesi ölçümü silme hatası: {e}")
            return False

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
