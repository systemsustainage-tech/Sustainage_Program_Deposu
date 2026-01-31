#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Tahmin ve Trend Sistemi - TAM VE EKSİKSİZ
Linear Regression, Time Series, Hedef Tahmini, What-If Analizi
"""

import logging
import json
import os
import sqlite3
import statistics
from datetime import datetime
from typing import Dict, List
from config.database import DB_PATH


class AdvancedForecasting:
    """Gelişmiş tahmin ve trend analizi sistemi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_forecast_tables()

    def _init_forecast_tables(self) -> None:
        """Tahmin tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Trend verileri (5-10 yıl)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trend_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    metric_code TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    actual_value REAL NOT NULL,
                    predicted_value REAL,
                    prediction_accuracy REAL,
                    data_source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, metric_code, year)
                )
            """)

            # Tahmin sonuçları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forecast_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    metric_code TEXT NOT NULL,
                    forecast_year INTEGER NOT NULL,
                    forecast_value REAL NOT NULL,
                    forecast_method TEXT NOT NULL,
                    confidence_interval_lower REAL,
                    confidence_interval_upper REAL,
                    confidence_level REAL DEFAULT 95.0,
                    assumptions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, metric_code, forecast_year, forecast_method)
                )
            """)

            # Hedef erişim tahminleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS target_forecasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    metric_code TEXT NOT NULL,
                    current_value REAL NOT NULL,
                    target_value REAL NOT NULL,
                    target_year INTEGER NOT NULL,
                    estimated_achievement_year INTEGER,
                    probability_of_achievement REAL,
                    required_annual_change REAL,
                    risk_level TEXT,
                    recommendations TEXT,
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # What-if senaryoları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS whatif_scenarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    scenario_name TEXT NOT NULL,
                    scenario_description TEXT,
                    metric_code TEXT NOT NULL,
                    baseline_value REAL NOT NULL,
                    change_percentage REAL NOT NULL,
                    projected_value REAL NOT NULL,
                    impact_analysis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logging.info("[OK] Tahmin tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[ERROR] Tahmin tablolari olusturulurken hata: {e}")
        finally:
            conn.close()

    # =====================================================
    # 1. LINEAR REGRESSION TAHMİNİ
    # =====================================================

    def linear_regression_forecast(self, historical_data: List[Dict],
                                   forecast_years: int = 3) -> List[Dict]:
        """
        Linear regression ile tahmin
        
        Args:
            historical_data: [{"year": 2020, "value": 100}, ...]
            forecast_years: Kaç yıl ilerisi tahmin edilecek
            
        Returns:
            Tahmin sonuçları
        """
        if len(historical_data) < 2:
            return []

        try:
            # Linear regression formülü: y = mx + b
            years = [d['year'] for d in historical_data]
            values = [d['value'] for d in historical_data]

            n = len(years)
            sum_x = sum(years)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(years, values))
            sum_x2 = sum(x * x for x in years)

            # Slope (m) ve intercept (b) hesapla
            m = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            b = (sum_y - m * sum_x) / n

            # Tahminleri hesapla
            last_year = max(years)
            forecasts = []

            for i in range(1, forecast_years + 1):
                forecast_year = last_year + i
                forecast_value = m * forecast_year + b

                # Güven aralığı hesapla (basitleştirilmiş)
                std_error = self._calculate_standard_error(years, values, m, b)
                confidence_margin = 1.96 * std_error  # %95 güven aralığı

                forecasts.append({
                    "year": forecast_year,
                    "forecast_value": round(forecast_value, 2),
                    "method": "Linear Regression",
                    "confidence_lower": round(forecast_value - confidence_margin, 2),
                    "confidence_upper": round(forecast_value + confidence_margin, 2),
                    "slope": round(m, 4),
                    "intercept": round(b, 2)
                })

            return forecasts

        except Exception as e:
            logging.error(f"Linear regression hatasi: {e}")
            return []

    def _calculate_standard_error(self, years: List[int], values: List[float],
                                  slope: float, intercept: float) -> float:
        """Standard error hesapla"""
        if len(years) < 3:
            return 0.0

        residuals = []
        for x, y in zip(years, values):
            predicted = slope * x + intercept
            residuals.append((y - predicted) ** 2)

        mse = sum(residuals) / (len(residuals) - 2)
        return mse ** 0.5

    # =====================================================
    # 2. TIME SERIES TAHMİNİ (MOVING AVERAGE)
    # =====================================================

    def moving_average_forecast(self, historical_data: List[Dict],
                                window_size: int = 3,
                                forecast_years: int = 3) -> List[Dict]:
        """
        Moving average ile tahmin
        
        Args:
            historical_data: Tarihsel veri
            window_size: Hareketli ortalama pencere boyutu
            forecast_years: Tahmin yılı sayısı
        """
        if len(historical_data) < window_size:
            return []

        try:
            values = [d['value'] for d in historical_data]
            years = [d['year'] for d in historical_data]

            # Son window_size kadar değerin ortalaması
            last_values = values[-window_size:]
            avg_value = statistics.mean(last_values)

            # Trend eğilimini hesapla
            trend = (values[-1] - values[-window_size]) / window_size

            last_year = max(years)
            forecasts = []

            for i in range(1, forecast_years + 1):
                forecast_year = last_year + i
                # Moving average + trend
                forecast_value = avg_value + (trend * i)

                # Güven aralığı
                std_dev = statistics.stdev(last_values) if len(last_values) > 1 else 0
                confidence_margin = 1.96 * std_dev

                forecasts.append({
                    "year": forecast_year,
                    "forecast_value": round(forecast_value, 2),
                    "method": f"Moving Average ({window_size} yil)",
                    "confidence_lower": round(forecast_value - confidence_margin, 2),
                    "confidence_upper": round(forecast_value + confidence_margin, 2),
                    "trend": round(trend, 2)
                })

            return forecasts

        except Exception as e:
            logging.error(f"Moving average hatasi: {e}")
            return []

    # =====================================================
    # 3. EXPONENTIAL SMOOTHING TAHMİNİ
    # =====================================================

    def exponential_smoothing_forecast(self, historical_data: List[Dict],
                                      alpha: float = 0.3,
                                      forecast_years: int = 3) -> List[Dict]:
        """
        Exponential smoothing ile tahmin
        
        Args:
            historical_data: Tarihsel veri
            alpha: Smoothing parametresi (0-1)
            forecast_years: Tahmin yılı sayısı
        """
        if len(historical_data) < 2:
            return []

        try:
            values = [d['value'] for d in historical_data]
            years = [d['year'] for d in historical_data]

            # Exponential smoothing
            smoothed_values = [values[0]]
            for i in range(1, len(values)):
                smoothed = alpha * values[i] + (1 - alpha) * smoothed_values[-1]
                smoothed_values.append(smoothed)

            # Trend hesapla
            trend = (smoothed_values[-1] - smoothed_values[-2]) if len(smoothed_values) > 1 else 0

            last_year = max(years)
            forecasts = []

            current_forecast = smoothed_values[-1]
            for i in range(1, forecast_years + 1):
                forecast_year = last_year + i
                current_forecast = current_forecast + trend

                forecasts.append({
                    "year": forecast_year,
                    "forecast_value": round(current_forecast, 2),
                    "method": f"Exponential Smoothing (alpha={alpha})",
                    "trend": round(trend, 2)
                })

            return forecasts

        except Exception as e:
            logging.error(f"Exponential smoothing hatasi: {e}")
            return []

    # =====================================================
    # 4. HEDEF ERİŞİM TAHMİNİ
    # =====================================================

    def estimate_target_achievement(self, company_id: int, metric_code: str,
                                   current_value: float, target_value: float,
                                   target_year: int,
                                   historical_data: List[Dict]) -> Dict:
        """
        Hedef erişim tahmini
        
        Args:
            current_value: Mevcut değer
            target_value: Hedef değer
            target_year: Hedef yıl
            historical_data: Tarihsel performans
            
        Returns:
            Tahmin sonuçları
        """
        try:
            # Tarihsel trend hesapla
            if len(historical_data) >= 2:
                values = [d['value'] for d in historical_data]
                [d['year'] for d in historical_data]

                # Yıllık ortalama değişim
                changes = []
                for i in range(1, len(values)):
                    change = values[i] - values[i-1]
                    changes.append(change)

                avg_annual_change = statistics.mean(changes) if changes else 0
            else:
                avg_annual_change = 0

            # Hedef için gereken değişim
            current_year = datetime.now().year
            years_to_target = target_year - current_year
            required_total_change = target_value - current_value
            required_annual_change = required_total_change / years_to_target if years_to_target > 0 else 0

            # Tahmini erişim yılı
            if avg_annual_change != 0:
                estimated_years = required_total_change / avg_annual_change
                estimated_achievement_year = current_year + int(estimated_years)
            else:
                estimated_achievement_year = None

            # Başarı olasılığı
            if avg_annual_change != 0:
                achievement_ratio = required_annual_change / avg_annual_change
                if achievement_ratio <= 1:
                    probability = 90  # Mevcut tempo yeterli
                elif achievement_ratio <= 1.5:
                    probability = 70  # Biraz daha hızlanmalı
                elif achievement_ratio <= 2:
                    probability = 50  # Önemli iyileştirme gerekli
                else:
                    probability = 25  # Çok zor hedef
            else:
                probability = 10  # Tarihsel veri yetersiz

            # Risk seviyesi
            if probability >= 75:
                risk_level = "Dusuk"
            elif probability >= 50:
                risk_level = "Orta"
            else:
                risk_level = "Yuksek"

            # Öneriler
            recommendations = []
            if achievement_ratio > 1.2:
                recommendations.append(f"Yillik degisimi {required_annual_change:.2f}'e cikarmaniz gerekiyor")
            if probability < 70:
                recommendations.append("Hedefe ulasmak icin agresif aksiyonlar gerekli")
            if avg_annual_change < 0 and required_total_change > 0:
                recommendations.append("Mevcut trend hedefin tersi yonde, stratejinizi gozden gecirin")

            result = {
                "current_value": current_value,
                "target_value": target_value,
                "target_year": target_year,
                "current_year": current_year,
                "years_to_target": years_to_target,
                "required_total_change": round(required_total_change, 2),
                "required_annual_change": round(required_annual_change, 2),
                "historical_annual_change": round(avg_annual_change, 2),
                "estimated_achievement_year": estimated_achievement_year,
                "probability_of_achievement": probability,
                "risk_level": risk_level,
                "recommendations": recommendations
            }

            # Sonuçları kaydet
            self._save_target_forecast(company_id, metric_code, result)

            return result

        except Exception as e:
            logging.error(f"Hedef tahmini hatasi: {e}")
            return {}

    def _save_target_forecast(self, company_id: int, metric_code: str,
                             forecast_data: Dict) -> None:
        """Hedef tahminini kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO target_forecasts
                (company_id, metric_code, current_value, target_value, target_year,
                 estimated_achievement_year, probability_of_achievement, 
                 required_annual_change, risk_level, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, metric_code,
                forecast_data['current_value'], forecast_data['target_value'],
                forecast_data['target_year'], forecast_data.get('estimated_achievement_year'),
                forecast_data['probability_of_achievement'],
                forecast_data['required_annual_change'],
                forecast_data['risk_level'],
                json.dumps(forecast_data['recommendations'])
            ))

            conn.commit()

        except Exception as e:
            logging.error(f"Hedef tahmini kaydetme hatasi: {e}")
        finally:
            conn.close()

    # =====================================================
    # 5. WHAT-IF ANALİZİ
    # =====================================================

    def whatif_analysis(self, company_id: int, metric_code: str,
                       baseline_value: float, scenarios: List[Dict]) -> List[Dict]:
        """
        What-if analizi - Farklı senaryoları simüle et
        
        Args:
            baseline_value: Mevcut/baz değer
            scenarios: [{"name": "Optimistic", "change_pct": 20}, ...]
            
        Returns:
            Senaryo sonuçları
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        results = []

        try:
            for scenario in scenarios:
                scenario_name = scenario['name']
                change_pct = scenario['change_pct']

                # Yeni değer hesapla
                projected_value = baseline_value * (1 + change_pct / 100)

                # Etki analizi
                impact = self._analyze_scenario_impact(
                    baseline_value, projected_value, change_pct
                )

                result = {
                    "scenario_name": scenario_name,
                    "baseline_value": baseline_value,
                    "change_percentage": change_pct,
                    "projected_value": round(projected_value, 2),
                    "absolute_change": round(projected_value - baseline_value, 2),
                    "impact_analysis": impact
                }

                results.append(result)

                # Senaryoyu kaydet
                cursor.execute("""
                    INSERT INTO whatif_scenarios
                    (company_id, scenario_name, scenario_description, metric_code,
                     baseline_value, change_percentage, projected_value, impact_analysis)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id, scenario_name,
                    scenario.get('description', ''),
                    metric_code, baseline_value, change_pct,
                    projected_value, impact
                ))

            conn.commit()
            return results

        except Exception as e:
            logging.error(f"What-if analizi hatasi: {e}")
            return []
        finally:
            conn.close()

    def _analyze_scenario_impact(self, baseline: float, projected: float,
                                change_pct: float) -> str:
        """Senaryo etkisini analiz et"""
        if change_pct > 0:
            if change_pct > 30:
                return "Cok Buyuk Artis - Agresif hedef"
            elif change_pct > 15:
                return "Onemli Artis - Iddiali hedef"
            else:
                return "Ilimli Artis - Gercekci hedef"
        elif change_pct < 0:
            if change_pct < -30:
                return "Cok Buyuk Azalis - Agresif hedef"
            elif change_pct < -15:
                return "Onemli Azalis - Iddiali hedef"
            else:
                return "Ilimli Azalis - Gercekci hedef"
        else:
            return "Degisim Yok - Stabil senaryo"

    # =====================================================
    # 6. ÇOK YILLI TREND GRAFİKLERİ (5-10 YIL)
    # =====================================================

    def get_multiyear_trend(self, company_id: int, metric_code: str,
                           start_year: int = 2015, end_year: int = 2024) -> Dict:
        """
        Çok yıllı trend verisi (5-10 yıl)
        
        Returns:
            {
                "historical": [...],
                "trend_line": [...],
                "statistics": {...}
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT year, actual_value FROM trend_data
                WHERE company_id = ? AND metric_code = ?
                AND year BETWEEN ? AND ?
                ORDER BY year
            """, (company_id, metric_code, start_year, end_year))

            historical = []
            for row in cursor.fetchall():
                historical.append({
                    "year": row[0],
                    "value": row[1]
                })

            if not historical:
                return {"historical": [], "statistics": {}}

            # İstatistikler
            values = [h['value'] for h in historical]
            stats = {
                "min": min(values),
                "max": max(values),
                "average": statistics.mean(values),
                "median": statistics.median(values),
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "total_change": values[-1] - values[0] if len(values) > 1 else 0,
                "total_change_pct": ((values[-1] - values[0]) / values[0] * 100) if len(values) > 1 and values[0] != 0 else 0
            }

            # Trend çizgisi (linear regression)
            trend_forecasts = self.linear_regression_forecast(historical, 0)

            return {
                "historical": historical,
                "statistics": stats,
                "trend_info": trend_forecasts[0] if trend_forecasts else {}
            }

        except Exception as e:
            logging.error(f"Cok yilli trend hatasi: {e}")
            return {"historical": [], "statistics": {}}
        finally:
            conn.close()

    # =====================================================
    # 7. ENSEMBLE TAHMİN (BİRLEŞİK)
    # =====================================================

    def ensemble_forecast(self, historical_data: List[Dict],
                         forecast_years: int = 3) -> Dict:
        """
        Ensemble tahmin - Birden fazla yöntemi birleştir
        
        Returns:
            {
                "linear_regression": [...],
                "moving_average": [...],
                "exponential_smoothing": [...],
                "ensemble_average": [...]
            }
        """
        try:
            # Tüm yöntemleri uygula
            lr_forecast = self.linear_regression_forecast(historical_data, forecast_years)
            ma_forecast = self.moving_average_forecast(historical_data, 3, forecast_years)
            es_forecast = self.exponential_smoothing_forecast(historical_data, 0.3, forecast_years)

            # Ensemble ortalaması
            ensemble = []
            for i in range(forecast_years):
                lr_val = lr_forecast[i]['forecast_value'] if i < len(lr_forecast) else 0
                ma_val = ma_forecast[i]['forecast_value'] if i < len(ma_forecast) else 0
                es_val = es_forecast[i]['forecast_value'] if i < len(es_forecast) else 0

                # Ağırlıklı ortalama
                ensemble_val = (lr_val * 0.4 + ma_val * 0.3 + es_val * 0.3)

                year = historical_data[-1]['year'] + i + 1
                ensemble.append({
                    "year": year,
                    "forecast_value": round(ensemble_val, 2),
                    "method": "Ensemble (Weighted Average)"
                })

            return {
                "linear_regression": lr_forecast,
                "moving_average": ma_forecast,
                "exponential_smoothing": es_forecast,
                "ensemble_average": ensemble
            }

        except Exception as e:
            logging.error(f"Ensemble tahmin hatasi: {e}")
            return {}

    # =====================================================
    # 8. YARDIMCI FONKSİYONLAR
    # =====================================================

    def save_forecast(self, company_id: int, metric_code: str,
                     forecasts: List[Dict]) -> None:
        """Tahmin sonuçlarını kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for forecast in forecasts:
                cursor.execute("""
                    INSERT OR REPLACE INTO forecast_results
                    (company_id, metric_code, forecast_year, forecast_value,
                     forecast_method, confidence_interval_lower, confidence_interval_upper)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id, metric_code,
                    forecast['year'], forecast['forecast_value'],
                    forecast['method'],
                    forecast.get('confidence_lower'),
                    forecast.get('confidence_upper')
                ))

            conn.commit()

        except Exception as e:
            logging.error(f"Tahmin kaydetme hatasi: {e}")
        finally:
            conn.close()

    def get_forecast_accuracy(self, company_id: int, metric_code: str,
                             actual_year: int) -> Dict:
        """Tahmin doğruluğunu hesapla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Geçmiş tahminleri al
            cursor.execute("""
                SELECT forecast_value, forecast_method FROM forecast_results
                WHERE company_id = ? AND metric_code = ? AND forecast_year = ?
            """, (company_id, metric_code, actual_year))

            forecasts = cursor.fetchall()

            # Gerçek değeri al
            cursor.execute("""
                SELECT actual_value FROM trend_data
                WHERE company_id = ? AND metric_code = ? AND year = ?
            """, (company_id, metric_code, actual_year))

            actual_result = cursor.fetchone()
            if not actual_result or not forecasts:
                return {}

            actual_value = actual_result[0]

            # Her yöntem için doğruluk hesapla
            accuracies = []
            for forecast_val, method in forecasts:
                error = abs(actual_value - forecast_val)
                error_pct = (error / actual_value * 100) if actual_value != 0 else 100
                accuracy = max(0, 100 - error_pct)

                accuracies.append({
                    "method": method,
                    "forecast": forecast_val,
                    "actual": actual_value,
                    "error": round(error, 2),
                    "error_pct": round(error_pct, 1),
                    "accuracy": round(accuracy, 1)
                })

            return {
                "year": actual_year,
                "accuracies": accuracies,
                "best_method": max(accuracies, key=lambda x: x['accuracy'])['method'] if accuracies else None
            }

        except Exception as e:
            logging.error(f"Tahmin dogrulugu hesaplama hatasi: {e}")
            return {}
        finally:
            conn.close()
