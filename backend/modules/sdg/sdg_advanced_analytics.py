#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG Gelişmiş Analitik Sistemi
Hedef bazında ilerleme hesaplama, gösterge detayları takibi, trend analizi, performans metrikleri
"""

import logging
import os
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
from config.database import DB_PATH


class SDGAdvancedAnalytics:
    """SDG Gelişmiş Analitik Sistemi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.db_path = os.path.join(base_dir, db_path)
        else:
            self.db_path = db_path

        self._create_advanced_tables()

    def _create_advanced_tables(self) -> None:
        """Gelişmiş analitik tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # SDG hedef performans skorları
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_goal_performance_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                performance_score REAL NOT NULL,
                improvement_rate REAL DEFAULT 0.0,
                benchmark_score REAL,
                industry_average REAL,
                measurement_date TEXT NOT NULL,
                calculation_method TEXT DEFAULT 'weighted_average',
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # SDG gösterge detaylı analizi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_indicator_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                indicator_code TEXT NOT NULL,
                indicator_title TEXT NOT NULL,
                completion_score REAL DEFAULT 0.0,
                quality_score REAL DEFAULT 0.0,
                timeliness_score REAL DEFAULT 0.0,
                consistency_score REAL DEFAULT 0.0,
                overall_score REAL DEFAULT 0.0,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                trend_direction TEXT DEFAULT 'stable',
                risk_level TEXT DEFAULT 'low',
                priority_level TEXT DEFAULT 'medium',
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # SDG trend analizi detayları
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_trend_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                analysis_period TEXT NOT NULL,
                trend_type TEXT NOT NULL,
                trend_strength REAL NOT NULL,
                trend_direction TEXT NOT NULL,
                confidence_level REAL NOT NULL,
                forecast_value REAL,
                forecast_date TEXT,
                analysis_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # SDG performans metrikleri detayları
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_performance_metrics_detailed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                metric_category TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                target_value REAL,
                actual_vs_target REAL,
                improvement_rate REAL,
                benchmark_value REAL,
                industry_percentile REAL,
                measurement_date TEXT NOT NULL,
                sdg_no INTEGER,
                indicator_code TEXT,
                calculation_method TEXT,
                data_source TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # SDG risk analizi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sdg_risk_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                sdg_no INTEGER NOT NULL,
                risk_type TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                risk_score REAL NOT NULL,
                risk_description TEXT,
                mitigation_strategy TEXT,
                impact_assessment TEXT,
                probability_assessment TEXT,
                analysis_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        conn.commit()
        conn.close()
        logging.info("SDG gelişmiş analitik tabloları oluşturuldu")

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def calculate_goal_performance_score(self, company_id: int, sdg_no: int) -> Dict:
        """SDG hedef performans skorunu hesapla"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Gösterge durumlarını al
            cursor.execute("""
                SELECT indicator_code, answered_questions, total_questions, 
                       completion_percentage, last_updated
                FROM sdg_indicator_status 
                WHERE company_id = ? AND sdg_no = ?
            """, (company_id, sdg_no))

            indicators = cursor.fetchall()

            if not indicators:
                return {
                    'sdg_no': sdg_no,
                    'performance_score': 0.0,
                    'improvement_rate': 0.0,
                    'benchmark_score': 0.0,
                    'industry_average': 0.0,
                    'calculation_method': 'weighted_average',
                    'indicators_analyzed': 0
                }

            # Performans skorunu hesapla
            total_score = 0.0
            total_weight = 0.0
            improvement_rates = []

            for indicator in indicators:
                completion = indicator[3] or 0.0
                answered = indicator[1] or 0
                total = indicator[2] or 3

                # Ağırlıklı skor hesaplama
                weight = 1.0  # Varsayılan ağırlık
                if total > 0:
                    weight = total / 3.0  # Soru sayısına göre ağırlık

                score = (completion / 100.0) * weight
                total_score += score
                total_weight += weight

                # İyileşme oranını hesapla (basit hesaplama)
                if answered > 0:
                    improvement_rate = (answered / total) * 100
                    improvement_rates.append(improvement_rate)

            # Genel performans skoru
            performance_score = (total_score / total_weight * 100) if total_weight > 0 else 0.0

            # İyileşme oranı
            avg_improvement = np.mean(improvement_rates) if improvement_rates else 0.0

            # Benchmark skorları (örnek değerler)
            benchmark_score = 75.0  # Sektör ortalaması
            industry_average = 70.0  # Endüstri ortalaması

            result = {
                'sdg_no': sdg_no,
                'performance_score': round(performance_score, 2),
                'improvement_rate': round(avg_improvement, 2),
                'benchmark_score': benchmark_score,
                'industry_average': industry_average,
                'calculation_method': 'weighted_average',
                'indicators_analyzed': len(indicators)
            }

            # Veritabanına kaydet
            self._save_goal_performance_score(company_id, result)

            return result

        except Exception as e:
            logging.error(f"SDG hedef performans skoru hesaplanırken hata: {e}")
            return {
                'sdg_no': sdg_no,
                'performance_score': 0.0,
                'improvement_rate': 0.0,
                'benchmark_score': 0.0,
                'industry_average': 0.0,
                'calculation_method': 'weighted_average',
                'indicators_analyzed': 0
            }
        finally:
            conn.close()

    def _save_goal_performance_score(self, company_id: int, score_data: Dict) -> None:
        """Hedef performans skorunu kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sdg_goal_performance_scores 
                (company_id, sdg_no, performance_score, improvement_rate, 
                 benchmark_score, industry_average, measurement_date, calculation_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, score_data['sdg_no'], score_data['performance_score'],
                score_data['improvement_rate'], score_data['benchmark_score'],
                score_data['industry_average'], datetime.now().isoformat(),
                score_data['calculation_method']
            ))

            conn.commit()

        except Exception as e:
            logging.error(f"Hedef performans skoru kaydedilirken hata: {e}")
        finally:
            conn.close()

    def analyze_indicator_details(self, company_id: int, sdg_no: int) -> List[Dict]:
        """Gösterge detaylarını analiz et"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Gösterge durumlarını al
            cursor.execute("""
                SELECT indicator_code, indicator_title, answered_questions, 
                       total_questions, completion_percentage, last_updated
                FROM sdg_indicator_status 
                WHERE company_id = ? AND sdg_no = ?
            """, (company_id, sdg_no))

            indicators = cursor.fetchall()

            analytics_results = []

            for indicator in indicators:
                indicator_code = indicator[0]
                indicator_title = indicator[1]
                answered = indicator[2] or 0
                total = indicator[3] or 3
                completion = indicator[4] or 0.0
                last_updated = indicator[5]

                # Detaylı skorları hesapla
                completion_score = completion
                quality_score = self._calculate_quality_score(answered, total)
                timeliness_score = self._calculate_timeliness_score(last_updated)
                consistency_score = self._calculate_consistency_score(company_id, indicator_code)

                # Genel skor
                overall_score = (completion_score + quality_score + timeliness_score + consistency_score) / 4

                # Trend yönü
                trend_direction = self._determine_trend_direction(company_id, indicator_code)

                # Risk seviyesi
                risk_level = self._assess_risk_level(overall_score, completion)

                # Öncelik seviyesi
                priority_level = self._assess_priority_level(overall_score, completion)

                result = {
                    'indicator_code': indicator_code,
                    'indicator_title': indicator_title,
                    'completion_score': round(completion_score, 2),
                    'quality_score': round(quality_score, 2),
                    'timeliness_score': round(timeliness_score, 2),
                    'consistency_score': round(consistency_score, 2),
                    'overall_score': round(overall_score, 2),
                    'trend_direction': trend_direction,
                    'risk_level': risk_level,
                    'priority_level': priority_level,
                    'answered_questions': answered,
                    'total_questions': total,
                    'completion_percentage': completion
                }

                analytics_results.append(result)

                # Veritabanına kaydet
                self._save_indicator_analytics(company_id, sdg_no, result)

            return analytics_results

        except Exception as e:
            logging.error(f"Gösterge detayları analiz edilirken hata: {e}")
            return []
        finally:
            conn.close()

    def _calculate_quality_score(self, answered: int, total: int) -> float:
        """Kalite skorunu hesapla"""
        if total == 0:
            return 0.0

        # Temel kalite metrikleri
        completion_ratio = answered / total

        # Kalite skoru: tamamlanma oranı * 100
        quality_score = completion_ratio * 100

        # Ek kalite faktörleri (örnek)
        if completion_ratio == 1.0:
            quality_score += 10  # Tamamlanmış gösterge bonusu

        return min(quality_score, 100.0)

    def _calculate_timeliness_score(self, last_updated: str) -> float:
        """Zamanında güncelleme skorunu hesapla"""
        if not last_updated:
            return 0.0

        try:
            last_update = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            days_since_update = (datetime.now() - last_update).days

            # Zamanında güncelleme skoru
            if days_since_update <= 7:
                return 100.0
            elif days_since_update <= 30:
                return 80.0
            elif days_since_update <= 90:
                return 60.0
            else:
                return 40.0

        except Exception:
            return 50.0  # Varsayılan skor

    def _calculate_consistency_score(self, company_id: int, indicator_code: str) -> float:
        """Tutarlılık skorunu hesapla"""
        # Basit tutarlılık hesaplama
        # Gerçek uygulamada daha karmaşık algoritmalar kullanılabilir
        return 75.0  # Varsayılan skor

    def _determine_trend_direction(self, company_id: int, indicator_code: str) -> str:
        """Trend yönünü belirle"""
        # Basit trend analizi
        # Gerçek uygulamada geçmiş veriler analiz edilir
        return "stable"  # Varsayılan trend

    def _assess_risk_level(self, overall_score: float, completion: float) -> str:
        """Risk seviyesini değerlendir"""
        if overall_score >= 80 and completion >= 80:
            return "low"
        elif overall_score >= 60 and completion >= 60:
            return "medium"
        else:
            return "high"

    def _assess_priority_level(self, overall_score: float, completion: float) -> str:
        """Öncelik seviyesini değerlendir"""
        if overall_score < 40 or completion < 40:
            return "high"
        elif overall_score < 70 or completion < 70:
            return "medium"
        else:
            return "low"

    def _save_indicator_analytics(self, company_id: int, sdg_no: int, analytics_data: Dict) -> None:
        """Gösterge analitik verilerini kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO sdg_indicator_analytics 
                (company_id, sdg_no, indicator_code, indicator_title, completion_score,
                 quality_score, timeliness_score, consistency_score, overall_score,
                 trend_direction, risk_level, priority_level, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                company_id, sdg_no, analytics_data['indicator_code'],
                analytics_data['indicator_title'], analytics_data['completion_score'],
                analytics_data['quality_score'], analytics_data['timeliness_score'],
                analytics_data['consistency_score'], analytics_data['overall_score'],
                analytics_data['trend_direction'], analytics_data['risk_level'],
                analytics_data['priority_level']
            ))

            conn.commit()

        except Exception as e:
            logging.error(f"Gösterge analitik verileri kaydedilirken hata: {e}")
        finally:
            conn.close()

    def perform_trend_analysis(self, company_id: int, sdg_no: int, days: int = 30) -> Dict:
        """Trend analizi yap"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Geçmiş verileri al
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            cursor.execute("""
                SELECT measurement_date, completion_percentage, answered_questions, total_questions
                FROM sdg_progress_trends 
                WHERE company_id = ? AND sdg_no = ? 
                AND measurement_date >= ? AND measurement_date <= ?
                ORDER BY measurement_date
            """, (company_id, sdg_no, start_date.isoformat(), end_date.isoformat()))

            trend_data = cursor.fetchall()

            if len(trend_data) < 2:
                return {
                    'trend_type': 'insufficient_data',
                    'trend_strength': 0.0,
                    'trend_direction': 'stable',
                    'confidence_level': 0.0,
                    'forecast_value': None,
                    'data_points': len(trend_data)
                }

            # Trend analizi
            [row[0] for row in trend_data]
            completions = [row[1] for row in trend_data]

            # Basit lineer regresyon
            x = np.arange(len(completions))
            y = np.array(completions)

            # Trend yönü ve gücü
            if len(y) > 1:
                slope = np.polyfit(x, y, 1)[0]
                trend_strength = abs(slope)

                if slope > 0.5:
                    trend_direction = "improving"
                elif slope < -0.5:
                    trend_direction = "declining"
                else:
                    trend_direction = "stable"
            else:
                trend_strength = 0.0
                trend_direction = "stable"

            # Güven seviyesi
            confidence_level = min(100.0, len(trend_data) * 10)  # Basit hesaplama

            # Tahmin değeri
            forecast_value = None
            if len(completions) >= 3:
                # Basit tahmin: son 3 değerin ortalaması
                forecast_value = np.mean(completions[-3:])

            result = {
                'trend_type': 'linear',
                'trend_strength': round(trend_strength, 2),
                'trend_direction': trend_direction,
                'confidence_level': round(confidence_level, 2),
                'forecast_value': round(forecast_value, 2) if forecast_value else None,
                'data_points': len(trend_data),
                'analysis_period': f"{days} days"
            }

            # Veritabanına kaydet
            self._save_trend_analysis(company_id, sdg_no, result)

            return result

        except Exception as e:
            logging.error(f"Trend analizi yapılırken hata: {e}")
            return {
                'trend_type': 'error',
                'trend_strength': 0.0,
                'trend_direction': 'stable',
                'confidence_level': 0.0,
                'forecast_value': None,
                'data_points': 0
            }
        finally:
            conn.close()

    def _save_trend_analysis(self, company_id: int, sdg_no: int, trend_data: Dict) -> None:
        """Trend analizi sonuçlarını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sdg_trend_analysis 
                (company_id, sdg_no, analysis_period, trend_type, trend_strength,
                 trend_direction, confidence_level, forecast_value, analysis_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, sdg_no, trend_data['analysis_period'],
                trend_data['trend_type'], trend_data['trend_strength'],
                trend_data['trend_direction'], trend_data['confidence_level'],
                trend_data['forecast_value'], datetime.now().isoformat()
            ))

            conn.commit()

        except Exception as e:
            logging.error(f"Trend analizi kaydedilirken hata: {e}")
        finally:
            conn.close()

    def get_performance_metrics_analysis(self, company_id: int, sdg_no: Optional[int] = None) -> Dict:
        """Performans metrikleri analizi"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Metrikleri al
            if sdg_no:
                cursor.execute("""
                    SELECT metric_category, metric_name, metric_value, target_value,
                           actual_vs_target, improvement_rate, measurement_date
                    FROM sdg_performance_metrics_detailed 
                    WHERE company_id = ? AND sdg_no = ?
                    ORDER BY measurement_date DESC
                """, (company_id, sdg_no))
            else:
                cursor.execute("""
                    SELECT metric_category, metric_name, metric_value, target_value,
                           actual_vs_target, improvement_rate, measurement_date
                    FROM sdg_performance_metrics_detailed 
                    WHERE company_id = ?
                    ORDER BY measurement_date DESC
                """, (company_id,))

            metrics = cursor.fetchall()

            if not metrics:
                return {
                    'total_metrics': 0,
                    'categories': {},
                    'top_performers': [],
                    'underperformers': [],
                    'average_performance': 0.0
                }

            # Kategorilere göre analiz
            categories = defaultdict(list)
            all_scores = []

            for metric in metrics:
                category = metric[0]
                name = metric[1]
                value = metric[2]
                target = metric[3]
                vs_target = metric[4]
                improvement = metric[5]

                categories[category].append({
                    'name': name,
                    'value': value,
                    'target': target,
                    'vs_target': vs_target,
                    'improvement': improvement
                })

                if vs_target is not None:
                    all_scores.append(vs_target)

            # En iyi ve en kötü performanslar
            sorted_metrics = sorted(metrics, key=lambda x: x[4] or 0, reverse=True)
            top_performers = sorted_metrics[:5]
            underperformers = sorted_metrics[-5:]

            # Ortalama performans
            avg_performance = np.mean(all_scores) if all_scores else 0.0

            result = {
                'total_metrics': len(metrics),
                'categories': dict(categories),
                'top_performers': [
                    {
                        'name': m[1],
                        'category': m[0],
                        'value': m[2],
                        'vs_target': m[4]
                    } for m in top_performers
                ],
                'underperformers': [
                    {
                        'name': m[1],
                        'category': m[0],
                        'value': m[2],
                        'vs_target': m[4]
                    } for m in underperformers
                ],
                'average_performance': round(avg_performance, 2)
            }

            return result

        except Exception as e:
            logging.error(f"Performans metrikleri analiz edilirken hata: {e}")
            return {
                'total_metrics': 0,
                'categories': {},
                'top_performers': [],
                'underperformers': [],
                'average_performance': 0.0
            }
        finally:
            conn.close()

    def perform_risk_analysis(self, company_id: int, sdg_no: int) -> List[Dict]:
        """Risk analizi yap"""
        try:
            # Gösterge analitik verilerini al
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT indicator_code, indicator_title, overall_score, 
                       risk_level, priority_level, completion_score
                FROM sdg_indicator_analytics 
                WHERE company_id = ? AND sdg_no = ?
            """, (company_id, sdg_no))

            indicators = cursor.fetchall()

            risks = []

            for indicator in indicators:
                indicator_code = indicator[0]
                indicator_title = indicator[1]
                overall_score = indicator[2]
                risk_level = indicator[3]
                indicator[4]
                completion_score = indicator[5]

                # Risk değerlendirmesi
                if risk_level == "high":
                    risk_type = "completion_risk"
                    risk_score = 100 - completion_score
                    risk_description = f"Gösterge {indicator_code} tamamlanma riski yüksek"
                    mitigation_strategy = "Acil eylem planı oluşturulmalı"
                elif risk_level == "medium":
                    risk_type = "performance_risk"
                    risk_score = 100 - overall_score
                    risk_description = f"Gösterge {indicator_code} performans riski orta"
                    mitigation_strategy = "İyileştirme planı uygulanmalı"
                else:
                    risk_type = "monitoring_risk"
                    risk_score = 50
                    risk_description = f"Gösterge {indicator_code} izleme gerektiriyor"
                    mitigation_strategy = "Düzenli takip yapılmalı"

                risk = {
                    'indicator_code': indicator_code,
                    'indicator_title': indicator_title,
                    'risk_type': risk_type,
                    'risk_level': risk_level,
                    'risk_score': round(risk_score, 2),
                    'risk_description': risk_description,
                    'mitigation_strategy': mitigation_strategy,
                    'impact_assessment': f"SDG {sdg_no} hedefine etki: {risk_level}",
                    'probability_assessment': f"Olasılık: {risk_level}"
                }

                risks.append(risk)

            # Risk analizi sonuçlarını kaydet
            self._save_risk_analysis(company_id, sdg_no, risks)

            return risks

        except Exception as e:
            logging.error(f"Risk analizi yapılırken hata: {e}")
            return []

    def _save_risk_analysis(self, company_id: int, sdg_no: int, risks: List[Dict]) -> None:
        """Risk analizi sonuçlarını kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            for risk in risks:
                cursor.execute("""
                    INSERT INTO sdg_risk_analysis 
                    (company_id, sdg_no, risk_type, risk_level, risk_score,
                     risk_description, mitigation_strategy, impact_assessment,
                     probability_assessment, analysis_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id, sdg_no, risk['risk_type'], risk['risk_level'],
                    risk['risk_score'], risk['risk_description'],
                    risk['mitigation_strategy'], risk['impact_assessment'],
                    risk['probability_assessment'], datetime.now().isoformat()
                ))

            conn.commit()

        except Exception as e:
            logging.error(f"Risk analizi kaydedilirken hata: {e}")
        finally:
            conn.close()

    def _save_performance_metric_detailed(self, company_id: int, category: str, metric_name: str,
                                        metric_value: float, metric_unit: Optional[str], target_value: Optional[float],
                                        actual_vs_target: Optional[float], improvement_rate: float,
                                        benchmark_value: Optional[float], industry_percentile: float,
                                        sdg_no: Optional[int], indicator_code: Optional[str], method: Optional[str],
                                        data_source: Optional[str]) -> bool:
        """Detaylı performans metriği kaydet"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO sdg_performance_metrics_detailed 
                (company_id, metric_category, metric_name, metric_value, metric_unit,
                 target_value, actual_vs_target, improvement_rate, benchmark_value,
                 industry_percentile, measurement_date, sdg_no, indicator_code,
                 calculation_method, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, category, metric_name, metric_value, metric_unit,
                target_value, actual_vs_target, improvement_rate, benchmark_value,
                industry_percentile, datetime.now().isoformat(), sdg_no, indicator_code,
                method, data_source
            ))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Detaylı performans metriği kaydedilirken hata: {e}")
            return False
        finally:
            conn.close()

    def get_comprehensive_analysis(self, company_id: int, sdg_no: int) -> Dict:
        """Kapsamlı analiz raporu"""
        try:
            # Tüm analizleri birleştir
            performance_score = self.calculate_goal_performance_score(company_id, sdg_no)
            indicator_analytics = self.analyze_indicator_details(company_id, sdg_no)
            trend_analysis = self.perform_trend_analysis(company_id, sdg_no)
            metrics_analysis = self.get_performance_metrics_analysis(company_id, sdg_no)
            risk_analysis = self.perform_risk_analysis(company_id, sdg_no)

            # Genel değerlendirme
            overall_score = performance_score['performance_score']
            risk_count = len([r for r in risk_analysis if r['risk_level'] == 'high'])

            if overall_score >= 80 and risk_count == 0:
                overall_status = "excellent"
            elif overall_score >= 60 and risk_count <= 2:
                overall_status = "good"
            elif overall_score >= 40 and risk_count <= 5:
                overall_status = "fair"
            else:
                overall_status = "needs_improvement"

            return {
                'sdg_no': sdg_no,
                'overall_status': overall_status,
                'overall_score': overall_score,
                'performance_analysis': performance_score,
                'indicator_analytics': indicator_analytics,
                'trend_analysis': trend_analysis,
                'metrics_analysis': metrics_analysis,
                'risk_analysis': risk_analysis,
                'analysis_date': datetime.now().isoformat(),
                'recommendations': self._generate_recommendations(overall_status, risk_analysis)
            }

        except Exception as e:
            logging.error(f"Kapsamlı analiz yapılırken hata: {e}")
            return {
                'sdg_no': sdg_no,
                'overall_status': 'error',
                'overall_score': 0.0,
                'error': str(e)
            }

    def _generate_recommendations(self, status: str, risks: List[Dict]) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []

        if status == "needs_improvement":
            recommendations.append("Acil eylem planı oluşturulmalı")
            recommendations.append("Kaynak tahsisi artırılmalı")
            recommendations.append("Haftalık takip toplantıları düzenlenmeli")
        elif status == "fair":
            recommendations.append("İyileştirme planı uygulanmalı")
            recommendations.append("Aylık değerlendirme yapılmalı")
        elif status == "good":
            recommendations.append("Mevcut performans korunmalı")
            recommendations.append("İyileştirme fırsatları değerlendirilmeli")
        else:  # excellent
            recommendations.append("Mükemmel performans sürdürülmeli")
            recommendations.append("Diğer SDG'lere örnek olarak paylaşılmalı")

        # Risk bazlı öneriler
        high_risks = [r for r in risks if r['risk_level'] == 'high']
        if high_risks:
            recommendations.append(f"{len(high_risks)} yüksek riskli gösterge için acil müdahale gerekli")

        return recommendations

if __name__ == "__main__":
    # Test
    analytics = SDGAdvancedAnalytics()
    logging.info("SDG Gelişmiş Analitik Sistemi başlatıldı")

    # Test analizi
    analysis = analytics.get_comprehensive_analysis(1, 9)
    logging.info(f"SDG 9 kapsamlı analizi: {analysis['overall_status']}")
