#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBAM (Carbon Border Adjustment Mechanism) Manager
AB Sınırda Karbon Düzenleme Mekanizması
"""

import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
try:
    from backend.config.database import DB_PATH
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    # Add project root to path if needed
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    if base_dir not in sys.path:
        sys.path.append(base_dir)
        
    try:
        from backend.config.database import DB_PATH
        from backend.core.base_manager import BaseTenantManager
    except ImportError:
        try:
            from config.database import DB_PATH
            from core.base_manager import BaseTenantManager
        except ImportError:
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
            from config.database import DB_PATH
            from core.base_manager import BaseTenantManager

class CBAMManager(BaseTenantManager):
    """CBAM yöneticisi"""

    def __init__(self, db_path: str = None, company_id: Optional[int] = None) -> None:
        final_db_path = db_path or DB_PATH
        if final_db_path and not os.path.isabs(final_db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            final_db_path = os.path.join(base_dir, final_db_path)
            
        super().__init__(final_db_path, company_id)
        
        self._ensure_schema()

        # CBAM kapsamındaki sektörler
        self.covered_sectors = {
            'cement': 'Çimento',
            'electricity': 'Elektrik',
            'fertilizers': 'Gübre',
            'iron_steel': 'Demir ve Çelik',
            'aluminium': 'Alüminyum',
            'hydrogen': 'Hidrojen'
        }

        # Emisyon türleri
        self.emission_types = {
            'direct': 'Doğrudan Emisyonlar (Scope 1)',
            'indirect': 'Dolaylı Emisyonlar (Scope 2)',
            'embedded': 'Gömülü Emisyonlar'
        }

        self.de_minimis_sectors = {'cement', 'iron_steel', 'aluminium', 'fertilizers'}
        self.de_minimis_excluded_sectors = {'electricity', 'hydrogen'}

    def _ensure_schema(self) -> None:
        """Veritabanı şemasını oluştur"""
        try:
            # CBAM ürünleri tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS cbam_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    product_code VARCHAR(50) NOT NULL,
                    product_name VARCHAR(255) NOT NULL,
                    hs_code VARCHAR(20),
                    cn_code VARCHAR(20),
                    sector VARCHAR(50),
                    production_route VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            # CBAM emisyon verileri tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS cbam_emissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    reporting_period VARCHAR(20),
                    emission_type VARCHAR(50),
                    direct_emissions DECIMAL(15,4),
                    indirect_emissions DECIMAL(15,4),
                    embedded_emissions DECIMAL(15,4),
                    total_emissions DECIMAL(15,4),
                    emission_factor DECIMAL(10,6),
                    calculation_method VARCHAR(100),
                    data_quality VARCHAR(50),
                    verification_status VARCHAR(50),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES cbam_products(id)
                )
            """)

            # CBAM ithalat verileri tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS cbam_imports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    import_period VARCHAR(20),
                    origin_country VARCHAR(100),
                    quantity DECIMAL(15,4),
                    quantity_unit VARCHAR(20),
                    customs_value DECIMAL(15,2),
                    currency VARCHAR(10),
                    embedded_emissions DECIMAL(15,4),
                    carbon_price_paid DECIMAL(15,2),
                    cbam_certificate_required BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (product_id) REFERENCES cbam_products(id)
                )
            """)

            # CBAM raporları tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS cbam_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    report_period VARCHAR(20),
                    report_type VARCHAR(50),
                    total_imports DECIMAL(15,4),
                    total_emissions DECIMAL(15,4),
                    total_cbam_liability DECIMAL(15,2),
                    report_status VARCHAR(50),
                    submitted_at TIMESTAMP,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)
            
            # CBAM factors (Global)
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS cbam_factors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    period INTEGER NOT NULL,
                    eu_ets_price_eur_per_tco2 REAL NOT NULL,
                    default_leakage_factor REAL DEFAULT 0.6,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(period)
                )
            """)

            logging.info("[OK] CBAM tabloları oluşturuldu")

        except Exception as e:
            logging.error(f"[HATA] CBAM şema oluşturma hatası: {e}")

    def get_carbon_price(self, date: str = None) -> float:
        """
        Güncel karbon fiyatını getir (API simülasyonu)
        Gerçek API entegrasyonu yapılana kadar EU ETS varsayılan değerlerini kullanır.
        """
        try:
            # TODO: Gerçek API entegrasyonu (ör. Ember, ICE, EEX)
            return self._get_eu_ets_price(date)
        except Exception as e:
            logging.error(f"Carbon price fetch error: {e}")
            return 85.0  # Güvenli varsayılan (2025 tahmini)

    def _get_eu_ets_price(self, period: str = None) -> float:
        try:
            check = self.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='cbam_factors'")
            if not check:
                return 80.0

            year_value = None
            if period:
                try:
                    year_value = int(str(period)[:4])
                except Exception:
                    year_value = None

            if year_value is not None:
                row = self.execute_query(
                    "SELECT eu_ets_price_eur_per_tco2 FROM cbam_factors WHERE period = ? ORDER BY period DESC LIMIT 1",
                    (year_value,)
                )
                if row and row[0]['eu_ets_price_eur_per_tco2'] is not None:
                    return float(row[0]['eu_ets_price_eur_per_tco2'])

            row = self.execute_query(
                "SELECT eu_ets_price_eur_per_tco2 FROM cbam_factors ORDER BY period DESC LIMIT 1"
            )
            if row and row[0]['eu_ets_price_eur_per_tco2'] is not None:
                return float(row[0]['eu_ets_price_eur_per_tco2'])

            return 80.0
        except Exception as e:
            logging.error(f"EU ETS price fetch error: {e}")
            return 80.0

    def calculate_cbam_metrics(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikler"""
        cid = self._ensure_context(company_id)
        stats = {
            'total_emissions': 0,
            'total_imports': 0,
            'liability': 0,
            'imports': []
        }
        try:
            # Get imports
            rows = self.execute_query("""
                SELECT i.*, p.product_name, p.sector 
                FROM cbam_imports i
                LEFT JOIN cbam_products p ON i.product_id = p.id
                WHERE i.company_id = ?
                ORDER BY i.created_at DESC
            """, (cid,))
            
            imports = [dict(row) for row in rows]
            stats['imports'] = imports
            total_quantity = sum((i.get('quantity') or 0) for i in imports)
            stats['total_imports'] = total_quantity
            stats['total_emissions'] = sum((i.get('embedded_emissions') or 0) for i in imports)

            eu_ets_price = self._get_eu_ets_price()
            covered_quantity = sum(
                (i.get('quantity') or 0)
                for i in imports
                if i.get('sector') in self.de_minimis_sectors
            )
            has_excluded = any(
                i.get('sector') in self.de_minimis_excluded_sectors for i in imports
            )

            total_price = stats['total_emissions'] * eu_ets_price
            paid_price = sum((i.get('carbon_price_paid') or 0) for i in imports)
            raw_liability = max(0, total_price - paid_price)

            de_minimis_threshold = 50.0
            below_de_minimis = (covered_quantity < de_minimis_threshold) and not has_excluded

            stats['eu_ets_price'] = eu_ets_price
            stats['total_quantity'] = total_quantity
            stats['covered_quantity'] = covered_quantity
            stats['de_minimis_threshold'] = de_minimis_threshold
            stats['below_de_minimis'] = below_de_minimis
            stats['liability_raw'] = raw_liability
            stats['liability'] = 0 if below_de_minimis else raw_liability
            
            return stats
        except Exception as e:
            logging.error(f"CBAM stats error: {e}")
            return stats

    def get_dashboard_stats(self, company_id: int) -> Dict:
        """Dashboard için özet istatistikleri getir"""
        return self.calculate_cbam_metrics(company_id)

    def get_recent_records(self, company_id: int, limit: int = 5) -> List[Dict]:
        """Dashboard için son kayıtlar"""
        cid = self._ensure_context(company_id)
        try:
            rows = self.execute_query("""
                SELECT i.import_period, p.product_name, i.quantity, i.embedded_emissions, i.created_at, p.sector, i.origin_country, p.cn_code
                FROM cbam_imports i
                LEFT JOIN cbam_products p ON i.product_id = p.id
                WHERE i.company_id = ?
                ORDER BY i.created_at DESC
                LIMIT ?
            """, (cid, limit))
            
            records = []
            for row in rows:
                records.append({
                    'period': row['import_period'],
                    'product': row['product_name'],
                    'quantity': row['quantity'],
                    'emissions': row['embedded_emissions'],
                    'date': row['created_at'],
                    'sector': row['sector'],
                    'origin_country': row['origin_country'],
                    'cn_code': row['cn_code']
                })
            return records
        except Exception as e:
            logging.error(f"CBAM recent records error: {e}")
            return []

    def add_product(
        self,
        company_id: int,
        product_code: str = None,
        product_name: str = None,
        *,
        sector: str = None,
        hs_code: str = None,
        cn_code: str = None,
        production_route: str = None,
        product_data: Dict = None,
    ) -> bool:
        """CBAM ürünü ekle"""
        cid = self._ensure_context(company_id)

        # Girdi normalizasyonu
        if product_data is None:
            product_data = {
                'product_code': product_code,
                'product_name': product_name,
                'hs_code': hs_code,
                'cn_code': cn_code,
                'sector': sector,
                'production_route': production_route,
            }

        try:
            # Basit doğrulamalar
            code = (product_data.get('product_code') or '').strip()
            name = (product_data.get('product_name') or '').strip()
            if not code or not name:
                logging.error("[HATA] Ürün kodu ve adı zorunludur")
                return False

            self.execute_update(
                """
                INSERT INTO cbam_products 
                (company_id, product_code, product_name, hs_code, cn_code, 
                 sector, production_route)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cid,
                    code,
                    name,
                    product_data.get('hs_code'),
                    product_data.get('cn_code'),
                    product_data.get('sector'),
                    product_data.get('production_route'),
                ),
            )

            logging.info(f"[OK] CBAM ürünü eklendi: {code}")
            return True

        except Exception as e:
            logging.error(f"[HATA] CBAM ürünü ekleme hatası: {e}")
            return False

    def get_product_by_code(self, company_id: int, product_code: str) -> Dict | None:
        """Ürün kodu ile ürün getir"""
        cid = self._ensure_context(company_id)
        try:
            rows = self.execute_query("SELECT * FROM cbam_products WHERE company_id = ? AND product_code = ?", (cid, product_code))
            if rows:
                return rows[0]
            return None
        except Exception as e:
            logging.error(f"CBAM get product error: {e}")
            return None

    def add_import(self, company_id: int, product_id: int, origin_country: str, quantity: float, 
                   embedded_emissions: float, carbon_price_paid: float, import_period: str = None) -> bool:
        """İthalat verisi ekle"""
        cid = self._ensure_context(company_id)
        try:
            self.execute_update("""
                INSERT INTO cbam_imports 
                (company_id, product_id, origin_country, quantity, embedded_emissions, carbon_price_paid, import_period) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cid, product_id, origin_country, quantity, embedded_emissions, carbon_price_paid, import_period))
            return True
        except Exception as e:
            logging.error(f"CBAM import add error: {e}")
            return False

    def record_emissions(self, product_id: int, emission_data: Dict) -> bool:
        """Emisyon verisi kaydet"""
        try:
            # Toplam emisyon hesapla
            direct = emission_data.get('direct_emissions', 0) or 0
            indirect = emission_data.get('indirect_emissions', 0) or 0
            embedded = emission_data.get('embedded_emissions', 0) or 0
            total = direct + indirect + embedded

            self.execute_update("""
                INSERT INTO cbam_emissions 
                (product_id, reporting_period, emission_type, direct_emissions,
                 indirect_emissions, embedded_emissions, total_emissions,
                 emission_factor, calculation_method, data_quality, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                emission_data.get('reporting_period'),
                emission_data.get('emission_type'),
                direct,
                indirect,
                embedded,
                total,
                emission_data.get('emission_factor'),
                emission_data.get('calculation_method'),
                emission_data.get('data_quality', 'estimated'),
                emission_data.get('notes')
            ))

            logging.info("[OK] Emisyon verisi kaydedildi")
            return True

        except Exception as e:
            logging.error(f"[HATA] Emisyon kaydı hatası: {e}")
            return False

    def calculate_cbam_liability(self, company_id: int, period: str) -> Dict:
        """CBAM yükümlülüğünü hesapla"""
        cid = self._ensure_context(company_id)

        try:
            # İthalat ve emisyon verilerini al
            rows = self.execute_query("""
                SELECT 
                    i.product_id,
                    p.product_name,
                    p.sector,
                    SUM(i.quantity) as total_quantity,
                    SUM(i.embedded_emissions) as total_emissions,
                    SUM(i.carbon_price_paid) as carbon_price_paid
                FROM cbam_imports i
                JOIN cbam_products p ON i.product_id = p.id
                WHERE i.company_id = ? AND i.import_period = ?
                GROUP BY i.product_id, p.product_name, p.sector
            """, (cid, period))

            imports = []
            total_emissions = 0
            total_carbon_price_paid = 0
            covered_quantity = 0
            has_excluded = False

            for row in rows:
                product_id = row['product_id']
                product_name = row['product_name']
                sector = row['sector']
                quantity = row['total_quantity']
                emissions = row['total_emissions']
                price_paid = row['carbon_price_paid']

                imports.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'sector': sector,
                    'quantity': quantity or 0,
                    'emissions': emissions or 0,
                    'carbon_price_paid': price_paid or 0
                })

                total_emissions += emissions or 0
                total_carbon_price_paid += price_paid or 0
                if sector in self.de_minimis_sectors:
                    covered_quantity += quantity or 0
                if sector in self.de_minimis_excluded_sectors:
                    has_excluded = True

            eu_ets_price = self._get_eu_ets_price(period)

            # Eğer ithalat verilerinden toplam emisyon sıfırsa, emisyon kayıtlarını fallback olarak kullan
            if total_emissions == 0:
                try:
                    row = self.execute_query("""
                        SELECT SUM(e.total_emissions) as total
                        FROM cbam_emissions e
                        JOIN cbam_products p ON e.product_id = p.id
                        WHERE p.company_id = ? AND e.reporting_period = ?
                    """, (cid, period))
                    total_emissions = (row[0]['total'] or 0) if row else 0
                except Exception as _:
                    total_emissions = 0

            cbam_liability_raw = (total_emissions * eu_ets_price) - total_carbon_price_paid

            de_minimis_threshold = 50.0
            below_de_minimis = (covered_quantity < de_minimis_threshold) and not has_excluded
            cbam_liability = 0 if below_de_minimis else cbam_liability_raw

            return {
                'period': period,
                'total_imports': len(imports),
                'total_quantity': sum(imp['quantity'] for imp in imports),
                'total_emissions': total_emissions,
                'eu_ets_price': eu_ets_price,
                'carbon_price_paid': total_carbon_price_paid,
                'cbam_liability': max(0, cbam_liability),
                'cbam_liability_raw': max(0, cbam_liability_raw),
                'covered_quantity': covered_quantity,
                'de_minimis_threshold': de_minimis_threshold,
                'below_de_minimis': below_de_minimis,
                'imports': imports
            }

        except Exception as e:
            logging.error(f"[HATA] CBAM yükümlülük hesaplama hatası: {e}")
            return {}

    def get_products(self, company_id: int) -> List[Dict]:
        """CBAM ürünlerini getir"""
        cid = self._ensure_context(company_id)

        try:
            rows = self.execute_query("""
                SELECT id, product_code, product_name, hs_code, cn_code, 
                       sector, production_route
                FROM cbam_products
                WHERE company_id = ?
                ORDER BY sector, product_name
            """, (cid,))

            return rows

        except Exception as e:
            logging.error(f"[HATA] CBAM ürünleri getirme hatası: {e}")
            return []

    def add_emission_data(self, emission_data: Dict) -> bool:
        """Emisyon verisi ekle"""
        # Note: This method might need verification of ownership if not done by caller.
        # However, it links to product_id, which should belong to the company.
        # We assume product_id is valid and belongs to the right company context if validated elsewhere.
        return self.record_emissions(emission_data.get('product_id'), emission_data)

    def get_emissions(self, company_id: int, period: str = None) -> List[Dict]:
        """Emisyon verilerini al"""
        cid = self._ensure_context(company_id)
        
        query = """
            SELECT e.*, p.product_name, p.product_code
            FROM cbam_emissions e
            LEFT JOIN cbam_products p ON e.product_id = p.id
            WHERE p.company_id = ?
        """
        params = [cid]

        if period:
            query += " AND e.reporting_period = ?"
            params.append(period)

        query += " ORDER BY e.created_at DESC"

        try:
            rows = self.execute_query(query, tuple(params))
            return rows
        except Exception as e:
            logging.error(f"CBAM get emissions error: {e}")
            return []

    def get_imports(self, company_id: int, period: str = None) -> List[Dict]:
        """İthalat verilerini al"""
        cid = self._ensure_context(company_id)
        
        query = """
            SELECT i.*, p.product_name, p.product_code
            FROM cbam_imports i
            LEFT JOIN cbam_products p ON i.product_id = p.id
            WHERE i.company_id = ?
        """
        params = [cid]

        if period:
            query += " AND i.import_period = ?"
            params.append(period)

        query += " ORDER BY i.created_at DESC"

        try:
            rows = self.execute_query(query, tuple(params))
            return rows
        except Exception as e:
            logging.error(f"CBAM get imports error: {e}")
            return []

    def save_ets_factor(self, period: int, price: float) -> bool:
        try:
            self.execute_update(
                """
                INSERT OR REPLACE INTO cbam_factors
                (period, eu_ets_price_eur_per_tco2, default_leakage_factor, notes)
                VALUES (?, ?, 0.6, NULL)
                """,
                (period, price),
            )
            return True
        except Exception as e:
            logging.error(f"CBAM ETS factor save error: {e}")
            return False

    def get_ets_factors(self, limit: int = 5) -> List[Dict]:
        try:
            check = self.execute_query("SELECT name FROM sqlite_master WHERE type='table' AND name='cbam_factors'")
            if not check:
                return []
            
            rows = self.execute_query(
                """
                SELECT period, eu_ets_price_eur_per_tco2, default_leakage_factor
                FROM cbam_factors
                ORDER BY period DESC
                LIMIT ?
                """,
                (limit,),
            )
            return rows
        except Exception as e:
            logging.error(f"CBAM ETS factor list error: {e}")
            return []

    def generate_quarterly_report(self, company_id: int, period: str) -> bool:
        """Quarterly CBAM raporu oluştur"""
        try:
            # Rapor verilerini topla
            products = self.get_products(company_id)
            emissions = self.get_emissions(company_id, period)
            imports = self.get_imports(company_id, period)

            # Rapor oluştur (şimdilik sadece log)
            logging.info(f"CBAM Quarterly Report for {period}:")
            logging.info(f"- Products: {len(products)}")
            logging.info(f"- Emissions: {len(emissions)}")
            logging.info(f"- Imports: {len(imports)}")

            return True

        except Exception as e:
            logging.error(f"Quarterly rapor oluşturma hatası: {e}")
            return False

    def generate_excel_report(self, company_id: int, period: str) -> bool:
        """Excel raporu oluştur"""
        try:
            # Excel raporu oluşturma mantığı buraya eklenecek
            logging.info(f"Excel raporu oluşturuluyor: {period}")
            return True

        except Exception as e:
            logging.error(f"Excel rapor oluşturma hatası: {e}")
            return False
