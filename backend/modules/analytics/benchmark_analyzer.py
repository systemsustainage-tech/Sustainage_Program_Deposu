#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Benchmark Analizi
Sektör karşılaştırması ve performans skorlama
"""

import statistics
from typing import Dict, List


class BenchmarkAnalyzer:
    """Sektör benchmark analizi"""

    # Sektör ortalamaları (örnek veriler)
    SECTOR_BENCHMARKS = {
        'İmalat': {
            'carbon_intensity': 2.5,  # tCO2e per unit
            'energy_intensity': 150,  # kWh per unit
            'water_intensity': 10,  # m³ per unit
            'waste_recycling_rate': 60,  # %
            'employee_training_hours': 25,  # hours per employee
            'ltifr': 2.0  # Lost Time Injury Frequency Rate
        },
        'Hizmet': {
            'carbon_intensity': 0.5,
            'energy_intensity': 30,
            'water_intensity': 2,
            'waste_recycling_rate': 70,
            'employee_training_hours': 30,
            'ltifr': 0.5
        },
        'Enerji': {
            'carbon_intensity': 5.0,
            'energy_intensity': 300,
            'water_intensity': 15,
            'waste_recycling_rate': 50,
            'employee_training_hours': 35,
            'ltifr': 3.0
        }
    }

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def compare_to_sector(self, company_id: int, sector: str, metrics: Dict[str, float]) -> Dict:
        """Şirket metriklerini sektör ortalamasıyla karşılaştır"""

        if sector not in self.SECTOR_BENCHMARKS:
            sector = 'İmalat'  # Default

        sector_avgs = self.SECTOR_BENCHMARKS[sector]
        comparisons = {}

        for metric, company_value in metrics.items():
            if metric in sector_avgs:
                sector_value = sector_avgs[metric]

                # Performans skoru hesapla
                # Düşük olması iyi olan metrikler için (carbon, energy, water, ltifr)
                if metric in ['carbon_intensity', 'energy_intensity', 'water_intensity', 'ltifr']:
                    if sector_value > 0:
                        performance = (sector_value / company_value) * 100
                    else:
                        performance = 100
                # Yüksek olması iyi olan metrikler için (recycling, training)
                else:
                    if sector_value > 0:
                        performance = (company_value / sector_value) * 100
                    else:
                        performance = 100

                # Performans kategori
                if performance >= 120:
                    category = 'Mükemmel'
                    color = '#27ae60'
                elif performance >= 100:
                    category = 'İyi'
                    color = '#2ecc71'
                elif performance >= 80:
                    category = 'Orta'
                    color = '#f39c12'
                else:
                    category = 'Zayıf'
                    color = '#e74c3c'

                comparisons[metric] = {
                    'company_value': company_value,
                    'sector_average': sector_value,
                    'performance_score': round(performance, 1),
                    'category': category,
                    'color': color,
                    'difference_percent': round(((company_value - sector_value) / sector_value * 100), 1) if sector_value > 0 else 0
                }

        return comparisons

    def calculate_overall_score(self, comparisons: Dict) -> Dict:
        """Genel performans skoru hesapla"""
        if not comparisons:
            return {'score': 0, 'grade': 'N/A', 'description': 'Veri yok'}

        scores = [comp['performance_score'] for comp in comparisons.values()]
        avg_score = statistics.mean(scores)

        # Harf notu
        if avg_score >= 120:
            grade = 'A+'
            description = 'Sektör lideri'
        elif avg_score >= 110:
            grade = 'A'
            description = 'Çok iyi'
        elif avg_score >= 100:
            grade = 'B+'
            description = 'İyi'
        elif avg_score >= 90:
            grade = 'B'
            description = 'Sektör ortalaması'
        elif avg_score >= 80:
            grade = 'C+'
            description = 'Ortalamanın altında'
        elif avg_score >= 70:
            grade = 'C'
            description = 'İyileştirme gerekli'
        else:
            grade = 'D'
            description = 'Acil aksiyon gerekli'

        return {
            'score': round(avg_score, 1),
            'grade': grade,
            'description': description,
            'total_metrics': len(scores)
        }

    def get_improvement_recommendations(self, comparisons: Dict) -> List[Dict]:
        """İyileştirme önerileri"""
        recommendations = []

        # Zayıf performans gösteren metrikleri bul
        weak_metrics = {k: v for k, v in comparisons.items() if v['performance_score'] < 100}

        # Öncelik sırasına göre sırala
        sorted_metrics = sorted(weak_metrics.items(), key=lambda x: x[1]['performance_score'])

        for metric, data in sorted_metrics[:5]:  # Top 5
            recommendations.append({
                'metric': metric,
                'current': data['company_value'],
                'target': data['sector_average'],
                'gap': abs(data['difference_percent']),
                'priority': 'Yüksek' if data['performance_score'] < 80 else 'Orta',
                'recommendation': self._get_recommendation_text(metric, data)
            })

        return recommendations

    def _get_recommendation_text(self, metric: str, data: Dict) -> str:
        """Metrik için öneri metni"""
        recommendations_map = {
            'carbon_intensity': 'Enerji verimliliğini artırın ve yenilenebilir enerji kullanımını genişletin.',
            'energy_intensity': 'Enerji tasarrufu projeleri başlatın ve ISO 50001 uyumluluğunu hedefleyin.',
            'water_intensity': 'Su geri kazanım sistemleri kurun ve su verimliliği programı başlatın.',
            'waste_recycling_rate': 'Atık ayrıştırma sistemini güçlendirin ve döngüsel ekonomi ilkelerini benimseyin.',
            'employee_training_hours': 'Eğitim programlarını çeşitlendirin ve online eğitim platformları kullanın.',
            'ltifr': 'İSG eğitimlerini artırın, risk değerlendirmelerini güçlendirin ve near-miss raporlamayı teşvik edin.'
        }

        return recommendations_map.get(metric, 'Sektör en iyi uygulamalarını inceleyin ve iyileştirme planı oluşturun.')

