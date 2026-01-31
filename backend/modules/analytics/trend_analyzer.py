#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trend Analizi
Çok yıllı performans analizi ve tahminleme
"""

import logging
import sqlite3
import statistics
from typing import Dict, List, Optional


class TrendAnalyzer:
    """Trend analizi ve tahminleme"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def get_metric_trend(self, company_id: int, table_name: str,
                        metric_name: str, years: List[int]) -> List[Dict]:
        """Metrik trendini al"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(years))
            query = f"""
                SELECT year, {metric_name}
                FROM {table_name}
                WHERE company_id = ? AND year IN ({placeholders})
                AND {metric_name} IS NOT NULL
                ORDER BY year
            """

            cursor.execute(query, [company_id] + years)

            trend_data = []
            for row in cursor.fetchall():
                trend_data.append({
                    'year': row[0],
                    'value': row[1]
                })

            conn.close()
            return trend_data

        except Exception as e:
            logging.error(f"Trend alma hatası: {e}")
            return []

    def calculate_trend_statistics(self, trend_data: List[Dict]) -> Dict:
        """Trend istatistikleri hesapla"""
        if len(trend_data) < 2:
            return {
                'trend': 'insufficient_data',
                'change_percent': 0,
                'average': 0,
                'min': 0,
                'max': 0
            }

        values = [d['value'] for d in trend_data]
        years = [d['year'] for d in trend_data]

        # Yıllık değişim yüzdesi
        first_value = values[0]
        last_value = values[-1]

        if first_value != 0:
            total_change = ((last_value - first_value) / first_value) * 100
        else:
            total_change = 0

        # Yıl sayısı
        year_span = years[-1] - years[0]
        if year_span > 0:
            annual_change = total_change / year_span
        else:
            annual_change = 0

        # Trend yönü
        if annual_change > 5:
            trend = 'increasing'
            trend_text = 'Artan'
        elif annual_change < -5:
            trend = 'decreasing'
            trend_text = 'Azalan'
        else:
            trend = 'stable'
            trend_text = 'Stabil'

        return {
            'trend': trend,
            'trend_text': trend_text,
            'total_change_percent': round(total_change, 1),
            'annual_change_percent': round(annual_change, 1),
            'average': round(statistics.mean(values), 2),
            'min': min(values),
            'max': max(values),
            'std_dev': round(statistics.stdev(values), 2) if len(values) > 1 else 0
        }

    def predict_next_year(self, trend_data: List[Dict], method: str = 'linear') -> Optional[float]:
        """Gelecek yıl tahmini"""
        if len(trend_data) < 2:
            return None

        values = [d['value'] for d in trend_data]

        if method == 'linear':
            # Basit lineer tahmin (son iki değerin ortalaması)
            return values[-1] + (values[-1] - values[-2])

        elif method == 'average':
            # Ortalama değişim
            changes = [values[i+1] - values[i] for i in range(len(values)-1)]
            avg_change = statistics.mean(changes)
            return values[-1] + avg_change

        elif method == 'exponential':
            # Exponential smoothing (alpha = 0.3)
            alpha = 0.3
            forecast = values[0]
            for value in values[1:]:
                forecast = alpha * value + (1 - alpha) * forecast
            return forecast

        return None

    def compare_years(self, company_id: int, table_name: str,
                     metric_name: str, year1: int, year2: int) -> Dict:
        """İki yılı karşılaştır"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = f"""
                SELECT year, {metric_name}
                FROM {table_name}
                WHERE company_id = ? AND year IN (?, ?)
                AND {metric_name} IS NOT NULL
                ORDER BY year
            """

            cursor.execute(query, (company_id, year1, year2))
            results = cursor.fetchall()
            conn.close()

            if len(results) != 2:
                return {'error': 'Yetersiz veri'}

            value1 = results[0][1]
            value2 = results[1][1]

            change = value2 - value1
            if value1 != 0:
                change_percent = (change / value1) * 100
            else:
                change_percent = 0

            return {
                'year1': year1,
                'value1': value1,
                'year2': year2,
                'value2': value2,
                'change': round(change, 2),
                'change_percent': round(change_percent, 1),
                'direction': 'artış' if change > 0 else 'azalış' if change < 0 else 'değişmedi'
            }

        except Exception as e:
            logging.error(f"Karşılaştırma hatası: {e}")
            return {'error': str(e)}

    def get_multi_metric_trends(self, company_id: int, metrics: List[Dict],
                                years: List[int]) -> Dict:
        """Çoklu metrik trendlerini al"""
        trends = {}

        for metric in metrics:
            table = metric['table']
            field = metric['field']
            name = metric['name']

            trend_data = self.get_metric_trend(company_id, table, field, years)

            if trend_data:
                stats = self.calculate_trend_statistics(trend_data)
                prediction = self.predict_next_year(trend_data)

                trends[name] = {
                    'data': trend_data,
                    'statistics': stats,
                    'prediction': prediction
                }

        return trends

    def detect_anomalies(self, trend_data: List[Dict], threshold: float = 2.0) -> List[Dict]:
        """Anom alileri tespit et (standart sapma bazlı)"""
        if len(trend_data) < 3:
            return []

        values = [d['value'] for d in trend_data]
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)

        anomalies = []
        for data_point in trend_data:
            z_score = abs((data_point['value'] - mean) / std_dev) if std_dev > 0 else 0

            if z_score > threshold:
                anomalies.append({
                    'year': data_point['year'],
                    'value': data_point['value'],
                    'z_score': round(z_score, 2),
                    'severity': 'high' if z_score > 3 else 'medium'
                })

        return anomalies

