#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNGC Benchmark Module
Compare performance with industry benchmarks
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional

from modules.ungc.ungc_manager_enhanced import UNGCManagerEnhanced
from config.database import DB_PATH


class UNGCBenchmark:
    """Benchmark UNGC performance"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.manager = UNGCManagerEnhanced(db_path)

        # Industry benchmarks (average scores)
        self.industry_benchmarks = {
            'Technology': {
                'overall': 65.0,
                'Human Rights': 70.0,
                'Labour': 68.0,
                'Environment': 62.0,
                'Anti-Corruption': 75.0
            },
            'Manufacturing': {
                'overall': 58.0,
                'Human Rights': 55.0,
                'Labour': 62.0,
                'Environment': 56.0,
                'Anti-Corruption': 60.0
            },
            'Finance': {
                'overall': 72.0,
                'Human Rights': 75.0,
                'Labour': 78.0,
                'Environment': 60.0,
                'Anti-Corruption': 85.0
            },
            'Retail': {
                'overall': 60.0,
                'Human Rights': 58.0,
                'Labour': 65.0,
                'Environment': 55.0,
                'Anti-Corruption': 62.0
            },
            'Healthcare': {
                'overall': 68.0,
                'Human Rights': 72.0,
                'Labour': 70.0,
                'Environment': 60.0,
                'Anti-Corruption': 70.0
            },
            'Default': {
                'overall': 62.0,
                'Human Rights': 63.0,
                'Labour': 65.0,
                'Environment': 58.0,
                'Anti-Corruption': 68.0
            }
        }

    def compare_with_industry(self, company_id: int, industry: str = 'Default',
                            period: Optional[str] = None) -> Dict:
        """
        Compare company performance with industry benchmark
        
        Args:
            company_id: Company ID
            industry: Industry sector
            period: Reporting period
            
        Returns:
            Comparison data
        """
        if period is None:
            period = str(datetime.now().year)

        # Get company scores
        company_data = self.manager.calculate_overall_score(company_id, period)

        # Get benchmark
        benchmark = self.industry_benchmarks.get(industry, self.industry_benchmarks['Default'])

        # Compare
        comparison = {
            'company_id': company_id,
            'industry': industry,
            'period': period,
            'company_overall': company_data['overall_score'],
            'benchmark_overall': benchmark['overall'],
            'difference_overall': company_data['overall_score'] - benchmark['overall'],
            'categories': {}
        }

        # Category comparison
        for category, company_score in company_data['category_scores'].items():
            benchmark_score = benchmark.get(category, 60.0)
            comparison['categories'][category] = {
                'company_score': company_score,
                'benchmark_score': benchmark_score,
                'difference': company_score - benchmark_score,
                'performance': 'Above' if company_score > benchmark_score else 'Below' if company_score < benchmark_score else 'At'
            }

        # Overall performance level
        if comparison['difference_overall'] > 10:
            comparison['performance_level'] = 'Industry Leader'
        elif comparison['difference_overall'] > 0:
            comparison['performance_level'] = 'Above Average'
        elif comparison['difference_overall'] > -10:
            comparison['performance_level'] = 'Average'
        else:
            comparison['performance_level'] = 'Below Average'

        return comparison

    def get_improvement_recommendations(self, comparison: Dict) -> List[Dict]:
        """
        Get recommendations based on benchmark comparison
        
        Args:
            comparison: Comparison data from compare_with_industry
            
        Returns:
            List of recommendations
        """
        recommendations = []

        # Check each category
        for category, data in comparison['categories'].items():
            if data['difference'] < 0:  # Below benchmark
                gap = abs(data['difference'])
                priority = 'High' if gap > 15 else 'Medium' if gap > 5 else 'Low'

                recommendations.append({
                    'category': category,
                    'gap': gap,
                    'priority': priority,
                    'recommendation': f"Focus on improving {category} practices. Current gap: {gap:.1f}%"
                })

        # Sort by gap (highest priority first)
        recommendations.sort(key=lambda x: x['gap'], reverse=True)

        return recommendations

    def compare_progress_over_time(self, company_id: int, start_period: str,
                                  end_period: str, industry: str = 'Default') -> Dict:
        """
        Compare progress over time against industry benchmark
        
        Args:
            company_id: Company ID
            start_period: Start period
            end_period: End period
            industry: Industry sector
            
        Returns:
            Progress comparison
        """
        # Get company progress
        progress = self.manager.track_progress(company_id, start_period, end_period)

        # Get benchmarks
        benchmark = self.industry_benchmarks.get(industry, self.industry_benchmarks['Default'])

        return {
            'company_id': company_id,
            'period': f"{start_period} to {end_period}",
            'company_improvement': progress['overall_improvement'],
            'start_vs_benchmark': progress['start_score'] - benchmark['overall'],
            'end_vs_benchmark': progress['end_score'] - benchmark['overall'],
            'progress_summary': f"Improved by {progress['overall_improvement']:.1f}% ({progress['start_score']:.1f}% → {progress['end_score']:.1f}%)",
            'benchmark_position': 'Above' if progress['end_score'] > benchmark['overall'] else 'Below'
        }


if __name__ == '__main__':
    # Test
    import sys
    db = sys.argv[1] if len(sys.argv) > 1 else DB_PATH

    benchmark = UNGCBenchmark(db)

    # Compare with industry
    comparison = benchmark.compare_with_industry(company_id=1, industry='Technology')
    logging.info("Benchmark Comparison:")
    logging.info(f"  Overall: {comparison['company_overall']:.1f}% vs {comparison['benchmark_overall']:.1f}%")
    logging.info(f"  Performance: {comparison['performance_level']}")

    # Get recommendations
    recs = benchmark.get_improvement_recommendations(comparison)
    logging.info("\nRecommendations:")
    for rec in recs:
        logging.info(f"  [{rec['priority']}] {rec['recommendation']}")

