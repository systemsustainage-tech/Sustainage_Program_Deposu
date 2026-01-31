#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Karbon Yönetimi Modülü
Scope 1, 2, 3 emisyonlarını yönetir ve karbon ayak izini hesaplar
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List

from utils.language_manager import LanguageManager
from config.database import DB_PATH

try:
    from .emission_factor_data import DEFRA_IPCC_DATA
except ImportError:
    from emission_factor_data import DEFRA_IPCC_DATA


class CarbonManager:
    """Karbon emisyonları ve karbon ayak izi yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.lm = LanguageManager()
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_db_tables()

    def _init_db_tables(self) -> None:
        """Karbon yönetimi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Scope 1 - Direkt emisyonlar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scope1_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    emission_source TEXT NOT NULL,
                    fuel_type TEXT,
                    fuel_consumption REAL,
                    fuel_unit TEXT,
                    emission_factor REAL,
                    total_emissions REAL,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Scope 2 - Enerji kaynaklı emisyonlar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scope2_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    energy_source TEXT NOT NULL,
                    energy_consumption REAL,
                    energy_unit TEXT,
                    grid_emission_factor REAL,
                    total_emissions REAL,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Scope 3 - Diğer dolaylı emisyonlar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scope3_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    activity_data REAL,
                    activity_unit TEXT,
                    emission_factor REAL,
                    total_emissions REAL,
                    invoice_date TEXT,
                    due_date TEXT,
                    supplier TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Emisyon faktörleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emission_factors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    fuel_type TEXT,
                    factor_value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    scope INTEGER,
                    country TEXT,
                    source_reference TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Şema güncellemesi: category kolonu kontrolü
            cursor.execute("PRAGMA table_info(emission_factors)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'category' not in columns:
                try:
                    cursor.execute("ALTER TABLE emission_factors ADD COLUMN category TEXT")
                    logging.info("Added 'category' column to emission_factors table")
                except Exception as e:
                    logging.error(f"Error adding category column: {e}")

            # Karbon hedefleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carbon_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    target_year INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    baseline_year INTEGER,
                    baseline_emissions REAL,
                    target_reduction_percent REAL,
                    target_emissions REAL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # Varsayılan emisyon faktörlerini ekle
            self._add_default_emission_factors(cursor)
            # DEFRA/IPCC Kütüphanesini içe aktar
            self.import_defra_ipcc_factors(cursor)

            conn.commit()
            logging.info(f"[OK] {self.lm.tr('carbon_module_tables_created', 'Karbon modülü tabloları başarıyla oluşturuldu')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('carbon_module_table_error', 'Karbon modülü tablo oluşturma')}: {e}")
            conn.rollback()
        finally:
            conn.close()

    def import_defra_ipcc_factors(self, cursor) -> None:
        """DEFRA/IPCC veri setini veritabanına aktar"""
        try:
            count = 0
            for item in DEFRA_IPCC_DATA:
                # Mükerrer kayıt kontrolü (Source + Fuel Type + Scope)
                cursor.execute("""
                    SELECT id FROM emission_factors 
                    WHERE source = ? AND fuel_type = ? AND scope = ?
                """, (item['source'], item['fuel_type'], item['scope']))
                
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO emission_factors 
                        (source, fuel_type, factor_value, unit, scope, category, source_reference, country)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item['source'], 
                        item['fuel_type'], 
                        item['factor_value'], 
                        item['unit'], 
                        item['scope'], 
                        item.get('category', ''), 
                        item.get('ref', ''),
                        'International'
                    ))
                    count += 1
            
            if count > 0:
                logging.info(f"DEFRA/IPCC kütüphanesinden {count} yeni emisyon faktörü eklendi.")
                
        except Exception as e:
            logging.error(f"DEFRA/IPCC import hatası: {e}")

    def _add_default_emission_factors(self, cursor) -> None:
        """Varsayılan emisyon faktörlerini ekle"""
        factors = [
            # Scope 1 - Yakıtlar
            ('Doğal Gaz', 'Natural Gas', 2.16, 'kg CO2/m3', 1, 'Turkey', 'TUIK'),
            ('Motorin', 'Diesel', 2.68, 'kg CO2/L', 1, 'Turkey', 'TUIK'),
            ('Benzin', 'Gasoline', 2.31, 'kg CO2/L', 1, 'Turkey', 'TUIK'),
            ('LPG', 'LPG', 1.67, 'kg CO2/L', 1, 'Turkey', 'TUIK'),
            ('Kömür', 'Coal', 2.93, 'kg CO2/kg', 1, 'Turkey', 'TUIK'),

            # Scope 2 - Elektrik
            ('Elektrik', 'Electricity', 0.526, 'kg CO2/kWh', 2, 'Turkey', 'TEIAS'),

            # Scope 3 - Ulaşım
            ('Havayolu', 'Air Travel', 0.255, 'kg CO2/km', 3, 'Global', 'ICAO'),
            ('Karayolu', 'Road Transport', 0.12, 'kg CO2/km', 3, 'Turkey', 'TUIK'),
            ('Denizyolu', 'Sea Transport', 0.01, 'kg CO2/km', 3, 'Global', 'IMO'),

            # Scope 3 - Malzeme
            ('Çimento', 'Cement', 0.9, 'kg CO2/kg', 3, 'Turkey', 'TCMA'),
            ('Çelik', 'Steel', 1.8, 'kg CO2/kg', 3, 'Turkey', 'TCMA'),
            ('Plastik', 'Plastic', 2.5, 'kg CO2/kg', 3, 'Global', 'EPA'),
        ]

        for source, fuel_type, factor, unit, scope, country, ref in factors:
            cursor.execute("""
                INSERT OR IGNORE INTO emission_factors 
                (source, fuel_type, factor_value, unit, scope, country, source_reference)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (source, fuel_type, factor, unit, scope, country, ref))

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        return {
            'total_co2e': self.get_total_carbon_footprint(company_id),
            'scope1': self.get_scope_emissions(company_id, 1),
            'scope2': self.get_scope_emissions(company_id, 2),
            'scope3': self.get_scope_emissions(company_id, 3)
        }

    def get_total_carbon_footprint(self, company_id: int, year: int = None) -> float:
        """Toplam karbon ayak izini hesapla (kg CO2e)"""
        s1 = self.get_scope_emissions(company_id, 1, year)
        s2 = self.get_scope_emissions(company_id, 2, year)
        s3 = self.get_scope_emissions(company_id, 3, year)
        return s1 + s2 + s3

    def get_scope_emissions(self, company_id: int, scope: int, year: int = None) -> float:
        """Belirli bir kapsamdaki toplam emisyonu getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        table_map = {1: 'scope1_emissions', 2: 'scope2_emissions', 3: 'scope3_emissions'}
        table = table_map.get(scope)
        
        if not table:
            return 0.0
            
        try:
            query = f"SELECT SUM(total_emissions) FROM {table} WHERE company_id = ?"
            params = [company_id]
            
            if year:
                query += " AND year = ?"
                params.append(year)
                
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            return result[0] if result and result[0] else 0.0
            
        except Exception as e:
            logging.error(f"Error calculating scope {scope} emissions: {e}")
            return 0.0
        finally:
            conn.close()

    def get_recent_records(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Son eklenen karbon verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        records = []

        try:
            # Scope 1
            query1 = """
                SELECT 'Scope 1' as scope, emission_source as category, fuel_consumption as quantity, 
                       fuel_unit as unit, total_emissions as emissions, year as period, 
                       created_at as date
                FROM scope1_emissions 
                WHERE company_id = ?
            """
            
            # Scope 2
            query2 = """
                SELECT 'Scope 2' as scope, energy_source as category, energy_consumption as quantity, 
                       energy_unit as unit, total_emissions as emissions, year as period, 
                       created_at as date
                FROM scope2_emissions 
                WHERE company_id = ?
            """
            
            # Scope 3
            query3 = """
                SELECT 'Scope 3' as scope, category, activity_data as quantity, 
                       activity_unit as unit, total_emissions as emissions, year as period, 
                       created_at as date
                FROM scope3_emissions 
                WHERE company_id = ?
            """
            
            # Union and sort
            full_query = f"""
                SELECT * FROM (
                    {query1}
                    UNION ALL
                    {query2}
                    UNION ALL
                    {query3}
                )
                ORDER BY date DESC LIMIT ?
            """
            
            cursor.execute(full_query, (company_id, company_id, company_id, limit))
            
            for row in cursor.fetchall():
                records.append({
                        'scope': row[0],
                        'category': row[1],
                        'quantity': row[2],
                        'unit': row[3],
                        'emissions': row[4],
                        'period': row[5],
                        'created_at': row[6]
                    })
            
            return records
        except Exception as e:
            logging.error(f"Carbon recent records error: {e}")
            return []
        finally:
            conn.close()

    def add_scope1_emission(self, company_id: int, year: int, emission_source: str,
                           fuel_type: str, fuel_consumption: float, fuel_unit: str,
                           emission_factor: float = None, invoice_date: str = None,
                           due_date: str = None, supplier: str = None) -> bool:
        """Scope 1 emisyonu ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Emisyon faktörü yoksa veritabanından al
            if emission_factor is None:
                cursor.execute("""
                    SELECT factor_value FROM emission_factors 
                    WHERE (fuel_type = ? OR source = ?) AND scope = 1
                """, (fuel_type, fuel_type))
                result = cursor.fetchone()
                if result:
                    emission_factor = result[0]
                else:
                    raise ValueError(f"{self.lm.tr('emission_factor_not_found', 'Emisyon faktörü bulunamadı')}: {fuel_type}")

            total_emissions = fuel_consumption * emission_factor

            cursor.execute("""
                INSERT INTO scope1_emissions 
                (company_id, year, emission_source, fuel_type, fuel_consumption, 
                 fuel_unit, emission_factor, total_emissions, invoice_date, due_date, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, emission_source, fuel_type, fuel_consumption,
                  fuel_unit, emission_factor, total_emissions, invoice_date, due_date, supplier))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('scope1_add_error', 'Scope 1 emisyon ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_scope2_emission(self, company_id: int, year: int, energy_source: str,
                           energy_consumption: float, energy_unit: str,
                           grid_emission_factor: float = None, invoice_date: str = None,
                           due_date: str = None, supplier: str = None) -> bool:
        """Scope 2 emisyonu ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Grid emisyon faktörü yoksa veritabanından al
            if grid_emission_factor is None:
                cursor.execute("""
                    SELECT factor_value FROM emission_factors 
                    WHERE source = 'Elektrik' AND scope = 2
                """)
                result = cursor.fetchone()
                if result:
                    grid_emission_factor = result[0]
                else:
                    grid_emission_factor = 0.526  # Türkiye ortalama

            total_emissions = energy_consumption * grid_emission_factor

            cursor.execute("""
                INSERT INTO scope2_emissions 
                (company_id, year, energy_source, energy_consumption, 
                 energy_unit, grid_emission_factor, total_emissions, invoice_date, due_date, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, energy_source, energy_consumption,
                  energy_unit, grid_emission_factor, total_emissions, invoice_date, due_date, supplier))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('scope2_add_error', 'Scope 2 emisyon ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_scope3_emission(self, company_id: int, year: int, category: str,
                           subcategory: str, activity_data: float, activity_unit: str,
                           emission_factor: float = None, invoice_date: str = None,
                           due_date: str = None, supplier: str = None) -> bool:
        """Scope 3 emisyonu ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Emisyon faktörü yoksa veritabanından al
            if emission_factor is None:
                # TR/EN esnek eşleştirme: source veya fuel_type ile kategori/alt kategori eşleştir
                cursor.execute("""
                    SELECT factor_value, source, fuel_type FROM emission_factors 
                    WHERE scope = 3
                """)
                rows = cursor.fetchall()
                cat = (category or "").strip().lower()
                sub = (subcategory or "").strip().lower()
                matched = None
                for factor_value, src, fuel in rows:
                    src_l = (src or "").strip().lower()
                    fuel_l = (fuel or "").strip().lower()
                    if cat and (cat == src_l or cat == fuel_l):
                        matched = factor_value
                        break
                    if sub and (sub == src_l or sub == fuel_l):
                        matched = factor_value
                        break
                if matched is not None:
                    emission_factor = matched
                else:
                    raise ValueError(f"{self.lm.tr('emission_factor_not_found', 'Emisyon faktörü bulunamadı')}: {category or subcategory}")

            total_emissions = activity_data * emission_factor

            cursor.execute("""
                INSERT INTO scope3_emissions 
                (company_id, year, category, subcategory, activity_data, 
                 activity_unit, emission_factor, total_emissions, invoice_date, due_date, supplier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, year, category, subcategory, activity_data,
                  activity_unit, emission_factor, total_emissions, invoice_date, due_date, supplier))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('scope3_add_error', 'Scope 3 emisyon ekleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        stats = {'total_co2e': 0, 'scope1': 0, 'scope2': 0, 'scope3': 0}

        try:
            # Scope 1
            cursor.execute("SELECT SUM(total_emissions) FROM scope1_emissions WHERE company_id = ?", (company_id,))
            stats['scope1'] = cursor.fetchone()[0] or 0

            # Scope 2
            cursor.execute("SELECT SUM(total_emissions) FROM scope2_emissions WHERE company_id = ?", (company_id,))
            stats['scope2'] = cursor.fetchone()[0] or 0

            # Scope 3
            cursor.execute("SELECT SUM(total_emissions) FROM scope3_emissions WHERE company_id = ?", (company_id,))
            stats['scope3'] = cursor.fetchone()[0] or 0

            stats['total_co2e'] = stats['scope1'] + stats['scope2'] + stats['scope3']
            
            return stats
        except Exception as e:
            logging.error(f"Carbon dashboard stats error: {e}")
            return stats
        finally:
            conn.close()

    def get_recent_records(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Dashboard tablosu için son eklenen kayıtları getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        records: List[Dict] = []

        try:
            query = """
                SELECT 
                    'Scope 1' AS scope,
                    emission_source AS category,
                    fuel_consumption AS quantity,
                    fuel_unit AS unit,
                    total_emissions AS co2e_emissions,
                    CAST(year AS TEXT) AS period,
                    created_at
                FROM scope1_emissions
                WHERE company_id = ?

                UNION ALL

                SELECT 
                    'Scope 2' AS scope,
                    energy_source AS category,
                    energy_consumption AS quantity,
                    energy_unit AS unit,
                    total_emissions AS co2e_emissions,
                    CAST(year AS TEXT) AS period,
                    created_at
                FROM scope2_emissions
                WHERE company_id = ?

                UNION ALL

                SELECT 
                    'Scope 3' AS scope,
                    category AS category,
                    activity_data AS quantity,
                    activity_unit AS unit,
                    total_emissions AS co2e_emissions,
                    CAST(year AS TEXT) AS period,
                    created_at
                FROM scope3_emissions
                WHERE company_id = ?

                ORDER BY created_at DESC
                LIMIT ?
            """

            cursor.execute(query, (company_id, company_id, company_id, limit))

            for row in cursor.fetchall():
                records.append({
                    'scope': row[0],
                    'category': row[1],
                    'quantity': row[2],
                    'unit': row[3],
                    'co2e_emissions': row[4],
                    'period': row[5],
                    'created_at': row[6],
                })

            return records
        except Exception as e:
            logging.error(f"Carbon recent records error: {e}")
            return []
        finally:
            conn.close()

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard istatistiklerini getir"""
        year = datetime.now().year
        footprint = self.get_total_carbon_footprint(company_id, year)
        
        # Map to template expected keys
        return {
            'total_co2e': footprint.get('total_footprint', 0),
            'scope1': footprint.get('scope1_total', 0),
            'scope2': footprint.get('scope2_total', 0),
            'scope3': footprint.get('scope3_total', 0)
        }

    def get_total_carbon_footprint(self, company_id: int, year: int) -> Dict:
        """Toplam karbon ayak izini hesapla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Scope 1 toplam
            cursor.execute("""
                SELECT SUM(total_emissions) FROM scope1_emissions 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))
            scope1_total = cursor.fetchone()[0] or 0

            # Scope 2 toplam
            cursor.execute("""
                SELECT SUM(total_emissions) FROM scope2_emissions 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))
            scope2_total = cursor.fetchone()[0] or 0

            # Scope 3 toplam
            cursor.execute("""
                SELECT SUM(total_emissions) FROM scope3_emissions 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))
            scope3_total = cursor.fetchone()[0] or 0

            total_footprint = scope1_total + scope2_total + scope3_total

            return {
                'scope1_total': scope1_total,
                'scope2_total': scope2_total,
                'scope3_total': scope3_total,
                'total_footprint': total_footprint,
                'year': year,
                'company_id': company_id
            }

        except Exception as e:
            logging.error(f"{self.lm.tr('carbon_footprint_calc_error', 'Karbon ayak izi hesaplama hatası')}: {e}")
            return {}
        finally:
            conn.close()

    def set_carbon_target(self, company_id: int, target_year: int, target_type: str,
                         baseline_year: int, baseline_emissions: float,
                         target_reduction_percent: float) -> bool:
        """Karbon hedefi belirle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            target_emissions = baseline_emissions * (1 - target_reduction_percent / 100)

            cursor.execute("""
                INSERT OR REPLACE INTO carbon_targets 
                (company_id, target_year, target_type, baseline_year, 
                 baseline_emissions, target_reduction_percent, target_emissions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, target_year, target_type, baseline_year,
                  baseline_emissions, target_reduction_percent, target_emissions))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('carbon_target_set_error', 'Karbon hedefi belirleme hatası')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_carbon_targets(self, company_id: int) -> List[Dict]:
        """Karbon hedeflerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT target_year, target_type, baseline_year, baseline_emissions,
                       target_reduction_percent, target_emissions, status
                FROM carbon_targets 
                WHERE company_id = ? AND status = 'active'
                ORDER BY target_year
            """, (company_id,))

            targets = []
            for row in cursor.fetchall():
                targets.append({
                    'target_year': row[0],
                    'target_type': row[1],
                    'baseline_year': row[2],
                    'baseline_emissions': row[3],
                    'target_reduction_percent': row[4],
                    'target_emissions': row[5],
                    'status': row[6]
                })

            return targets

        except Exception as e:
            logging.error(f"{self.lm.tr('carbon_targets_get_error', 'Karbon hedefleri getirme hatası')}: {e}")
            return []
        finally:
            conn.close()

    def get_emission_factors(self, scope: int = None) -> List[Dict]:
        """Emisyon faktörlerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if scope:
                cursor.execute("""
                    SELECT source, fuel_type, factor_value, unit, scope, country, source_reference
                    FROM emission_factors 
                    WHERE scope = ?
                    ORDER BY scope, source
                """, (scope,))
            else:
                cursor.execute("""
                    SELECT source, fuel_type, factor_value, unit, scope, country, source_reference
                    FROM emission_factors 
                    ORDER BY scope, source
                """)

            factors = []
            for row in cursor.fetchall():
                factors.append({
                    'source': row[0],
                    'fuel_type': row[1],
                    'factor_value': row[2],
                    'unit': row[3],
                    'scope': row[4],
                    'country': row[5],
                    'source_reference': row[6]
                })

            return factors

        except Exception as e:
            logging.error(f"{self.lm.tr('emission_factors_get_error', 'Emisyon faktörleri getirme hatası')}: {e}")
            return []
        finally:
            conn.close()

    def get_carbon_records(self, company_id: int, year: int) -> List[Dict]:
        """Tüm scope emisyon kayıtlarını getir (Raporlama için)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        records = []

        try:
            # Scope 1
            cursor.execute("""
                SELECT 'Scope 1' as scope, emission_source, fuel_type, fuel_consumption, fuel_unit, 
                       total_emissions, invoice_date, due_date, supplier, created_at
                FROM scope1_emissions 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))
            for row in cursor.fetchall():
                records.append({
                    'scope': row[0],
                    'source': row[1],
                    'type': row[2],
                    'amount': row[3],
                    'unit': row[4],
                    'total_emissions': row[5],
                    'invoice_date': row[6],
                    'due_date': row[7],
                    'supplier': row[8],
                    'date': row[9]
                })

            # Scope 2
            cursor.execute("""
                SELECT 'Scope 2' as scope, energy_source, 'Elektrik' as type, energy_consumption, energy_unit, 
                       total_emissions, invoice_date, due_date, supplier, created_at
                FROM scope2_emissions 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))
            for row in cursor.fetchall():
                records.append({
                    'scope': row[0],
                    'source': row[1],
                    'type': row[2],
                    'amount': row[3],
                    'unit': row[4],
                    'total_emissions': row[5],
                    'invoice_date': row[6],
                    'due_date': row[7],
                    'supplier': row[8],
                    'date': row[9]
                })

            # Scope 3
            cursor.execute("""
                SELECT 'Scope 3' as scope, category, subcategory, activity_data, activity_unit, 
                       total_emissions, invoice_date, due_date, supplier, created_at
                FROM scope3_emissions 
                WHERE company_id = ? AND year = ?
            """, (company_id, year))
            for row in cursor.fetchall():
                records.append({
                    'scope': row[0],
                    'source': row[1],
                    'type': row[2], # using subcategory as type
                    'amount': row[3],
                    'unit': row[4],
                    'total_emissions': row[5],
                    'invoice_date': row[6],
                    'due_date': row[7],
                    'supplier': row[8],
                    'date': row[9]
                })

            return records

        except Exception as e:
            logging.error(f"Karbon kayıtları getirme hatası: {e}")
            return []
        finally:
            conn.close()
