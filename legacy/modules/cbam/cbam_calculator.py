#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CBAM (Carbon Border Adjustment Mechanism) Hesaplayıcı
İnovasyon ile CBAM sertifika maliyeti tasarrufu hesaplama
"""

import os
from typing import Dict

from utils import get_db_cursor, log_error, log_info


class CBAMCalculator:
    """
    CBAM maliyet ve tasarruf hesaplama
    
    Formüller:
    E_post = E_base × [1 - innovation_ratio × attenuation_factor]
    CBAM_cost = max(E - domestic_carbon_price, 0) × EU_ETS_price × volume
    Saving = CBAM_cost_baseline - CBAM_cost_post_innovation
    """

    CBAM_SECTORS = ['steel', 'cement', 'aluminum', 'fertilizer', 'electricity', 'hydrogen']

    def __init__(self, db_path: str = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), 'data', 'sdg_desktop.sqlite')

    def compute_cbam_savings(self, company_id: int, period: int) -> Dict:
        """
        Şirketin CBAM tasarrufunu hesapla
        
        Args:
            company_id: Firma ID
            period: Yıl (2024, 2025...)
        
        Returns:
            Dict: {
                'total_saving_eur': float,
                'products': List[Dict],
                'summary': Dict
            }
        """
        with get_db_cursor(self.db_path) as cursor:
            try:
                # EU ETS fiyatını al
                eu_ets_price = self._get_eu_ets_price(cursor, period)

                if eu_ets_price == 0:
                    log_error(f"EU ETS fiyatı bulunamadı: {period}", module='CBAM')
                    return {'error': 'EU ETS fiyatı tanımlı değil', 'total_saving_eur': 0}

                # İnovasyon oranını al
                innovation_ratio = self._get_innovation_ratio(cursor, company_id, period)

                # Ürünleri al
                cursor.execute("""
                    SELECT id, product_code, cbam_sector, baseline_emission_intensity,
                           post_innovation_emission_intensity, trade_volume_tons,
                           domestic_carbon_price_eur_per_tco2
                    FROM cbam_products
                    WHERE company_id=? AND period=?
                """, (company_id, period))

                products_data = []
                total_saving = 0

                for row in cursor.fetchall():
                    product_result = self._calculate_product_saving(
                        row, eu_ets_price, innovation_ratio, cursor, company_id, period
                    )
                    products_data.append(product_result)
                    total_saving += product_result['saving_eur']

                log_info(f"CBAM tasarruf hesaplandı: {total_saving:.2f} EUR",
                        module='CBAM', company_id=company_id)

                return {
                    'total_saving_eur': round(total_saving, 2),
                    'eu_ets_price': eu_ets_price,
                    'innovation_ratio': innovation_ratio,
                    'products': products_data,
                    'product_count': len(products_data),
                    'period': period
                }

            except Exception as e:
                log_error(f"CBAM hesaplama hatası: {e}", module='CBAM', company_id=company_id)
                return {'error': str(e), 'total_saving_eur': 0}

    def _calculate_product_saving(self, row, eu_ets_price: float, default_innovation_ratio: float,
                                  cursor, company_id: int, period: int) -> Dict:
        """Tek ürün için CBAM tasarrufu"""

        product_id, product_code, sector, e_base, e_post, volume, domestic_price = row

        # Innovation link var mı?
        cursor.execute("""
            SELECT innovation_share_ratio, attenuation_factor
            FROM cbam_innovation_links
            WHERE company_id=? AND period=? AND product_code=?
        """, (company_id, period, product_code))

        link = cursor.fetchone()

        if link:
            innovation_ratio = link[0]
            attenuation = link[1]
        else:
            # Varsayılan: şirket geneli
            innovation_ratio = default_innovation_ratio
            attenuation = 0.6

        # E_post hesapla (eğer yoksa)
        if e_post is None or e_post == 0:
            e_post = e_base * (1 - innovation_ratio * attenuation)

        # CBAM maliyetleri
        cbam_cost_baseline = max(e_base - domestic_price, 0) * eu_ets_price * volume
        cbam_cost_post = max(e_post - domestic_price, 0) * eu_ets_price * volume

        # Tasarruf
        saving = cbam_cost_baseline - cbam_cost_post

        # Güncelle (hesaplanan e_post'u kaydet)
        cursor.execute("""
            UPDATE cbam_products 
            SET post_innovation_emission_intensity=?, last_updated=CURRENT_TIMESTAMP
            WHERE id=?
        """, (e_post, product_id))

        return {
            'product_code': product_code,
            'sector': sector,
            'e_baseline': round(e_base, 3),
            'e_post_innovation': round(e_post, 3),
            'emission_reduction_pct': round((e_base - e_post) / e_base * 100, 2) if e_base > 0 else 0,
            'trade_volume_tons': volume,
            'cbam_cost_baseline_eur': round(cbam_cost_baseline, 2),
            'cbam_cost_post_eur': round(cbam_cost_post, 2),
            'saving_eur': round(saving, 2),
            'innovation_ratio': innovation_ratio,
            'attenuation_factor': attenuation
        }

    def _get_eu_ets_price(self, cursor, period: int) -> float:
        """EU ETS fiyatını al"""
        cursor.execute("""
            SELECT eu_ets_price_eur_per_tco2 
            FROM cbam_factors 
            WHERE period=?
        """, (period,))

        row = cursor.fetchone()
        return row[0] if row else 0

    def _get_innovation_ratio(self, cursor, company_id: int, period: int) -> float:
        """Şirket inovasyon oranını al"""
        try:
            cursor.execute("""
                SELECT sustainability_innovation_ratio 
                FROM innovation_metrics 
                WHERE company_id=? AND period=?
            """, (company_id, str(period)))

            row = cursor.fetchone()
            return (row[0] / 100.0) if row and row[0] else 0
        except Exception:
            return 0

    def save_cbam_product(self, company_id: int, period: int, product_code: str,
                         cbam_sector: str, baseline_emission: float,
                         trade_volume: float, **kwargs) -> int:
        """CBAM ürün kaydı ekle"""
        with get_db_cursor(self.db_path) as cursor:
            cursor.execute("""
                INSERT INTO cbam_products 
                (company_id, period, product_code, cbam_sector, baseline_emission_intensity,
                 trade_volume_tons, domestic_carbon_price_eur_per_tco2, importing_region)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id, period, product_code) DO UPDATE SET
                    baseline_emission_intensity=excluded.baseline_emission_intensity,
                    trade_volume_tons=excluded.trade_volume_tons,
                    last_updated=CURRENT_TIMESTAMP
            """, (company_id, period, product_code, cbam_sector, baseline_emission,
                  trade_volume, kwargs.get('domestic_price', 0),
                  kwargs.get('importing_region', 'EU')))

            return cursor.lastrowid

    def save_cbam_factor(self, period: int, eu_ets_price: float, **kwargs) -> bool:
        """EU ETS fiyatı kaydet"""
        with get_db_cursor(self.db_path) as cursor:
            cursor.execute("""
                INSERT INTO cbam_factors (period, eu_ets_price_eur_per_tco2, notes)
                VALUES (?, ?, ?)
                ON CONFLICT(period) DO UPDATE SET
                    eu_ets_price_eur_per_tco2=excluded.eu_ets_price_eur_per_tco2
            """, (period, eu_ets_price, kwargs.get('notes')))

            return True

    def link_innovation_to_product(self, company_id: int, period: int,
                                  product_code: str, innovation_ratio: float = None,
                                  attenuation: float = 0.6) -> bool:
        """Ürüne inovasyon bağla"""

        # Oran verilmemişse şirket genelini al
        if innovation_ratio is None:
            with get_db_cursor(self.db_path) as cursor:
                innovation_ratio = self._get_innovation_ratio(cursor, company_id, period)

        with get_db_cursor(self.db_path) as cursor:
            cursor.execute("""
                INSERT INTO cbam_innovation_links 
                (company_id, period, product_code, innovation_share_ratio, attenuation_factor)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(company_id, period, product_code) DO UPDATE SET
                    innovation_share_ratio=excluded.innovation_share_ratio,
                    attenuation_factor=excluded.attenuation_factor
            """, (company_id, period, product_code, innovation_ratio, attenuation))

            return True

