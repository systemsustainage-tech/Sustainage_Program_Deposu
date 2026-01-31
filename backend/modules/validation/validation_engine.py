#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation Engine
Toplu validasyon ve kalite kontrol motoru
"""

import sqlite3
from typing import Dict, List

from .data_validator import ENVIRONMENTAL_CROSS_CHECKS, SOCIAL_CROSS_CHECKS, DataValidator


class ValidationEngine:
    """Toplu validasyon motoru"""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.validator = DataValidator(db_path)

    def validate_table(self, company_id: int, table_name: str,
                      field_validations: Dict[str, List] = None,
                      cross_checks: List[Dict] = None,
                      year_comparisons: List[Dict] = None) -> Dict:
        """
        Tüm tabloyu validate et
        
        Args:
            company_id: Şirket ID
            table_name: Tablo adı
            field_validations: Alan validasyonları {field: [rules]}
            cross_checks: Çapraz kontroller
            year_comparisons: Yıllık karşılaştırmalar
        
        Returns:
            Validasyon sonuç raporu
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabloyu oku
        cursor.execute(f"SELECT * FROM {table_name} WHERE company_id = ?", (company_id,))
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()

        total_errors = []
        total_warnings = []
        total_info = []

        for i, row in enumerate(rows):
            record = dict(zip(columns, row))
            record_id = record.get('id')

            # Alan validasyonları
            if field_validations:
                for field, rules in field_validations.items():
                    if field in record:
                        for rule in rules:
                            errors = self.validator.validate_field(field, record[field])

                            for error in errors:
                                if error['severity'] == 'error':
                                    total_errors.append(error)
                                elif error['severity'] == 'warning':
                                    total_warnings.append(error)
                                else:
                                    total_info.append(error)

                                # Log
                                self.validator.log_validation_result(
                                    company_id, table_name, record_id,
                                    field, error['rule_id'],
                                    error['severity'] != 'error',
                                    error['message']
                                )

            # Çapraz kontroller
            if cross_checks:
                cross_errors = self.validator.validate_cross_field(record, cross_checks)
                for error in cross_errors:
                    if error['severity'] == 'error':
                        total_errors.append(error)
                    elif error['severity'] == 'warning':
                        total_warnings.append(error)

            # Yıllık karşılaştırmalar
            if year_comparisons and 'year' in record:
                for comparison in year_comparisons:
                    field = comparison['field']
                    threshold = comparison.get('threshold', 50.0)

                    if field in record and record[field] is not None:
                        warnings = self.validator.compare_with_previous_year(
                            company_id, table_name, field,
                            float(record[field]), int(record['year']),
                            threshold
                        )
                        total_warnings.extend(warnings)

        # Kalite skoru hesapla
        quality_score = self.validator.calculate_quality_score(company_id, table_name)

        return {
            'table': table_name,
            'total_records': len(rows),
            'errors': len(total_errors),
            'warnings': len(total_warnings),
            'info': len(total_info),
            'quality_score': quality_score,
            'error_details': total_errors,
            'warning_details': total_warnings,
            'info_details': total_info
        }

    def validate_all_tables(self, company_id: int) -> Dict:
        """Tüm tabloları validate et"""
        results = []

        # Çevresel tablolar
        env_result = self.validate_table(
            company_id,
            'environmental_metrics',
            cross_checks=ENVIRONMENTAL_CROSS_CHECKS,
            year_comparisons=[
                {'field': 'value', 'threshold': 30.0}
            ]
        )
        results.append(env_result)

        # Sosyal tablolar
        social_result = self.validate_table(
            company_id,
            'social_metrics',
            cross_checks=SOCIAL_CROSS_CHECKS,
            year_comparisons=[
                {'field': 'value', 'threshold': 25.0}
            ]
        )
        results.append(social_result)

        # Genel özet
        total_errors = sum(r['errors'] for r in results)
        total_warnings = sum(r['warnings'] for r in results)
        avg_quality = sum(r['quality_score'] for r in results) / len(results) if results else 0

        return {
            'summary': {
                'total_tables': len(results),
                'total_errors': total_errors,
                'total_warnings': total_warnings,
                'average_quality_score': avg_quality
            },
            'table_results': results
        }

