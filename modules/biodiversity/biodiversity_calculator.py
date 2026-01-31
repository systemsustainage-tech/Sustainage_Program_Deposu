#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BİYOÇEŞİTLİLİK HESAPLAYICISI
Biyoçeşitlilik indekslerini ve KPI'larını hesaplar
"""

import logging
from typing import Dict, List, Optional

class BiodiversityCalculator:
    """Biyoçeşitlilik Hesaplama Motoru"""

    def __init__(self) -> None:
        pass

    def calculate_kpis(self, summary_data: Dict) -> Dict:
        """
        Biyoçeşitlilik KPI'larını hesaplar.
        
        Args:
            summary_data (Dict): get_biodiversity_summary() metodundan dönen veri yapısı
            
        Returns:
            Dict: Hesaplanmış KPI'lar
        """
        if not summary_data:
            return {}

        try:
            total_habitat_area = summary_data.get('total_habitat_area', 0)
            total_species_count = summary_data.get('total_species_count', 0)
            total_investment = summary_data.get('total_investment', 0)
            active_projects = summary_data.get('active_projects', 0)
            habitat_summary = summary_data.get('habitat_summary', {})

            # 1. Biyoçeşitlilik Yoğunluğu (Tür/m²)
            # Genellikle tür sayısı / alan (ha veya km2) olarak verilir ama burada m2 bazlı total_area geliyorsa dikkat.
            # total_habitat_area m2 cinsinden hesaplanıyor manager içinde.
            # Daha anlamlı olması için hektar başına tür sayısı verelim.
            total_area_ha = total_habitat_area / 10000.0
            biodiversity_density = (total_species_count / total_area_ha) if total_area_ha > 0 else 0

            # 2. Habitat Koruma Oranı
            # Koruma statüsüne göre alanları topla
            protected_area = 0.0
            # Not: summary_data['habitat_summary'] yapısı: {type: {'area': ..., 'unit': ..., 'count': ...}}
            # Bu özet yapısında 'protection_status' bilgisi kaybolmuş durumda.
            # Bu hesaplama için manager'dan daha detaylı veri gelmesi gerekebilir veya
            # varsayım olarak tüm habitat alanlarını korunan alan kabul ediyoruz (desktop implementasyonundaki gibi).
            # Desktop kodunda:
            # for habitat_data in summary['habitat_summary'].values():
            #     protected_area += habitat_data['area']
            # Yani tüm tanımlı habitat alanları "korunan alan" olarak varsayılmış.
            
            for habitat_data in habitat_summary.values():
                # Alan birim dönüşümü manager'da yapılmıştı ama summary içinde 'area' ham değer olabilir.
                # Manager koduna bakınca: total_area zaten dönüştürülmüş toplam.
                # habitat_summary içindeki 'area' ise ham değer.
                # Bu yüzden summary içindeki total_area'yı kullanmak daha güvenli.
                pass
            
            # Desktop mantığını koruyoruz: Tüm tanımlı habitat alanları koruma altındadır varsayımı.
            protection_ratio = 100.0 if total_habitat_area > 0 else 0.0
            
            # 3. Hektar Başına Yatırım
            investment_per_ha = (total_investment / total_area_ha) if total_area_ha > 0 else 0

            return {
                'total_habitat_area_m2': round(total_habitat_area, 2),
                'total_habitat_area_ha': round(total_area_ha, 2),
                'total_species_count': total_species_count,
                'biodiversity_density_per_ha': round(biodiversity_density, 2),
                'protection_ratio': round(protection_ratio, 2),
                'active_projects': active_projects,
                'total_investment': round(total_investment, 2),
                'investment_per_ha': round(investment_per_ha, 2)
            }

        except Exception as e:
            logging.error(f"[HATA] Biyoçeşitlilik KPI hesaplama hatası: {e}")
            return {}

    def calculate_shannon_index(self, species_counts: List[int]) -> float:
        """
        Shannon Çeşitlilik İndeksi (H') hesaplar.
        H' = -sum(pi * ln(pi))
        
        Args:
            species_counts: Her bir türün birey sayısını içeren liste
        """
        import math
        
        total_individuals = sum(species_counts)
        if total_individuals == 0:
            return 0.0
            
        shannon_index = 0.0
        for count in species_counts:
            if count > 0:
                pi = count / total_individuals
                shannon_index += pi * math.log(pi)
                
        return round(-shannon_index, 3)

    def calculate_simpson_index(self, species_counts: List[int]) -> float:
        """
        Simpson Çeşitlilik İndeksi (D) hesaplar.
        D = 1 - sum(n(n-1) / N(N-1))
        
        Args:
            species_counts: Her bir türün birey sayısını içeren liste
        """
        total_individuals = sum(species_counts)
        if total_individuals <= 1:
            return 0.0
            
        numerator = sum(n * (n - 1) for n in species_counts)
        denominator = total_individuals * (total_individuals - 1)
        
        if denominator == 0:
            return 0.0
            
        D = 1 - (numerator / denominator)
        return round(D, 3)
