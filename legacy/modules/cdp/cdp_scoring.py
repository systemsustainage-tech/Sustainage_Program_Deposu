#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CDP Scoring System
CDP A-D seviyeli scoring sistemi
"""

from enum import Enum
from typing import Dict, List
from utils.language_manager import LanguageManager


class CDPGrade(Enum):
    """CDP Grade seviyeleri"""
    A = "A"  # 90-100%
    B = "B"  # 70-89%
    C = "C"  # 50-69%
    D = "D"  # 0-49%

class CDPScoringSystem:
    """CDP Scoring sistemi"""

    def __init__(self):
        self.grade_thresholds = {
            CDPGrade.A: 90.0,
            CDPGrade.B: 70.0,
            CDPGrade.C: 50.0,
            CDPGrade.D: 0.0
        }

        # CDP scoring kategorileri ve ağırlıkları
        self.category_weights = {
            "Climate Change": {
                "Governance": 0.25,
                "Strategy": 0.25,
                "Risk Management": 0.25,
                "Metrics and Targets": 0.25
            },
            "Water Security": {
                "Governance": 0.25,
                "Strategy": 0.25,
                "Risk Management": 0.25,
                "Metrics and Targets": 0.25
            },
            "Forests": {
                "Governance": 0.25,
                "Strategy": 0.25,
                "Risk Management": 0.25,
                "Metrics and Targets": 0.25
            }
        }

    def calculate_grade(self, score: float) -> CDPGrade:
        """Skora göre CDP grade hesapla"""
        if score >= self.grade_thresholds[CDPGrade.A]:
            return CDPGrade.A
        elif score >= self.grade_thresholds[CDPGrade.B]:
            return CDPGrade.B
        elif score >= self.grade_thresholds[CDPGrade.C]:
            return CDPGrade.C
        else:
            return CDPGrade.D

    def calculate_category_score(self, responses: List[Dict], category: str) -> float:
        """Kategori bazında skor hesapla"""
        category_responses = [r for r in responses if r.get('question_category') == category]

        if not category_responses:
            return 0.0

        total_weight = sum(r.get('scoring_weight', 1.0) for r in category_responses)
        answered_weight = sum(
            r.get('scoring_weight', 1.0) for r in category_responses
            if r.get('response', '').strip()
        )

        return (answered_weight / total_weight * 100) if total_weight > 0 else 0.0

    def calculate_weighted_score(self, questionnaire_type: str, responses: List[Dict]) -> Dict:
        """Ağırlıklı skor hesapla"""
        if questionnaire_type not in self.category_weights:
            return {"total_score": 0.0, "grade": "D", "category_scores": {}}

        category_weights = self.category_weights[questionnaire_type]
        category_scores = {}
        weighted_total = 0.0

        for category, weight in category_weights.items():
            category_score = self.calculate_category_score(responses, category)
            category_scores[category] = {
                "score": category_score,
                "weight": weight,
                "weighted_score": category_score * weight
            }
            weighted_total += category_score * weight

        grade = self.calculate_grade(weighted_total)

        return {
            "total_score": weighted_total,
            "grade": grade.value,
            "category_scores": category_scores,
            "completion_rate": self.calculate_completion_rate(responses)
        }

    def calculate_completion_rate(self, responses: List[Dict]) -> float:
        """Tamamlanma oranını hesapla"""
        if not responses:
            return 0.0

        total_questions = len(responses)
        answered_questions = len([r for r in responses if r.get('response', '').strip()])

        return (answered_questions / total_questions * 100) if total_questions > 0 else 0.0

    def get_grade_description(self, grade: str) -> str:
        """Grade açıklaması"""
        descriptions = {
            "A": "Leadership Level - Excellent disclosure and performance",
            "B": "Management Level - Good disclosure and performance",
            "C": "Awareness Level - Basic disclosure and performance",
            "D": "Disclosure Level - Limited disclosure and performance"
        }
        return descriptions.get(grade, "Unknown grade")

    def get_improvement_recommendations(self, questionnaire_type: str,
                                      category_scores: Dict) -> List[str]:
        """İyileştirme önerileri"""
        recommendations = []

        for category, data in category_scores.items():
            score = data.get('score', 0)
            if score < 50:
                recommendations.append(f"Improve {category} disclosure and management")
            elif score < 70:
                recommendations.append(f"Enhance {category} practices and reporting")
            elif score < 90:
                recommendations.append(f"Strengthen {category} leadership and innovation")

        return recommendations

    def calculate_benchmark_score(self, company_scores: Dict,
                                 industry_average: Dict) -> Dict:
        """Benchmark skorları hesapla"""
        benchmark = {}

        for questionnaire_type, scores in company_scores.items():
            if questionnaire_type in industry_average:
                company_score = scores.get('total_score', 0)
                industry_score = industry_average[questionnaire_type].get('average_score', 0)

                benchmark[questionnaire_type] = {
                    "company_score": company_score,
                    "industry_average": industry_score,
                    "performance_vs_industry": company_score - industry_score,
                    "performance_level": self._get_performance_level(company_score, industry_score)
                }

        return benchmark

    def _get_performance_level(self, company_score: float, industry_score: float) -> str:
        """Performans seviyesi belirle"""
        diff = company_score - industry_score

        if diff >= 20:
            return self.lm.tr('perf_significantly_above', "Significantly Above Average")
        elif diff >= 10:
            return self.lm.tr('perf_above', "Above Average")
        elif diff >= -10:
            return self.lm.tr('perf_average', "Average")
        elif diff >= -20:
            return self.lm.tr('perf_below', "Below Average")
        else:
            return self.lm.tr('perf_significantly_below', "Significantly Below Average")

    def generate_scoring_report(self, questionnaire_type: str,
                              scoring_data: Dict) -> str:
        """Scoring raporu oluştur"""
        report = f"{self.lm.tr('cdp_scoring_report_title', 'CDP {questionnaire_type} Scoring Report').format(questionnaire_type=questionnaire_type)}\n"
        report += "=" * 50 + "\n\n"

        # Genel skor
        total_score = scoring_data.get('total_score', 0)
        grade = scoring_data.get('grade', 'D')
        completion_rate = scoring_data.get('completion_rate', 0)

        report += f"{self.lm.tr('overall_score', 'Overall Score')}: {total_score:.1f}%\n"
        report += f"{self.lm.tr('cdp_grade', 'CDP Grade')}: {grade}\n"
        report += f"{self.lm.tr('grade_description', 'Grade Description')}: {self.get_grade_description(grade)}\n"
        report += f"{self.lm.tr('completion_rate', 'Completion Rate')}: {completion_rate:.1f}%\n\n"

        # Kategori skorları
        category_scores = scoring_data.get('category_scores', {})
        if category_scores:
            report += f"{self.lm.tr('category_scores', 'Category Scores')}:\n"
            report += "-" * 30 + "\n"

            for category, data in category_scores.items():
                score = data.get('score', 0)
                weight = data.get('weight', 0)
                weighted_score = data.get('weighted_score', 0)

                report += f"{category}:\n"
                report += f"  {self.lm.tr('score', 'Score')}: {score:.1f}%\n"
                report += f"  {self.lm.tr('weight', 'Weight')}: {weight:.2f}\n"
                report += f"  {self.lm.tr('weighted_score', 'Weighted Score')}: {weighted_score:.1f}\n\n"

        # İyileştirme önerileri
        recommendations = self.get_improvement_recommendations(questionnaire_type, category_scores)
        if recommendations:
            report += f"{self.lm.tr('improvement_recommendations', 'Improvement Recommendations')}:\n"
            report += "-" * 30 + "\n"
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"

        return report
