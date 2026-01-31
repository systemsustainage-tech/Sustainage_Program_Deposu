#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KARBON YÖNETİCİ SINIFI
Karbon emisyon verilerinin yönetimi ve raporlama
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List

from .carbon_calculator import CarbonCalculator
from .emission_factors import EmissionFactors
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CarbonManager:
    """Karbon emisyon yönetimi ana sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.calculator = CarbonCalculator(db_path)
        self.emission_factors = EmissionFactors(db_path)

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_tables(self) -> None:
        """Karbon modülü tablolarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Emisyon kayıtları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_emissions (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,                -- 2024, 2024-Q1, etc.
                    scope TEXT NOT NULL,                 -- scope1, scope2, scope3
                    category TEXT NOT NULL,              -- stationary, mobile, fugitive, electricity, etc.
                    subcategory TEXT,                    -- Scope 3 için kategori numarası
                    fuel_type TEXT NOT NULL,             -- natural_gas, diesel, etc.
                    quantity REAL NOT NULL,              -- Miktar
                    unit TEXT NOT NULL,                  -- m3, litre, kWh, etc.
                    co2_emissions REAL,                  -- tCO2
                    ch4_emissions REAL,                  -- tCH4
                    n2o_emissions REAL,                  -- tN2O
                    co2e_emissions REAL NOT NULL,        -- Total tCO2e
                    emission_factor_source TEXT,         -- Faktör kaynağı
                    calculation_method TEXT,             -- Hesaplama metodu
                    data_quality TEXT DEFAULT 'measured', -- measured, estimated, default
                    source TEXT,                         -- Veri kaynağı
                    evidence_file TEXT,                  -- Kanıt dosyası
                    data_json TEXT,                      -- Ek veriler (JSON)
                    verified BOOLEAN DEFAULT 0,
                    verified_by TEXT,
                    verified_at TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 2. Karbon hedefleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_targets (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    target_name TEXT NOT NULL,
                    target_description TEXT,
                    scope_coverage TEXT NOT NULL,        -- scope1, scope1_2, scope1_2_3
                    baseline_year INTEGER NOT NULL,
                    baseline_co2e REAL NOT NULL,         -- Baz yıl emisyonu
                    target_year INTEGER NOT NULL,
                    target_co2e REAL NOT NULL,           -- Hedef emisyon
                    target_reduction_pct REAL,           -- Hedef azaltma %
                    target_type TEXT,                    -- absolute, intensity
                    intensity_metric TEXT,               -- revenue, employee, production
                    commitment_level TEXT,               -- committed, aspirational
                    sbti_approved BOOLEAN DEFAULT 0,     -- Science Based Target Initiative
                    status TEXT DEFAULT 'active',        -- active, achieved, missed, revised
                    progress_pct REAL DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 3. Azaltma girişimleri tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_reduction_initiatives (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    initiative_name TEXT NOT NULL,
                    initiative_description TEXT,
                    initiative_type TEXT,                -- energy_efficiency, renewable, process_change, etc.
                    target_scope TEXT,                   -- scope1, scope2, scope3
                    start_date DATE,
                    end_date DATE,
                    investment_amount REAL,              -- Yatırım tutarı
                    expected_reduction_co2e REAL,        -- Beklenen azaltma (tCO2e/yıl)
                    actual_reduction_co2e REAL,          -- Gerçekleşen azaltma
                    status TEXT DEFAULT 'planned',       -- planned, ongoing, completed, cancelled
                    roi_years REAL,                      -- Return on Investment (yıl)
                    sdg_alignment TEXT,                  -- İlgili SDG'ler (JSON)
                    responsible_person TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 4. Emisyon raporları tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_reports (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    report_period TEXT NOT NULL,
                    report_type TEXT,                    -- annual, quarterly, verification
                    scope1_total REAL,
                    scope2_total REAL,
                    scope3_total REAL,
                    total_co2e REAL NOT NULL,
                    boundary_description TEXT,           -- Organizational boundary
                    base_year INTEGER,
                    reporting_standard TEXT DEFAULT 'GHG Protocol',
                    verification_status TEXT,            -- unverified, third_party, internal
                    verifier_name TEXT,
                    verification_date DATE,
                    report_file_path TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 5. Özel emisyon faktörleri (EmissionFactors sınıfından)
            self.emission_factors.create_emission_factors_table()

            # İndeksler
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_carbon_emissions_company_period 
                ON carbon_emissions(company_id, period)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_carbon_emissions_scope 
                ON carbon_emissions(scope, category)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_carbon_targets_company 
                ON carbon_targets(company_id)
            """)

            conn.commit()
            logging.info("[OK] Karbon modulu tablolari basariyla olusturuldu")
            return True

        except Exception as e:
            logging.error(f"Karbon tabloları oluşturma hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==================== EMİSYON KAYITLARI (CRUD) ====================

    def add_emission(self, company_id: int, period: str, scope: str,
                    category: str, fuel_type: str, quantity: float,
                    unit: str, co2e_emission: float, notes: str = None) -> int:
        """Yeni emisyon kaydı ekle - add_emission alias"""
        return self.save_emission_record(company_id, period, scope, category,
                                       fuel_type, quantity, unit, notes=notes, co2e_emission=co2e_emission)

    def save_emission_record(self, company_id: int, period: str, scope: str,
                           category: str, fuel_type: str, quantity: float,
                           unit: str, **kwargs) -> int:
        """
        Emisyon kaydı kaydet
        
        Args:
            company_id: Şirket ID
            period: Dönem
            scope: scope1, scope2, scope3
            category: stationary, mobile, fugitive, electricity, etc.
            fuel_type: Yakıt/kaynak türü
            quantity: Miktar
            unit: Birim
            **kwargs: Ek alanlar
        
        Returns:
            emission_id veya None
        """
        # CO2e hesapla (eğer kwargs'da yoksa)
        co2e_emission = kwargs.get('co2e_emission')
        if co2e_emission is None:
            try:
                calc_result = self.emission_factors.calculate_co2e(
                    scope=scope,
                    category=category,
                    fuel_type=fuel_type,
                    quantity=quantity
                )
                co2e_emission = calc_result['co2e']
            except Exception as e:
                logging.error(f"Emisyon hesaplama hatası: {e}")
                return None

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO carbon_emissions 
                (company_id, period, scope, category, subcategory, fuel_type, 
                 quantity, unit, co2_emissions, ch4_emissions, n2o_emissions, 
                 co2e_emissions, emission_factor_source, calculation_method,
                 data_quality, source, evidence_file, data_json, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                period,
                scope,
                category,
                kwargs.get('subcategory'),
                fuel_type,
                quantity,
                unit,
                kwargs.get('co2_emissions', 0),
                kwargs.get('ch4_emissions', 0),
                kwargs.get('n2o_emissions', 0),
                co2e_emission,
                kwargs.get('emission_factor_source', 'Standard'),
                kwargs.get('calculation_method', 'standard'),
                kwargs.get('data_quality', 'measured'),
                kwargs.get('source'),
                kwargs.get('evidence_file'),
                kwargs.get('data_json'),
                kwargs.get('notes', '')
            ))

            emission_id = cursor.lastrowid
            conn.commit()
            return emission_id

        except Exception as e:
            logging.error(f"Emisyon kaydı kaydetme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_emissions(self, company_id: int, period: str = None,
                     scope: str = None) -> List[Dict]:
        """Emisyon kayıtlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, period, scope, category, subcategory, fuel_type, 
                   quantity, unit, co2e_emissions, data_quality, verified, notes
            FROM carbon_emissions
            WHERE company_id = ?
        """
        params = [company_id]

        if period:
            query += " AND period = ?"
            params.append(period)

        if scope:
            query += " AND scope = ?"
            params.append(scope)

        query += " ORDER BY period DESC, scope, category"

        try:
            cursor.execute(query, params)

            emissions = []
            for row in cursor.fetchall():
                emissions.append({
                    'id': row[0],
                    'period': row[1],
                    'scope': row[2],
                    'category': row[3],
                    'subcategory': row[4],
                    'fuel_type': row[5],
                    'quantity': row[6],
                    'unit': row[7],
                    'co2e_emissions': row[8],
                    'data_quality': row[9],
                    'verified': bool(row[10]),
                    'notes': row[11]
                })

            return emissions

        except Exception as e:
            logging.error(f"Emisyon getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def update_emission_record(self, emission_id: int, **updates) -> bool:
        """Emisyon kaydını güncelle"""
        if not updates:
            return False

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Güncellenebilir alanlar
            allowed_fields = ['quantity', 'unit', 'co2e_emissions', 'data_quality',
                            'source', 'evidence_file', 'notes', 'verified']

            set_clause = []
            values = []

            for field, value in updates.items():
                if field in allowed_fields:
                    set_clause.append(f"{field} = ?")
                    values.append(value)

            if not set_clause:
                return False

            set_clause.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(emission_id)

            query = f"UPDATE carbon_emissions SET {', '.join(set_clause)} WHERE id = ?"
            cursor.execute(query, values)

            conn.commit()
            return cursor.rowcount > 0

        except Exception as e:
            logging.error(f"Emisyon güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_emission_record(self, emission_id: int) -> bool:
        """Emisyon kaydını sil"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM carbon_emissions WHERE id = ?", (emission_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Emisyon silme hatası: {e}")
            return False
        finally:
            conn.close()

    # ==================== HEDEF YÖNETİMİ ====================

    def save_carbon_target(self, company_id: int, target_data: Dict) -> int:
        """
        Karbon hedefi kaydet
        
        Args:
            target_data: {
                'target_name': str,
                'scope_coverage': str,  # scope1, scope1_2, scope1_2_3
                'baseline_year': int,
                'baseline_co2e': float,
                'target_year': int,
                'target_co2e': float,
                'target_reduction_pct': float,
                'sbti_approved': bool,
                ...
            }
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO carbon_targets 
                (company_id, target_name, target_description, scope_coverage,
                 baseline_year, baseline_co2e, target_year, target_co2e,
                 target_reduction_pct, target_type, intensity_metric,
                 commitment_level, sbti_approved, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                target_data['target_name'],
                target_data.get('target_description'),
                target_data['scope_coverage'],
                target_data['baseline_year'],
                target_data['baseline_co2e'],
                target_data['target_year'],
                target_data['target_co2e'],
                target_data.get('target_reduction_pct'),
                target_data.get('target_type', 'absolute'),
                target_data.get('intensity_metric'),
                target_data.get('commitment_level', 'committed'),
                target_data.get('sbti_approved', False),
                target_data.get('status', 'active')
            ))

            target_id = cursor.lastrowid
            conn.commit()
            return target_id

        except Exception as e:
            logging.error(f"Hedef kaydetme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_carbon_targets(self, company_id: int) -> List[Dict]:
        """Şirketin karbon hedeflerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, target_name, target_description, scope_coverage,
                       baseline_year, baseline_co2e, target_year, target_co2e,
                       target_reduction_pct, target_type, sbti_approved, status, progress_pct
                FROM carbon_targets
                WHERE company_id = ?
                ORDER BY target_year DESC
            """, (company_id,))

            targets = []
            for row in cursor.fetchall():
                targets.append({
                    'id': row[0],
                    'target_name': row[1],
                    'target_description': row[2],
                    'scope_coverage': row[3],
                    'baseline_year': row[4],
                    'baseline_co2e': row[5],
                    'target_year': row[6],
                    'target_co2e': row[7],
                    'target_reduction_pct': row[8],
                    'target_type': row[9],
                    'sbti_approved': bool(row[10]),
                    'status': row[11],
                    'progress_pct': row[12]
                })

            return targets

        except Exception as e:
            logging.error(f"Hedef getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def update_target_progress(self, target_id: int, company_id: int) -> bool:
        """Hedef ilerlemesini güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Hedef bilgilerini al
            cursor.execute("""
                SELECT baseline_year, baseline_co2e, target_year, target_co2e, scope_coverage
                FROM carbon_targets
                WHERE id = ?
            """, (target_id,))

            target_row = cursor.fetchone()
            if not target_row:
                return False

            baseline_year, baseline_co2e, target_year, target_co2e, scope_coverage = target_row

            # Mevcut yıl emisyonunu hesapla
            current_year = str(datetime.now().year)
            current_footprint = self.calculator.calculate_total_footprint(
                company_id=company_id,
                period=current_year,
                include_scope3=(scope_coverage == 'scope1_2_3')
            )

            current_co2e = current_footprint['total_co2e']

            # İlerleme hesapla
            progress_result = self.calculator.calculate_target_progress(
                baseline_co2e=baseline_co2e,
                current_co2e=current_co2e,
                target_co2e=target_co2e
            )

            # Progress'i güncelle
            cursor.execute("""
                UPDATE carbon_targets 
                SET progress_pct = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (progress_result['progress_pct'], target_id))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Hedef ilerleme güncelleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    # ==================== AZALTMA GİRİŞİMLERİ ====================

    def save_reduction_initiative(self, company_id: int, initiative_data: Dict) -> int:
        """Emisyon azaltma girişimi kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO carbon_reduction_initiatives 
                (company_id, initiative_name, initiative_description, initiative_type,
                 target_scope, start_date, end_date, investment_amount,
                 expected_reduction_co2e, status, sdg_alignment, responsible_person, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                initiative_data['initiative_name'],
                initiative_data.get('initiative_description'),
                initiative_data.get('initiative_type'),
                initiative_data.get('target_scope'),
                initiative_data.get('start_date'),
                initiative_data.get('end_date'),
                initiative_data.get('investment_amount'),
                initiative_data.get('expected_reduction_co2e'),
                initiative_data.get('status', 'planned'),
                initiative_data.get('sdg_alignment'),
                initiative_data.get('responsible_person'),
                initiative_data.get('notes')
            ))

            initiative_id = cursor.lastrowid
            conn.commit()
            return initiative_id

        except Exception as e:
            logging.error(f"Girişim kaydetme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_reduction_initiatives(self, company_id: int,
                                 status: str = None) -> List[Dict]:
        """Azaltma girişimlerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, initiative_name, initiative_description, initiative_type,
                   target_scope, start_date, end_date, investment_amount,
                   expected_reduction_co2e, actual_reduction_co2e, status,
                   responsible_person
            FROM carbon_reduction_initiatives
            WHERE company_id = ?
        """
        params = [company_id]

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY start_date DESC"

        try:
            cursor.execute(query, params)

            initiatives = []
            for row in cursor.fetchall():
                initiatives.append({
                    'id': row[0],
                    'initiative_name': row[1],
                    'initiative_description': row[2],
                    'initiative_type': row[3],
                    'target_scope': row[4],
                    'start_date': row[5],
                    'end_date': row[6],
                    'investment_amount': row[7],
                    'expected_reduction_co2e': row[8],
                    'actual_reduction_co2e': row[9],
                    'status': row[10],
                    'responsible_person': row[11]
                })

            return initiatives

        except Exception as e:
            logging.error(f"Girişim getirme hatası: {e}")
            return []
        finally:
            conn.close()

    # ==================== RAPORLAMA VE ANALİZ ====================

    def generate_emissions_summary(self, company_id: int, period: str,
                                  include_scope3: bool = False) -> Dict:
        """
        Emisyon özeti raporu oluştur
        
        Returns:
            Scope 1, 2, (3) toplam ve detaylı breakdown
        """
        return self.calculator.calculate_total_footprint(
            company_id=company_id,
            period=period,
            include_scope3=include_scope3
        )

    def get_emissions_trend(self, company_id: int,
                          start_year: int, end_year: int) -> Dict:
        """
        Emisyon trendi analizi (yıllara göre)
        
        Returns:
            {
                'years': [2020, 2021, 2022, 2023, 2024],
                'scope1': [100, 95, 90, 85, 80],
                'scope2': [50, 48, 45, 42, 40],
                'total': [150, 143, 135, 127, 120]
            }
        """
        years = list(range(start_year, end_year + 1))
        scope1_data = []
        scope2_data = []
        scope3_data = []
        total_data = []

        for year in years:
            summary = self.generate_emissions_summary(
                company_id=company_id,
                period=str(year),
                include_scope3=True
            )

            scope1_data.append(summary['scope1_total'])
            scope2_data.append(summary['scope2_total'])
            scope3_data.append(summary.get('scope3_total', 0))
            total_data.append(summary['total_co2e'])

        return {
            'years': years,
            'scope1': scope1_data,
            'scope2': scope2_data,
            'scope3': scope3_data,
            'total': total_data,
            'trend': self._calculate_trend(total_data)
        }

    def _calculate_trend(self, data: List[float]) -> str:
        """Trend hesapla (increasing, decreasing, stable)"""
        if len(data) < 2:
            return 'insufficient_data'

        avg_change = sum(data[i] - data[i-1] for i in range(1, len(data))) / (len(data) - 1)

        if avg_change < -5:
            return 'decreasing'  # Azalıyor
        elif avg_change > 5:
            return 'increasing'  # Artıyor
        else:
            return 'stable'  # Stabil

    def save_carbon_report(self, company_id: int, period: str,
                          footprint_data: Dict) -> int:
        """Karbon raporunu kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO carbon_reports 
                (company_id, report_period, report_type, scope1_total, scope2_total,
                 scope3_total, total_co2e, reporting_standard)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                period,
                'annual',
                footprint_data['scope1_total'],
                footprint_data['scope2_total'],
                footprint_data.get('scope3_total'),
                footprint_data['total_co2e'],
                'GHG Protocol'
            ))

            report_id = cursor.lastrowid
            conn.commit()
            return report_id

        except Exception as e:
            logging.error(f"Rapor kaydetme hatası: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_carbon_reports(self, company_id: int) -> List[Dict]:
        """Karbon raporlarını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, report_period, scope1_total, scope2_total, scope3_total,
                       total_co2e, verification_status, created_at
                FROM carbon_reports
                WHERE company_id = ?
                ORDER BY report_period DESC
            """, (company_id,))

            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'report_period': row[1],
                    'scope1_total': row[2],
                    'scope2_total': row[3],
                    'scope3_total': row[4],
                    'total_co2e': row[5],
                    'verification_status': row[6],
                    'created_at': row[7]
                })

            return reports

        except Exception as e:
            logging.error(f"Rapor getirme hatası: {e}")
            return []
        finally:
            conn.close()

    # ==================== İSTATİSTİKLER VE DASHBOARD ====================

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için istatistikler"""
        current_year = str(datetime.now().year)
        previous_year = str(datetime.now().year - 1)

        # Mevcut yıl
        current = self.generate_emissions_summary(company_id, current_year)

        # Önceki yıl
        try:
            previous = self.generate_emissions_summary(company_id, previous_year)
            year_over_year = self.calculator.calculate_reduction_percentage(
                baseline_co2e=previous['total_co2e'],
                current_co2e=current['total_co2e']
            )
        except Exception:
            previous = None
            year_over_year = 0

        # Hedefler
        targets = self.get_carbon_targets(company_id)
        active_targets = [t for t in targets if t['status'] == 'active']

        # Azaltma girişimleri
        initiatives = self.get_reduction_initiatives(company_id, status='ongoing')

        return {
            'current_year': current_year,
            'current_total_co2e': current['total_co2e'],
            'scope1_total': current['scope1_total'],
            'scope2_total': current['scope2_total'],
            'scope3_total': current.get('scope3_total', 0),
            'previous_year_co2e': previous['total_co2e'] if previous else None,
            'year_over_year_change_pct': year_over_year,
            'active_targets_count': len(active_targets),
            'ongoing_initiatives_count': len(initiatives),
            'reduction_trend': 'decreasing' if year_over_year > 0 else 'increasing'
        }

