#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Karbon Yönetimi Modülü
Scope 1, 2, 3 emisyonlarını yönetir ve karbon ayak izini hesaplar
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# BaseTenantManager'ı içe aktar
try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    # Eğer backend modülü olarak çalıştırılmazsa path ayarı gerekebilir
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from backend.core.base_manager import BaseTenantManager

try:
    from utils.language_manager import LanguageManager
    from config.database import DB_PATH
except ImportError:
    from backend.utils.language_manager import LanguageManager
    from backend.config.database import DB_PATH

try:
    from .emission_factor_data import DEFRA_IPCC_DATA
except ImportError:
    # Bağıl import hatası durumunda (test vs)
    try:
        from backend.modules.environmental.emission_factor_data import DEFRA_IPCC_DATA
    except ImportError:
        # Fallback empty list or mock
        DEFRA_IPCC_DATA = []


class CarbonManager(BaseTenantManager):
    """Karbon emisyonları ve karbon ayak izi yönetimi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        self.lm = LanguageManager()
        # db_path çözümü BaseTenantManager'da yapılabilir ama burada da path fix var
        final_db_path = db_path or DB_PATH
        if final_db_path and not os.path.isabs(final_db_path):
             base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
             final_db_path = os.path.join(base_dir, final_db_path)
        
        super().__init__(final_db_path, company_id)
        self._init_db_tables()
        self._migrate_tables()

    def _init_db_tables(self) -> None:
        """Karbon yönetimi tablolarını oluştur"""
        try:
            # Scope 1 - Direkt emisyonlar
            self.db.execute_update("""
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
            self.db.execute_update("""
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
            self.db.execute_update("""
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
            self.db.execute_update("""
                CREATE TABLE IF NOT EXISTS emission_factors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    fuel_type TEXT,
                    factor_value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    scope INTEGER,
                    country TEXT,
                    source_reference TEXT,
                    category TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Karbon hedefleri
            self.db.execute_update("""
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
            self._add_default_emission_factors()
            # DEFRA/IPCC Kütüphanesini içe aktar
            self.import_defra_ipcc_factors()

            logging.info(f"[OK] {self.lm.tr('carbon_module_tables_created', 'Karbon modülü tabloları başarıyla oluşturuldu')}")

        except Exception as e:
            logging.error(f"[{self.lm.tr('error', 'HATA')}] {self.lm.tr('carbon_module_table_error', 'Karbon modülü tablo oluşturma')}: {e}")

    def _migrate_tables(self) -> None:
        """Tablo şemalarını güncelle"""
        try:
            # Check for category column in emission_factors
            # We check if we can select the column
            try:
                self.db.execute_query("SELECT category FROM emission_factors LIMIT 1")
            except Exception:
                logging.info("Adding 'category' column to emission_factors table")
                self.db.execute_update("ALTER TABLE emission_factors ADD COLUMN category TEXT")
                
        except Exception as e:
            # Column might already exist or table issue, log but continue
            logging.debug(f"Migration check/update note: {e}")

    def import_defra_ipcc_factors(self) -> None:
        """DEFRA/IPCC veri setini veritabanına aktar"""
        try:
            count = 0
            if not DEFRA_IPCC_DATA:
                return

            for item in DEFRA_IPCC_DATA:
                # Mükerrer kayıt kontrolü (Source + Fuel Type + Scope)
                existing = self.db.execute_query("""
                    SELECT id FROM emission_factors 
                    WHERE source = ? AND fuel_type = ? AND scope = ?
                """, (item['source'], item['fuel_type'], item['scope']))
                
                if not existing:
                    self.db.execute_update("""
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

    def _add_default_emission_factors(self) -> None:
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
            # Use INSERT OR IGNORE via execute_update
            self.db.execute_update("""
                INSERT OR IGNORE INTO emission_factors 
                (source, fuel_type, factor_value, unit, scope, country, source_reference)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (source, fuel_type, factor, unit, scope, country, ref))

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        cid = self._ensure_context(company_id)
        return {
            'total_co2e': self.get_total_carbon_footprint(cid),
            'scope1': self.get_scope_emissions(cid, 1),
            'scope2': self.get_scope_emissions(cid, 2),
            'scope3': self.get_scope_emissions(cid, 3)
        }

    def get_total_carbon_footprint(self, company_id: int, year: int = None) -> float:
        """Toplam karbon ayak izini hesapla (kg CO2e)"""
        cid = self._ensure_context(company_id)
        s1 = self.get_scope_emissions(cid, 1, year)
        s2 = self.get_scope_emissions(cid, 2, year)
        s3 = self.get_scope_emissions(cid, 3, year)
        return s1 + s2 + s3

    def get_scope_emissions(self, company_id: int, scope: int, year: int = None) -> float:
        """Belirli bir kapsamdaki toplam emisyonu getir"""
        # cid = self._ensure_context(company_id) # BaseTenantManager handles context in select/execute_query
        
        table_map = {1: 'scope1_emissions', 2: 'scope2_emissions', 3: 'scope3_emissions'}
        table = table_map.get(scope)
        
        if not table:
            return 0.0
            
        try:
            # Using BaseTenantManager.select which enforces tenant isolation
            where_clause = None
            params = []
            
            if year:
                where_clause = "year = ?"
                params.append(year)
                
            # We select SUM directly via raw query or select helper?
            # select() returns rows. Let's use execute_query with automatic injection.
            
            query = f"SELECT SUM(total_emissions) as total FROM {table}"
            if year:
                query += " WHERE year = ?"
            
            # Note: execute_query will inject 'WHERE company_id = ?' automatically.
            # If we already have WHERE, it injects '... AND company_id = ?'
            
            result = self.execute_query(query, tuple(params), company_id=company_id)
            return result[0]['total'] if result and result[0]['total'] else 0.0
            
        except Exception as e:
            logging.error(f"Error calculating scope {scope} emissions: {e}")
            return 0.0

    def get_monthly_emission_stats(self, company_id: int, year: int) -> List[float]:
        """Get monthly aggregated emissions for the given year (Scope 1+2+3)"""
        # cid = self._ensure_context(company_id) # Handled by execute_query
        monthly_data = [0.0] * 12
        
        try:
            tables = ['scope1_emissions', 'scope2_emissions', 'scope3_emissions']
            
            for table in tables:
                # Use invoice_date if available, otherwise fallback to created_at
                # Handle empty strings as NULL using NULLIF
                # execute_query will inject company_id filter
                query = f"""
                    SELECT 
                        strftime('%m', COALESCE(NULLIF(invoice_date, ''), NULLIF(created_at, ''), CURRENT_DATE)) as month,
                        SUM(total_emissions) as total
                    FROM {table}
                    WHERE year = ?
                    GROUP BY month
                """
                rows = self.execute_query(query, (year,), company_id=company_id)
                
                for row in rows:
                    month_str = row['month']
                    total = row['total']
                    if month_str:
                        try:
                            m_idx = int(month_str) - 1
                            if 0 <= m_idx < 12:
                                monthly_data[m_idx] += total or 0.0
                        except ValueError:
                            pass
                            
        except Exception as e:
            logging.error(f"Error getting monthly emission stats: {e}")
            
        return monthly_data

    def get_recent_records(self, company_id: int, limit: int = 10) -> List[Dict]:
        """Son eklenen karbon verilerini getir"""
        # cid = self._ensure_context(company_id) # Handled by execute_query
        
        try:
            # Note: Union queries are tricky for auto-injection if not careful.
            # But execute_query injects into EACH SELECT if we rely on regex.
            # However, our regex might be too simple for complex UNION ALL.
            # Safer approach with BaseTenantManager is to execute separate queries or rely on injection if robust.
            # Our injection regex handles 'FROM table' but might get confused with multiple FROMs in one string.
            # Let's verify: inject_tenant_filter regex finds "FROM table". It replaces ONE occurrence or ALL?
            # It finds the first match usually in simple implementation.
            
            # Since UNION queries are complex, let's use the explicit 'company_id = ?' 
            # and pass skip_tenant_filter=True to avoid double injection messing things up,
            # OR refactor to use separate calls.
            
            # Refactoring to separate calls is safer and cleaner for TenantAwareness.
            
            cid = self._ensure_context(company_id)

            # Scope 1
            query1 = """
                SELECT 'Scope 1' as scope, emission_source as category, fuel_consumption as quantity, 
                       fuel_unit as unit, total_emissions as emissions, year as period, 
                       created_at as date
                FROM scope1_emissions 
                ORDER BY created_at DESC LIMIT ?
            """
            rows1 = self.execute_query(query1, (limit,), company_id=cid)
            
            # Scope 2
            query2 = """
                SELECT 'Scope 2' as scope, energy_source as category, energy_consumption as quantity, 
                       energy_unit as unit, total_emissions as emissions, year as period, 
                       created_at as date
                FROM scope2_emissions 
                ORDER BY created_at DESC LIMIT ?
            """
            rows2 = self.execute_query(query2, (limit,), company_id=cid)
            
            # Scope 3
            query3 = """
                SELECT 'Scope 3' as scope, category, activity_data as quantity, 
                       activity_unit as unit, total_emissions as emissions, year as period, 
                       created_at as date
                FROM scope3_emissions 
                ORDER BY created_at DESC LIMIT ?
            """
            rows3 = self.execute_query(query3, (limit,), company_id=cid)
            
            # Combine and Sort in Python
            all_rows = rows1 + rows2 + rows3
            
            # Sort by date descending
            all_rows.sort(key=lambda x: x['date'], reverse=True)
            
            # Take top N
            final_rows = all_rows[:limit]
            
            records = []
            for row in final_rows:
                records.append({
                        'scope': row['scope'],
                        'category': row['category'],
                        'quantity': row['quantity'],
                        'unit': row['unit'],
                        'emissions': row['emissions'],
                        'period': row['period'],
                        'created_at': row['date']
                    })
            
            return records
        except Exception as e:
            logging.error(f"Carbon recent records error: {e}")
            return []

    def add_scope1_emission(self, company_id: int, year: int, emission_source: str,
                           fuel_type: str, fuel_consumption: float, fuel_unit: str,
                           emission_factor: float = None, invoice_date: str = None,
                           due_date: str = None, supplier: str = None) -> bool:
        """Scope 1 emisyonu ekle"""
        cid = self._ensure_context(company_id)

        try:
            # Emisyon faktörü yoksa veritabanından al
            if emission_factor is None:
                result = self.execute_query("""
                    SELECT factor_value FROM emission_factors 
                    WHERE (fuel_type = ? OR source = ?) AND scope = 1
                """, (fuel_type, fuel_type))
                
                if result:
                    emission_factor = result[0]['factor_value']
                else:
                    raise ValueError(f"{self.lm.tr('emission_factor_not_found', 'Emisyon faktörü bulunamadı')}: {fuel_type}")

            total_emissions = fuel_consumption * emission_factor

            self.insert('scope1_emissions', {
                'company_id': cid,
                'year': year,
                'emission_source': emission_source,
                'fuel_type': fuel_type,
                'fuel_consumption': fuel_consumption,
                'fuel_unit': fuel_unit,
                'emission_factor': emission_factor,
                'total_emissions': total_emissions,
                'invoice_date': invoice_date,
                'due_date': due_date,
                'supplier': supplier
            })

            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('scope1_add_error', 'Scope 1 emisyon ekleme hatası')}: {e}")
            return False

    def add_scope2_emission(self, company_id: int, year: int, energy_source: str,
                           energy_consumption: float, energy_unit: str,
                           grid_emission_factor: float = None, invoice_date: str = None,
                           due_date: str = None, supplier: str = None) -> bool:
        """Scope 2 emisyonu ekle"""
        cid = self._ensure_context(company_id)

        try:
            # Grid emisyon faktörü yoksa veritabanından al
            if grid_emission_factor is None:
                result = self.execute_query("""
                    SELECT factor_value FROM emission_factors 
                    WHERE source = 'Elektrik' AND scope = 2
                """)
                if result:
                    grid_emission_factor = result[0]['factor_value']
                else:
                    grid_emission_factor = 0.526  # Türkiye ortalama

            total_emissions = energy_consumption * grid_emission_factor

            self.insert('scope2_emissions', {
                'company_id': cid,
                'year': year,
                'energy_source': energy_source,
                'energy_consumption': energy_consumption,
                'energy_unit': energy_unit,
                'grid_emission_factor': grid_emission_factor,
                'total_emissions': total_emissions,
                'invoice_date': invoice_date,
                'due_date': due_date,
                'supplier': supplier
            })

            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('scope2_add_error', 'Scope 2 emisyon ekleme hatası')}: {e}")
            return False

    def add_scope3_emission(self, company_id: int, year: int, category: str,
                           subcategory: str, activity_data: float, activity_unit: str,
                           emission_factor: float = None, invoice_date: str = None,
                           due_date: str = None, supplier: str = None) -> bool:
        """Scope 3 emisyonu ekle"""
        cid = self._ensure_context(company_id)

        try:
            # Emisyon faktörü yoksa veritabanından al
            if emission_factor is None:
                # TR/EN esnek eşleştirme: source veya fuel_type ile kategori/alt kategori eşleştir
                rows = self.execute_query("""
                    SELECT factor_value, source, fuel_type FROM emission_factors 
                    WHERE scope = 3
                """)
                
                cat = (category or "").strip().lower()
                sub = (subcategory or "").strip().lower()
                matched = None
                
                for row in rows:
                    factor_value = row['factor_value']
                    src = row['source']
                    fuel = row['fuel_type']
                    
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

            self.insert('scope3_emissions', {
                'company_id': cid,
                'year': year,
                'category': category,
                'subcategory': subcategory,
                'activity_data': activity_data,
                'activity_unit': activity_unit,
                'emission_factor': emission_factor,
                'total_emissions': total_emissions,
                'invoice_date': invoice_date,
                'due_date': due_date,
                'supplier': supplier
            })

            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('scope3_add_error', 'Scope 3 emisyon ekleme hatası')}: {e}")
            return False

    def set_carbon_target(self, company_id: int, target_year: int, target_type: str,
                         baseline_year: int, baseline_emissions: float,
                         target_reduction_percent: float) -> bool:
        """Karbon hedefi belirle"""
        cid = self._ensure_context(company_id)

        try:
            target_emissions = baseline_emissions * (1 - target_reduction_percent / 100)

            # REPLACE INTO behavior can be simulated or we assume insert works with primary key checks?
            # Actually sqlite supports INSERT OR REPLACE. BaseTenantManager usually wraps execution.
            # We'll use execute_update for raw query.
            self.execute_update("""
                INSERT OR REPLACE INTO carbon_targets 
                (company_id, target_year, target_type, baseline_year, 
                 baseline_emissions, target_reduction_percent, target_emissions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cid, target_year, target_type, baseline_year,
                  baseline_emissions, target_reduction_percent, target_emissions))

            return True

        except Exception as e:
            logging.error(f"{self.lm.tr('carbon_target_set_error', 'Karbon hedefi belirleme hatası')}: {e}")
            return False

    def get_carbon_targets(self, company_id: int) -> List[Dict]:
        """Karbon hedeflerini getir"""
        cid = self._ensure_context(company_id)

        try:
            rows = self.execute_query("""
                SELECT target_year, target_type, baseline_year, baseline_emissions,
                       target_reduction_percent, target_emissions, status
                FROM carbon_targets 
                WHERE company_id = ? AND status = 'active'
                ORDER BY target_year
            """, (cid,))

            targets = []
            for row in rows:
                targets.append({
                    'target_year': row['target_year'],
                    'target_type': row['target_type'],
                    'baseline_year': row['baseline_year'],
                    'baseline_emissions': row['baseline_emissions'],
                    'target_reduction_percent': row['target_reduction_percent'],
                    'target_emissions': row['target_emissions'],
                    'status': row['status']
                })

            return targets

        except Exception as e:
            logging.error(f"{self.lm.tr('carbon_targets_get_error', 'Karbon hedefleri getirme hatası')}: {e}")
            return []

    def get_emission_factors(self, scope: int = None) -> List[Dict]:
        """Emisyon faktörlerini getir"""
        try:
            if scope:
                rows = self.execute_query("""
                    SELECT source, fuel_type, factor_value, unit, scope, country, source_reference
                    FROM emission_factors 
                    WHERE scope = ?
                    ORDER BY scope, source
                """, (scope,))
            else:
                rows = self.execute_query("""
                    SELECT source, fuel_type, factor_value, unit, scope, country, source_reference
                    FROM emission_factors 
                    ORDER BY scope, source
                """)

            factors = []
            for row in rows:
                factors.append({
                    'source': row['source'],
                    'fuel_type': row['fuel_type'],
                    'factor_value': row['factor_value'],
                    'unit': row['unit'],
                    'scope': row['scope'],
                    'country': row['country'],
                    'source_reference': row['source_reference']
                })

            return factors

        except Exception as e:
            logging.error(f"{self.lm.tr('emission_factors_get_error', 'Emisyon faktörleri getirme hatası')}: {e}")
            return []

    def get_carbon_records(self, company_id: int, year: int) -> List[Dict]:
        """Tüm scope emisyon kayıtlarını getir (Raporlama için)"""
        cid = self._ensure_context(company_id)
        records = []

        try:
            # Scope 1
            rows1 = self.execute_query("""
                SELECT 'Scope 1' as scope, emission_source, fuel_type, fuel_consumption, fuel_unit, 
                       total_emissions, invoice_date, due_date, supplier, created_at
                FROM scope1_emissions 
                WHERE company_id = ? AND year = ?
            """, (cid, year))
            
            for row in rows1:
                records.append({
                    'scope': row['scope'],
                    'source': row['emission_source'],
                    'type': row['fuel_type'],
                    'amount': row['fuel_consumption'],
                    'unit': row['fuel_unit'],
                    'total_emissions': row['total_emissions'],
                    'invoice_date': row['invoice_date'],
                    'due_date': row['due_date'],
                    'supplier': row['supplier'],
                    'date': row['created_at']
                })

            # Scope 2
            rows2 = self.execute_query("""
                SELECT 'Scope 2' as scope, energy_source, 'Elektrik' as type, energy_consumption, energy_unit, 
                       total_emissions, invoice_date, due_date, supplier, created_at
                FROM scope2_emissions 
                WHERE company_id = ? AND year = ?
            """, (cid, year))
            
            for row in rows2:
                records.append({
                    'scope': row['scope'],
                    'source': row['energy_source'],
                    'type': row['type'],
                    'amount': row['energy_consumption'],
                    'unit': row['energy_unit'],
                    'total_emissions': row['total_emissions'],
                    'invoice_date': row['invoice_date'],
                    'due_date': row['due_date'],
                    'supplier': row['supplier'],
                    'date': row['created_at']
                })

            # Scope 3
            rows3 = self.execute_query("""
                SELECT 'Scope 3' as scope, category, subcategory, activity_data, activity_unit, 
                       total_emissions, invoice_date, due_date, supplier, created_at
                FROM scope3_emissions 
                WHERE company_id = ? AND year = ?
            """, (cid, year))
            
            for row in rows3:
                records.append({
                    'scope': row['scope'],
                    'source': row['category'],
                    'type': row['subcategory'], # using subcategory as type
                    'amount': row['activity_data'],
                    'unit': row['activity_unit'],
                    'total_emissions': row['total_emissions'],
                    'invoice_date': row['invoice_date'],
                    'due_date': row['due_date'],
                    'supplier': row['supplier'],
                    'date': row['created_at']
                })

            return records

        except Exception as e:
            logging.error(f"Karbon kayıtları getirme hatası: {e}")
            return []
