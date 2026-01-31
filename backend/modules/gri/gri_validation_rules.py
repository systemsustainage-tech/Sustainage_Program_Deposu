#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GRI Validation Rules - Sprint 2
Birim tipleri, pozitif/negatif sınırlar, yüzde aralığı kontrolleri
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict
from config.database import DB_PATH


class GRIValidationRules:
    """GRI doğrulama kuralları sınıfı"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        # db_path göreli ise proje köküne göre mutlak hale getir
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path

    def get_connection(self) -> None:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_validation_rules(self) -> None:
        """Temel doğrulama kurallarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            logging.info("GRI Validation Rules oluşturuluyor...")

            # 1. Birim tipi doğrulama kuralları
            unit_validation_rules = [
                # Text birimler için
                ('unit_type_text', 'unit_type', 'unit IN ("Text", "Number", "Currency", "Percentage", "Ratio")', 'Yüksek', 'Geçersiz birim tipi'),

                # Currency birimler için pozitif değer kontrolü
                ('currency_positive', 'currency_positive', 'unit = "Currency" AND numerical_value >= 0', 'Yüksek', 'Para birimi negatif olamaz'),

                # Percentage birimler için 0-100 aralık kontrolü
                ('percentage_range', 'percentage_range', 'unit = "Percentage" AND numerical_value BETWEEN 0 AND 100', 'Yüksek', 'Yüzde değeri 0-100 arasında olmalı'),

                # Number birimler için pozitif kontrol (enerji, emisyon vb.)
                ('energy_positive', 'energy_positive', 'unit IN ("MWh", "tCO2e", "Ton", "m³", "kg") AND numerical_value >= 0', 'Yüksek', 'Enerji/emisyon değerleri negatif olamaz'),

                # Ratio birimler için pozitif kontrol
                ('ratio_positive', 'ratio_positive', 'unit = "Ratio" AND numerical_value >= 0', 'Orta', 'Oran değerleri negatif olamaz'),

                # GRI Core vs Comprehensive uyumluluk
                ('core_comprehensive', 'core_comprehensive', 'reporting_requirement IN ("Core", "Comprehensive")', 'Yüksek', 'GRI Core/Comprehensive uyumluluk kontrolü'),

                # Zorunlu alan kontrolü
                ('mandatory_fields', 'mandatory_fields', 'unit IS NOT NULL AND methodology IS NOT NULL', 'Kritik', 'Birim ve metodoloji zorunlu alanlar'),

                # Metodoloji uzunluk kontrolü
                ('methodology_length', 'methodology_length', 'LENGTH(methodology) >= 10', 'Orta', 'Metodoloji en az 10 karakter olmalı'),

                # Kanıt URL kontrolü
                ('evidence_url_format', 'evidence_url_format', 'evidence_url LIKE "http%" OR evidence_url IS NULL', 'Orta', 'Kanıt URL geçerli format olmalı'),

                # Dönem format kontrolü
                ('period_format', 'period_format', 'period LIKE "20__"', 'Yüksek', 'Dönem YYYY formatında olmalı'),

                # Stakeholder group kontrolü
                ('stakeholder_group', 'stakeholder_group', 'stakeholder_group IN ("Employees", "Customers", "Investors", "Community", "Government", "NGOs", "Suppliers") OR stakeholder_group IS NULL', 'Düşük', 'Geçersiz paydaş grubu'),

                # Impact area kontrolü
                ('impact_area', 'impact_area', 'impact_area IN ("Environmental", "Social", "Economic", "Governance") OR impact_area IS NULL', 'Düşük', 'Geçersiz etki alanı'),
            ]

            for rule_name, rule_type, rule_expression, severity, message in unit_validation_rules:
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_validation_rules 
                    (indicator_id, rule_type, rule_expression, severity, message, created_at)
                    VALUES (NULL, ?, ?, ?, ?, ?)
                """, (rule_type, rule_expression, severity, message, datetime.now().isoformat()))

            # 2. Metodoloji doğrulama kuralları
            methodology_rules = [
                ('methodology_required', 'methodology_required', 'methodology IS NOT NULL AND methodology != ""', 'Yüksek', 'Metodoloji belirtilmelidir'),
                ('methodology_format', 'methodology_format', 'methodology LIKE "%GRI%" OR methodology LIKE "%ISO%" OR methodology LIKE "%GHG%"', 'Orta', 'Standart metodoloji kullanılmalıdır'),
            ]

            for rule_name, rule_type, rule_expression, severity, message in methodology_rules:
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_validation_rules 
                    (indicator_id, rule_type, rule_expression, severity, message, created_at)
                    VALUES (NULL, ?, ?, ?, ?, ?)
                """, (rule_type, rule_expression, severity, message, datetime.now().isoformat()))

            # 3. Raporlama gereksinimi kuralları
            reporting_rules = [
                ('reporting_requirement', 'reporting_requirement', 'reporting_requirement IN ("Zorunlu", "Önerilen", "İsteğe Bağlı")', 'Yüksek', 'Geçersiz raporlama gereksinimi'),
                ('requirement_level', 'requirement_level', 'requirement_level IN ("Yüksek", "Orta", "Düşük")', 'Orta', 'Geçersiz gereksinim seviyesi'),
            ]

            for rule_name, rule_type, rule_expression, severity, message in reporting_rules:
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_validation_rules 
                    (indicator_id, rule_type, rule_expression, severity, message, created_at)
                    VALUES (NULL, ?, ?, ?, ?, ?)
                """, (rule_type, rule_expression, severity, message, datetime.now().isoformat()))

            # 4. Veri kalitesi kuralları
            quality_rules = [
                ('data_quality_level', 'data_quality_level', 'data_quality IN ("Yüksek", "Orta", "Düşük")', 'Orta', 'Geçersiz veri kalitesi seviyesi'),
                ('audit_required', 'audit_required', 'audit_required IN ("Evet", "Hayır")', 'Orta', 'Denetim gereksinimi Evet/Hayır olmalı'),
                ('validation_required', 'validation_required', 'validation_required IN ("Evet", "Hayır")', 'Orta', 'Validasyon gereksinimi Evet/Hayır olmalı'),
            ]

            for rule_name, rule_type, rule_expression, severity, message in quality_rules:
                cursor.execute("""
                    INSERT OR REPLACE INTO gri_validation_rules 
                    (indicator_id, rule_type, rule_expression, severity, message, created_at)
                    VALUES (NULL, ?, ?, ?, ?, ?)
                """, (rule_type, rule_expression, severity, message, datetime.now().isoformat()))

            # 5. Özel gösterge kuralları (indicator-specific)
            self.create_indicator_specific_rules(cursor)

            conn.commit()
            logging.info("Validation rules başarıyla oluşturuldu!")
            return True

        except Exception as e:
            logging.error(f"Validation rules oluşturma hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def create_indicator_specific_rules(self, cursor) -> None:
        """Gösterge özel doğrulama kuralları"""

        # GRI 2-7: Çalışan sayısı pozitif olmalı
        cursor.execute("SELECT id FROM gri_indicators WHERE code = '2-7'")
        result = cursor.fetchone()
        if result:
            indicator_id = result[0]
            cursor.execute("""
                INSERT OR REPLACE INTO gri_validation_rules 
                (indicator_id, rule_type, rule_expression, severity, message, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (indicator_id, 'positive_value', 'numerical_value > 0', 'Kritik', 'Çalışan sayısı pozitif olmalı', datetime.now().isoformat()))

        # GRI 201-1: Gelir pozitif olmalı
        cursor.execute("SELECT id FROM gri_indicators WHERE code = '201-1'")
        result = cursor.fetchone()
        if result:
            indicator_id = result[0]
            cursor.execute("""
                INSERT OR REPLACE INTO gri_validation_rules 
                (indicator_id, rule_type, rule_expression, severity, message, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (indicator_id, 'positive_value', 'numerical_value > 0', 'Kritik', 'Gelir pozitif olmalı', datetime.now().isoformat()))

        # GRI 302-1: Enerji tüketimi pozitif olmalı
        cursor.execute("SELECT id FROM gri_indicators WHERE code = '302-1'")
        result = cursor.fetchone()
        if result:
            indicator_id = result[0]
            cursor.execute("""
                INSERT OR REPLACE INTO gri_validation_rules 
                (indicator_id, rule_type, rule_expression, severity, message, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (indicator_id, 'positive_value', 'numerical_value > 0', 'Yüksek', 'Enerji tüketimi pozitif olmalı', datetime.now().isoformat()))

        # GRI 305-1: Emisyon pozitif olmalı
        cursor.execute("SELECT id FROM gri_indicators WHERE code = '305-1'")
        result = cursor.fetchone()
        if result:
            indicator_id = result[0]
            cursor.execute("""
                INSERT OR REPLACE INTO gri_validation_rules 
                (indicator_id, rule_type, rule_expression, severity, message, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (indicator_id, 'positive_value', 'numerical_value >= 0', 'Yüksek', 'Emisyon değeri negatif olamaz', datetime.now().isoformat()))

    def validate_indicator_response(self, indicator_id: int, response_value: str, numerical_value: float, unit: str) -> Dict:
        """Gösterge yanıtını doğrula"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'score': 100
            }

            # Genel kuralları kontrol et
            cursor.execute("""
                SELECT rule_type, rule_expression, severity, message
                FROM gri_validation_rules
                WHERE indicator_id IS NULL
            """)

            general_rules = cursor.fetchall()

            for rule_type, rule_expression, severity, message in general_rules:
                if not self.evaluate_rule(rule_expression, response_value, numerical_value, unit):
                    validation_result['is_valid'] = False
                    error_info = {
                        'rule_type': rule_type,
                        'message': message,
                        'severity': severity
                    }

                    if severity == 'Kritik':
                        validation_result['errors'].append(error_info)
                        validation_result['score'] -= 20
                    elif severity == 'Yüksek':
                        validation_result['errors'].append(error_info)
                        validation_result['score'] -= 15
                    elif severity == 'Orta':
                        validation_result['warnings'].append(error_info)
                        validation_result['score'] -= 10
                    else:
                        validation_result['warnings'].append(error_info)
                        validation_result['score'] -= 5

            # Gösterge özel kuralları kontrol et
            cursor.execute("""
                SELECT rule_type, rule_expression, severity, message
                FROM gri_validation_rules
                WHERE indicator_id = ?
            """, (indicator_id,))

            specific_rules = cursor.fetchall()

            for rule_type, rule_expression, severity, message in specific_rules:
                if not self.evaluate_rule(rule_expression, response_value, numerical_value, unit):
                    validation_result['is_valid'] = False
                    error_info = {
                        'rule_type': rule_type,
                        'message': message,
                        'severity': severity
                    }

                    if severity == 'Kritik':
                        validation_result['errors'].append(error_info)
                        validation_result['score'] -= 20
                    elif severity == 'Yüksek':
                        validation_result['errors'].append(error_info)
                        validation_result['score'] -= 15
                    elif severity == 'Orta':
                        validation_result['warnings'].append(error_info)
                        validation_result['score'] -= 10
                    else:
                        validation_result['warnings'].append(error_info)
                        validation_result['score'] -= 5

            return validation_result

        except Exception as e:
            logging.error(f"Validation hatası: {e}")
            return {
                'is_valid': False,
                'errors': [{'rule_type': 'system_error', 'message': f'Validation hatası: {e}', 'severity': 'Kritik'}],
                'warnings': [],
                'score': 0
            }
        finally:
            conn.close()

    def evaluate_rule(self, rule_expression: str, response_value: str, numerical_value: float, unit: str) -> bool:
        """Kural ifadesini değerlendir"""
        try:
            # Basit kural değerlendirme
            # Bu gerçek uygulamada daha gelişmiş bir rule engine olmalı

            if 'numerical_value >= 0' in rule_expression:
                return numerical_value >= 0
            elif 'numerical_value > 0' in rule_expression:
                return numerical_value > 0
            elif 'numerical_value BETWEEN 0 AND 100' in rule_expression:
                return 0 <= numerical_value <= 100
            elif 'unit IN' in rule_expression:
                valid_units = ['Text', 'Number', 'Currency', 'Percentage', 'Ratio', 'MWh', 'tCO2e', 'Ton', 'm³', 'kg']
                return unit in valid_units
            elif 'unit = "Currency"' in rule_expression:
                return unit == 'Currency'
            elif 'unit = "Percentage"' in rule_expression:
                return unit == 'Percentage'
            elif 'unit = "Ratio"' in rule_expression:
                return unit == 'Ratio'
            elif 'unit IN ("MWh", "tCO2e", "Ton", "m³", "kg")' in rule_expression:
                return unit in ['MWh', 'tCO2e', 'Ton', 'm³', 'kg']
            elif 'methodology IS NOT NULL' in rule_expression:
                return response_value is not None and response_value != ''
            else:
                return True  # Bilinmeyen kurallar için varsayılan olarak geçerli

        except Exception as e:
            logging.error(f"Rule evaluation hatası: {e}")
            return True

    def get_validation_summary(self) -> Dict:
        """Doğrulama özetini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Toplam kural sayısı
            cursor.execute("SELECT COUNT(*) FROM gri_validation_rules")
            total_rules = cursor.fetchone()[0]

            # Kural türlerine göre dağılım
            cursor.execute("""
                SELECT rule_type, COUNT(*) 
                FROM gri_validation_rules 
                GROUP BY rule_type
            """)
            rule_types = dict(cursor.fetchall())

            # Severity'ye göre dağılım
            cursor.execute("""
                SELECT severity, COUNT(*) 
                FROM gri_validation_rules 
                GROUP BY severity
            """)
            severity_dist = dict(cursor.fetchall())

            return {
                'total_rules': total_rules,
                'rule_types': rule_types,
                'severity_distribution': severity_dist
            }

        except Exception as e:
            logging.error(f"Validation summary hatası: {e}")
            return {}
        finally:
            conn.close()

def create_gri_validation_rules() -> None:
    """GRI validation rules oluştur"""
    validator = GRIValidationRules()
    return validator.create_validation_rules()

if __name__ == "__main__":
    create_gri_validation_rules()
