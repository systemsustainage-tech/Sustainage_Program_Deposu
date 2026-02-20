#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBAM (Carbon Border Adjustment Mechanism) Manager
AB Sınırda Karbon Düzenleme Mekanizması
"""

import logging
import sqlite3
import sys
from datetime import datetime
from typing import Dict, List
from config.database import DB_PATH


class CBAMManager:
    """CBAM yöneticisi"""

    def __init__(self, db_path: str | None = None) -> None:
        try:
            if db_path:
                self.db_path = db_path
            else:
                # Merkezi ayarlardan veritabanı yolunu kullan
                from config.settings import ensure_directories, get_db_path
                ensure_directories()
                self.db_path = get_db_path()
        except Exception:
            # Geriye dönük uyumluluk: varsayılan yol
            import os
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            self.db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')

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

    def _ensure_schema(self) -> None:
        """Veritabanı şemasını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # CBAM ürünleri tablosu
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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
            cursor.execute("""
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

            conn.commit()
            logging.info("[OK] CBAM tabloları oluşturuldu")

        except Exception as e:
            logging.error(f"[HATA] CBAM şema oluşturma hatası: {e}")
            conn.rollback()
        finally:
            conn.close()

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def add_product(
        self,
        company_id: int,
        product_code: str | None = None,
        product_name: str | None = None,
        *,
        sector: str | None = None,
        hs_code: str | None = None,
        cn_code: str | None = None,
        production_route: str | None = None,
        product_data: Dict | None = None,
    ) -> bool:
        """CBAM ürünü ekle (geriye dönük uyumlu)

        Eski çağrım:
            add_product(company_id, product_data={...})
        Yeni/kolay çağrım:
            add_product(company_id, code, name, sector='cement')
        """
        conn = self.get_connection()
        cursor = conn.cursor()

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

            cursor.execute(
                """
                INSERT INTO cbam_products 
                (company_id, product_code, product_name, hs_code, cn_code, 
                 sector, production_route)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    company_id,
                    code,
                    name,
                    product_data.get('hs_code'),
                    product_data.get('cn_code'),
                    product_data.get('sector'),
                    product_data.get('production_route'),
                ),
            )

            conn.commit()
            logging.info(f"[OK] CBAM ürünü eklendi: {code}")
            return True

        except Exception as e:
            logging.error(f"[HATA] CBAM ürünü ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()



    def record_emissions(self, product_id: int, emission_data: Dict) -> bool:
        """Emisyon verisi kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Toplam emisyon hesapla
            direct = emission_data.get('direct_emissions', 0) or 0
            indirect = emission_data.get('indirect_emissions', 0) or 0
            embedded = emission_data.get('embedded_emissions', 0) or 0
            total = direct + indirect + embedded

            cursor.execute("""
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

            conn.commit()
            logging.info("[OK] Emisyon verisi kaydedildi")
            return True

        except Exception as e:
            logging.error(f"[HATA] Emisyon kaydı hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def calculate_cbam_liability(self, company_id: int, period: str) -> Dict:
        """CBAM yükümlülüğünü hesapla"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # İthalat ve emisyon verilerini al
            cursor.execute("""
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
            """, (company_id, period))

            imports = []
            total_emissions = 0
            total_carbon_price_paid = 0

            for row in cursor.fetchall():
                product_id, product_name, sector, quantity, emissions, price_paid = row

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

            # EU ETS fiyatı (örnek - gerçek fiyat API'den alınmalı)
            eu_ets_price = 85.0  # EUR/ton CO2

            # Eğer ithalat verilerinden toplam emisyon sıfırsa, emisyon kayıtlarını fallback olarak kullan
            if total_emissions == 0:
                try:
                    cursor.execute("""
                        SELECT SUM(e.total_emissions)
                        FROM cbam_emissions e
                        JOIN cbam_products p ON e.product_id = p.id
                        WHERE p.company_id = ? AND e.reporting_period = ?
                    """, (company_id, period))
                    row = cursor.fetchone()
                    total_emissions = (row[0] or 0) if row else 0
                except Exception as _:
                    total_emissions = 0

            # CBAM yükümlülüğü = (Toplam Emisyon * EU ETS Fiyatı) - Ödenen Karbon Fiyatı
            cbam_liability = (total_emissions * eu_ets_price) - total_carbon_price_paid

            return {
                'period': period,
                'total_imports': len(imports),
                'total_quantity': sum(imp['quantity'] for imp in imports),
                'total_emissions': total_emissions,
                'eu_ets_price': eu_ets_price,
                'carbon_price_paid': total_carbon_price_paid,
                'cbam_liability': max(0, cbam_liability),
                'imports': imports
            }

        except Exception as e:
            logging.error(f"[HATA] CBAM yükümlülük hesaplama hatası: {e}")
            return {}
        finally:
            conn.close()

    def get_products(self, company_id: int) -> List[Dict]:
        """CBAM ürünlerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, product_code, product_name, hs_code, cn_code, 
                       sector, production_route
                FROM cbam_products
                WHERE company_id = ?
                ORDER BY sector, product_name
            """, (company_id,))

            columns = [desc[0] for desc in cursor.description]
            products = []

            for row in cursor.fetchall():
                product = dict(zip(columns, row))
                products.append(product)

            return products

        except Exception as e:
            logging.error(f"[HATA] CBAM ürünleri getirme hatası: {e}")
            return []
        finally:
            conn.close()

    def add_emission_data(self, emission_data: Dict) -> bool:
        """Emisyon verisi ekle"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO cbam_emissions (
                    product_id, reporting_period, emission_type, direct_emissions, indirect_emissions,
                    embedded_emissions, total_emissions, calculation_method, data_quality, verification_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                emission_data['product_id'],
                emission_data['reporting_period'],
                emission_data['emission_type'],
                emission_data['direct_emissions'],
                emission_data['indirect_emissions'],
                emission_data['embedded_emissions'],
                emission_data['total_emissions'],
                emission_data['calculation_method'],
                emission_data['data_quality'],
                emission_data['verification_status'],
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logging.error(f"Emisyon verisi ekleme hatası: {e}")
            return False

    def get_emissions(self, company_id: int, period: str = None) -> List[Dict]:
        """Emisyon verilerini al"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT e.*, p.product_name, p.product_code
            FROM cbam_emissions e
            LEFT JOIN cbam_products p ON e.product_id = p.id
            WHERE p.company_id = ?
        """
        params = [company_id]

        if period:
            query += " AND e.reporting_period = ?"
            params.append(period)

        query += " ORDER BY e.created_at DESC"

        cursor.execute(query, params)

        columns = [description[0] for description in cursor.description]
        results = []

        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        conn.close()
        return results

    def get_imports(self, company_id: int, period: str = None) -> List[Dict]:
        """İthalat verilerini al"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT i.*, p.product_name, p.product_code
            FROM cbam_imports i
            LEFT JOIN cbam_products p ON i.product_id = p.id
            WHERE i.company_id = ?
        """
        params = [company_id]

        if period:
            query += " AND i.import_period = ?"
            params.append(period)

        query += " ORDER BY i.created_at DESC"

        cursor.execute(query, params)

        columns = [description[0] for description in cursor.description]
        results = []

        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))

        conn.close()
        return results

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



    def add_products_bulk(self, company_id: int, products: List[Dict]) -> bool:
        """Toplu ürün ekleme - Yüksek performans için optimize edilmiş"""
        if not products:
            return True

        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Tüm ürünleri tek transaction'da ekle
            product_values = []
            for product in products:
                if isinstance(product, dict):
                    product_values.append((
                        company_id,
                        product.get('product_code'),
                        product.get('product_name'),
                        product.get('hs_code'),
                        product.get('cn_code'),
                        product.get('sector'),
                        product.get('production_route')
                    ))
                else:
                    # Tuple olarak geliyorsa direkt ekle (product_code, product_name, sector format)
                    product_values.append((
                        company_id,
                        product[0] if len(product) > 0 else None,
                        product[1] if len(product) > 1 else None,
                        None,  # hs_code
                        None,  # cn_code
                        product[2] if len(product) > 2 else None,
                        None   # production_route
                    ))

            # executemany ile toplu insert - çok daha hızlı!
            cursor.executemany("""
                INSERT INTO cbam_products 
                (company_id, product_code, product_name, hs_code, cn_code, sector, production_route)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, product_values)

            conn.commit()
            logging.info(f"[OK] {len(products)} CBAM ürünü toplu olarak eklendi")
            return True

        except Exception as e:
            logging.error(f"[HATA] Toplu ürün ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_import_record(self, company_id: int, import_period: str, origin_country: str,
                         quantity: float, quantity_unit: str = 'ton', customs_value: float = 0,
                         currency: str = 'EUR', embedded_emissions: float = 0,
                         carbon_price_paid: float = 0, product_id: int = None) -> bool:
        """Yeni ithalat kaydı ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Eğer product_id verilmemişse, ilk ürünü kullan
            if not product_id:
                cursor.execute("SELECT id FROM cbam_products WHERE company_id = ? LIMIT 1", (company_id,))
                result = cursor.fetchone()
                if result:
                    product_id = result[0]
                else:
                    logging.error("[HATA] Hiç ürün bulunamadı!")
                    return False

            cursor.execute("""
                INSERT INTO cbam_imports 
                (company_id, product_id, import_period, origin_country, quantity, quantity_unit,
                 customs_value, currency, embedded_emissions, carbon_price_paid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, product_id, import_period, origin_country, quantity, quantity_unit,
                  customs_value, currency, embedded_emissions, carbon_price_paid))

            conn.commit()
            logging.info(f"[OK] İthalat kaydı eklendi: {origin_country}")
            return True

        except Exception as e:
            logging.error(f"[HATA] İthalat kaydı ekleme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def export_cbam_xml(self, company_id: int, period: str) -> bool:
        """CBAM XML export"""
        try:
            # XML export mantığı buraya eklenecek
            logging.info(f"CBAM XML export: {period}")
            return True

        except Exception as e:
            logging.error(f"XML export hatası: {e}")
            return False

# Test fonksiyonu
if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    manager = CBAMManager(db_path)

    # Test ürün ekle
    test_product = {
        'product_code': 'CEMENT-001',
        'product_name': 'Portland Çimentosu',
        'hs_code': '2523.29',
        'cn_code': '2523 29 00',
        'sector': 'cement',
        'production_route': 'Clinker bazlı'
    }

    manager.add_product(company_id=1, product_data=test_product)
