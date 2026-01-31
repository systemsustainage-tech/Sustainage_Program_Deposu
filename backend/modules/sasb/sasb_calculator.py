#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SASB Calculator - SASB hesaplama ve analiz sınıfı
- Finansal materiality hesaplamaları
- Sektör karşılaştırmaları
- Trend analizleri
- Performans skorları
"""

import logging
import sqlite3
from typing import Any, Dict, Optional

import pandas as pd


class SASBCalculator:
    """SASB hesaplama ve analiz sınıfı"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def calculate_materiality_score(self, company_id: int, sector_id: int,
                                  year: Optional[int] = None) -> Dict[str, Any]:
        """Finansal materiality skorunu hesapla"""
        try:
            conn = sqlite3.connect(self.db_path)

            # Sektöre özgü topics'leri al
            query = """
                SELECT id, topic_code, topic_name, category, is_material
                FROM sasb_disclosure_topics
                WHERE sector_id = ?
            """
            topics_df = pd.read_sql_query(query, conn, params=(sector_id,))

            if topics_df.empty:
                conn.close()
                return {}

            # Year handling
            if not year:
                latest_year_query = """
                    SELECT MAX(year) as max_year
                    FROM sasb_metric_responses
                    WHERE company_id = ?
                """
                latest_year = pd.read_sql_query(latest_year_query, conn, params=(company_id,))
                if latest_year.empty or latest_year.iloc[0]['max_year'] is None:
                    year = 2024 # Default
                else:
                    year = latest_year.iloc[0]['max_year']

            # Disclosure verilerini al
            disclosure_query = """
                SELECT r.metric_id, r.response_value, r.numerical_value,
                       m.metric_code, m.disclosure_topic_id
                FROM sasb_metric_responses r
                JOIN sasb_metrics m ON r.metric_id = m.id
                WHERE r.company_id = ? AND r.year = ?
            """
            disclosures_df = pd.read_sql_query(disclosure_query, conn, params=(company_id, year))
            conn.close()

            # Hesaplamalar
            total_topics = len(topics_df)
            material_topics = len(topics_df[topics_df['is_material'] == 1])

            # Disclose edilen topics (en az bir metriği doldurulmuş topicler)
            disclosed_topic_ids = set()
            if not disclosures_df.empty:
                disclosed_topic_ids = set(disclosures_df['disclosure_topic_id'].unique())
            
            disclosed_count = len(disclosed_topic_ids)

            # Material topics'lerden disclose edilenler
            material_topic_ids = set(topics_df[topics_df['is_material'] == 1]['id'])
            disclosed_material = len(disclosed_topic_ids.intersection(material_topic_ids))

            # Skorlar
            disclosure_rate = (disclosed_count / total_topics * 100) if total_topics > 0 else 0
            materiality_rate = (disclosed_material / material_topics * 100) if material_topics > 0 else 0

            # Genel skor (ağırlıklı)
            overall_score = ((disclosure_rate * 0.4) + (materiality_rate * 0.6))

            # Kategori (Boyut) bazında skorlar
            dimension_scores = {}
            if 'category' in topics_df.columns:
                for category in topics_df['category'].unique():
                    if not category:
                        continue
                    
                    cat_topics = topics_df[topics_df['category'] == category]
                    cat_material = len(cat_topics[cat_topics['is_material'] == 1])
                    cat_ids = set(cat_topics['id'])
                    
                    cat_disclosed = len(disclosed_topic_ids.intersection(cat_ids))
                    cat_disclosed_material = len(disclosed_topic_ids.intersection(cat_ids).intersection(material_topic_ids))

                    cat_score = 0
                    if len(cat_topics) > 0:
                        cat_score = (cat_disclosed / len(cat_topics)) * 100

                    dimension_scores[category] = {
                        'total_topics': len(cat_topics),
                        'material_topics': cat_material,
                        'disclosed_topics': cat_disclosed,
                        'disclosed_material': cat_disclosed_material,
                        'score': cat_score
                    }

            return {
                'year': year,
                'total_topics': total_topics,
                'material_topics': material_topics,
                'disclosed_topics': disclosed_count,
                'disclosed_material_topics': disclosed_material,
                'disclosure_rate': disclosure_rate,
                'materiality_rate': materiality_rate,
                'overall_score': overall_score,
                'dimension_scores': dimension_scores,
                'grade': self._calculate_grade(overall_score)
            }

        except Exception as e:
            self.logger.error(f"Materiality skoru hesaplanamadı: {e}")
            return {}

    def _calculate_grade(self, score: float) -> str:
        """Skora göre harf notu hesapla"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C+"
        elif score >= 40:
            return "C"
        elif score >= 30:
            return "D"
        else:
            return "F"

    def calculate_sector_comparison(self, company_id: int, sector_id: int,
                                  year: int) -> Dict[str, Any]:
        """Sektör karşılaştırması"""
        try:
            # Şirket skoru
            company_score_data = self.calculate_materiality_score(company_id, sector_id, year)
            company_score = company_score_data.get('overall_score', 0)

            # Sektör ortalaması (Basitçe veritabanındaki diğer şirketlerin ortalaması)
            # Gerçek senaryoda daha karmaşık olabilir
            conn = sqlite3.connect(self.db_path)
            query = """
                SELECT DISTINCT company_id
                FROM company_sasb_data
                WHERE sector_id = ? AND year = ? AND company_id != ?
            """
            cursor = conn.cursor()
            cursor.execute(query, (sector_id, year, company_id))
            other_companies = [row[0] for row in cursor.fetchall()]
            conn.close()

            total_score = 0
            count = 0
            for other_id in other_companies:
                score_data = self.calculate_materiality_score(other_id, sector_id, year)
                if score_data:
                    total_score += score_data.get('overall_score', 0)
                    count += 1
            
            sector_average = (total_score / count) if count > 0 else company_score # Eğer başka şirket yoksa kendisi

            return {
                'company_score': company_score,
                'sector_average': sector_average,
                'difference': company_score - sector_average
            }
        except Exception as e:
            self.logger.error(f"Sektör karşılaştırması hatası: {e}")
            return {}

    def calculate_trend_analysis(self, company_id: int, sector_id: int,
                               years: list) -> Dict[str, Any]:
        """Trend analizi"""
        try:
            scores = []
            for year in sorted(years):
                score_data = self.calculate_materiality_score(company_id, sector_id, year)
                scores.append(score_data.get('overall_score', 0))
            
            trend_direction = "flat"
            if len(scores) >= 2:
                if scores[-1] > scores[0]:
                    trend_direction = "up"
                elif scores[-1] < scores[0]:
                    trend_direction = "down"

            return {
                'years': sorted(years),
                'scores': scores,
                'trend_direction': trend_direction
            }
        except Exception as e:
            self.logger.error(f"Trend analizi hatası: {e}")
            return {}

    def calculate_risk_assessment(self, company_id: int, sector_id: int,
                                year: int) -> Dict[str, Any]:
        """Risk değerlendirmesi"""
        try:
            # Basit risk hesabı: Düşük disclosure = Yüksek risk
            score_data = self.calculate_materiality_score(company_id, sector_id, year)
            overall_score = score_data.get('overall_score', 0)
            
            risk_score = 100 - overall_score
            
            risk_level = "Low"
            if risk_score > 75:
                risk_level = "High"
            elif risk_score > 50:
                risk_level = "Medium"
                
            return {
                'overall_risk_score': risk_score,
                'risk_level': risk_level,
                'category_scores': {} # Detaylandırılabilir
            }
        except Exception as e:
            self.logger.error(f"Risk değerlendirmesi hatası: {e}")
            return {}
