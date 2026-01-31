"""
CBAM (Carbon Border Adjustment Mechanism) Manager
SKDM İnovasyon Etkisi ve Tasarruf Hesaplamaları
"""

from datetime import datetime
from typing import Dict

from core.db_manager import db_manager
from core.logger import sdg_logger
from config.database import DB_PATH


class CBAMManager:
    """CBAM hesaplamaları ve inovasyon etkisi yöneticisi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """CBAM tablolarını oluştur"""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # CBAM ürünleri tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cbam_products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        period INTEGER NOT NULL,
                        product_code TEXT NOT NULL,
                        product_name TEXT,
                        cbam_sector TEXT NOT NULL,
                        baseline_emission_intensity REAL NOT NULL,
                        post_innovation_emission_intensity REAL,
                        trade_volume_tons REAL NOT NULL,
                        domestic_carbon_price_eur_per_tco2 REAL DEFAULT 0,
                        importing_region TEXT DEFAULT 'EU',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(company_id, period, product_code)
                    )
                """)

                # CBAM faktörleri tablosu
                cursor.execute("""
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

                # İnovasyon bağlantıları tablosu
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cbam_innovation_links (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_id INTEGER NOT NULL,
                        period INTEGER NOT NULL,
                        product_code TEXT NOT NULL,
                        innovation_share_ratio REAL NOT NULL,
                        attenuation_factor REAL DEFAULT 0.6,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(company_id, period, product_code)
                    )
                """)

                conn.commit()
                sdg_logger.log_info("CBAM tabloları oluşturuldu/doğrulandı", "cbam_manager")

        except Exception as e:
            sdg_logger.log_error(e, "CBAM tabloları oluşturma", module="cbam_manager")

    def save_cbam_product(self, company_id: int, period: int, product_code: str,
                         product_name: str, cbam_sector: str, baseline_emission: float,
                         trade_volume: float, domestic_carbon_price: float = 0) -> bool:
        """CBAM ürünü kaydet"""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO cbam_products 
                    (company_id, period, product_code, product_name, cbam_sector,
                     baseline_emission_intensity, trade_volume_tons, domestic_carbon_price_eur_per_tco2,
                     updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (company_id, period, product_code, product_name, cbam_sector,
                      baseline_emission, trade_volume, domestic_carbon_price, datetime.now()))

                conn.commit()
                sdg_logger.log_info(f"CBAM ürünü kaydedildi: {product_code}", "cbam_manager")
                return True

        except Exception as e:
            sdg_logger.log_error(e, f"CBAM ürünü kaydetme: {product_code}", module="cbam_manager")
            return False

    def save_cbam_factor(self, period: int, eu_ets_price: float,
                        leakage_factor: float = 0.6, notes: str = "") -> bool:
        """CBAM faktörü kaydet"""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO cbam_factors 
                    (period, eu_ets_price_eur_per_tco2, default_leakage_factor, notes)
                    VALUES (?, ?, ?, ?)
                """, (period, eu_ets_price, leakage_factor, notes))

                conn.commit()
                sdg_logger.log_info(f"CBAM faktörü kaydedildi: {period}", "cbam_manager")
                return True

        except Exception as e:
            sdg_logger.log_error(e, f"CBAM faktörü kaydetme: {period}", module="cbam_manager")
            return False

    def link_innovation_to_product(self, company_id: int, period: int, product_code: str,
                                  innovation_ratio: float, attenuation_factor: float = 0.6) -> bool:
        """İnovasyon oranını ürüne bağla"""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO cbam_innovation_links 
                    (company_id, period, product_code, innovation_share_ratio, attenuation_factor, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (company_id, period, product_code, innovation_ratio, attenuation_factor, datetime.now()))

                conn.commit()
                sdg_logger.log_info(f"İnovasyon bağlantısı kuruldu: {product_code}", "cbam_manager")
                return True

        except Exception as e:
            sdg_logger.log_error(e, f"İnovasyon bağlantısı: {product_code}", module="cbam_manager")
            return False

    def compute_cbam_savings(self, company_id: int, period: int) -> Dict[str, any]:
        """
        CBAM tasarruflarını hesapla
        
        Formüller:
        E_post(i) = E_base(i) × [1 − innovation_share_ratio(i) × attenuation_factor(i)]
        CBAM_cost_base(i) = max(E_base(i) − carbon_price_paid_domestic(i), 0) × EU_ETS_price × trade_volume(i)
        CBAM_cost_post(i) = max(E_post(i) − carbon_price_paid_domestic(i), 0) × EU_ETS_price × trade_volume(i)
        CBAM_saving(i) = CBAM_cost_base(i) − CBAM_cost_post(i)
        """
        try:
            with db_manager.get_connection(read_only=True) as conn:
                cursor = conn.cursor()

                # CBAM faktörlerini al
                cursor.execute("SELECT eu_ets_price_eur_per_tco2 FROM cbam_factors WHERE period = ?", (period,))
                factor_result = cursor.fetchone()
                if not factor_result:
                    # Varsayılan ETS fiyatı
                    eu_ets_price = 80.0
                    sdg_logger.log_warning(f"CBAM faktörü bulunamadı, varsayılan fiyat kullanıldı: {eu_ets_price}", "cbam_manager")
                else:
                    eu_ets_price = factor_result[0]

                # Ürünleri ve inovasyon bağlantılarını al
                cursor.execute("""
                    SELECT 
                        p.product_code, p.product_name, p.baseline_emission_intensity,
                        p.trade_volume_tons, p.domestic_carbon_price_eur_per_tco2,
                        COALESCE(l.innovation_share_ratio, 0) as innovation_ratio,
                        COALESCE(l.attenuation_factor, 0.6) as attenuation_factor
                    FROM cbam_products p
                    LEFT JOIN cbam_innovation_links l ON p.company_id = l.company_id 
                        AND p.period = l.period AND p.product_code = l.product_code
                    WHERE p.company_id = ? AND p.period = ?
                """, (company_id, period))

                products = cursor.fetchall()

                if not products:
                    return {
                        "total_savings": 0,
                        "total_emission_reduction": 0,
                        "products": [],
                        "summary": "Ürün bulunamadı"
                    }

                results = []
                total_savings = 0
                total_emission_reduction = 0

                for product in products:
                    (product_code, product_name, e_base, trade_volume,
                     domestic_price, innovation_ratio, attenuation_factor) = product

                    # İnovasyon etkili emisyon yoğunluğu
                    e_post = e_base * (1 - innovation_ratio * attenuation_factor)

                    # CBAM maliyetleri
                    cbam_cost_base = max(e_base - domestic_price, 0) * eu_ets_price * trade_volume
                    cbam_cost_post = max(e_post - domestic_price, 0) * eu_ets_price * trade_volume

                    # Tasarruf
                    cbam_saving = cbam_cost_base - cbam_cost_post
                    emission_reduction = (e_base - e_post) * trade_volume

                    total_savings += cbam_saving
                    total_emission_reduction += emission_reduction

                    results.append({
                        "product_code": product_code,
                        "product_name": product_name,
                        "e_base": e_base,
                        "e_post": e_post,
                        "trade_volume": trade_volume,
                        "innovation_ratio": innovation_ratio,
                        "attenuation_factor": attenuation_factor,
                        "cbam_cost_base": cbam_cost_base,
                        "cbam_cost_post": cbam_cost_post,
                        "cbam_saving": cbam_saving,
                        "emission_reduction": emission_reduction
                    })

                # Sonuç
                result = {
                    "total_savings": total_savings,
                    "total_emission_reduction": total_emission_reduction,
                    "eu_ets_price": eu_ets_price,
                    "products": results,
                    "summary": f"{len(results)} ürün için toplam {total_savings:,.0f} € tasarruf"
                }

                sdg_logger.log_info(f"CBAM tasarrufu hesaplandı: {total_savings:,.0f} €", "cbam_manager")
                return result

        except Exception as e:
            sdg_logger.log_error(e, "CBAM tasarrufu hesaplama", module="cbam_manager")
            return {"error": str(e), "total_savings": 0, "products": []}

    def get_company_cbam_summary(self, company_id: int, period: int) -> Dict[str, any]:
        """Şirket CBAM özeti"""
        try:
            with db_manager.get_connection(read_only=True) as conn:
                cursor = conn.cursor()

                # Ürün sayısı
                cursor.execute("""
                    SELECT COUNT(*) FROM cbam_products 
                    WHERE company_id = ? AND period = ?
                """, (company_id, period))
                product_count = cursor.fetchone()[0]

                # Toplam ticaret hacmi
                cursor.execute("""
                    SELECT SUM(trade_volume_tons) FROM cbam_products 
                    WHERE company_id = ? AND period = ?
                """, (company_id, period))
                total_volume = cursor.fetchone()[0] or 0

                # CBAM tasarrufu
                savings_data = self.compute_cbam_savings(company_id, period)

                return {
                    "product_count": product_count,
                    "total_volume_tons": total_volume,
                    "total_savings_eur": savings_data.get("total_savings", 0),
                    "total_emission_reduction": savings_data.get("total_emission_reduction", 0),
                    "eu_ets_price": savings_data.get("eu_ets_price", 80),
                    "products": savings_data.get("products", [])
                }

        except Exception as e:
            sdg_logger.log_error(e, "CBAM özet alma", module="cbam_manager")
            return {"error": str(e)}

    def create_sample_data(self, company_id: int = 1, period: int = 2024) -> None:
        """
        DEPRECATED: Örnek veri oluşturma devre dışı bırakıldı.
        """
        sdg_logger.log_info("create_sample_data çağrıldı ancak devre dışı bırakıldı (Gerçek veri zorunluluğu)", "cbam_manager")
        return

