#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Veri Validasyonu
Mantık kuralları, çapraz kontroller, yıllık karşılaştırma
"""

import logging
import re
import sqlite3
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple


class ValidationRule:
    """Tek bir validasyon kuralı"""

    def __init__(self, rule_id: str, name: str, rule_type: str,
                 validation_fn: Callable, error_message: str,
                 severity: str = 'error'):
        """
        Args:
            rule_id: Kural ID
            name: Kural adı
            rule_type: Kural tipi (range, logic, format, cross_check, trend)
            validation_fn: Validasyon fonksiyonu
            error_message: Hata mesajı şablonu
            severity: Önem derecesi (error, warning, info)
        """
        self.rule_id = rule_id
        self.name = name
        self.rule_type = rule_type
        self.validation_fn = validation_fn
        self.error_message = error_message
        self.severity = severity

    def validate(self, value: Any, context: Dict = None) -> Tuple[bool, str]:
        """
        Validasyon yap
        
        Args:
            value: Kontrol edilecek değer
            context: Ek bilgiler (diğer alanlar, geçmiş veriler vb.)
        
        Returns:
            (geçerli_mi, hata_mesajı)
        """
        try:
            result = self.validation_fn(value, context)

            if result:
                return True, ""
            else:
                return False, self.error_message.format(value=value, **context if context else {})

        except Exception as e:
            return False, f"Validasyon hatası: {e}"


class DataValidator:
    """Veri validasyon sistemi"""

    def __init__(self, db_path: str) -> None:
        """
        Args:
            db_path: Veritabanı yolu
        """
        self.db_path = db_path
        self.rules = {}  # {field_name: [ValidationRule, ...]}
        self._init_database()
        self._load_default_rules()

    def _init_database(self) -> None:
        """Veritabanı tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Validasyon kuralları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE NOT NULL,
                field_name TEXT NOT NULL,
                rule_name TEXT NOT NULL,
                rule_type TEXT NOT NULL,
                rule_config TEXT,
                error_message TEXT,
                severity TEXT DEFAULT 'error',
                is_active INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        # Validasyon sonuçları tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                field_name TEXT NOT NULL,
                rule_id TEXT NOT NULL,
                validation_status TEXT NOT NULL,
                error_message TEXT,
                validated_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        # Veri kalite skoru tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_quality_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                table_name TEXT NOT NULL,
                quality_score REAL DEFAULT 0,
                total_records INTEGER DEFAULT 0,
                valid_records INTEGER DEFAULT 0,
                warning_records INTEGER DEFAULT 0,
                error_records INTEGER DEFAULT 0,
                calculated_at TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(id)
            )
        """)

        conn.commit()
        conn.close()

    def _load_default_rules(self) -> None:
        """Varsayılan validasyon kurallarını yükle"""
        # Sayısal aralık kuralları
        self.add_rule('numeric_positive', 'value',
                     ValidationRule(
                         'numeric_positive',
                         'Pozitif Sayı',
                         'range',
                         lambda v, c: v is None or (isinstance(v, (int, float)) and v >= 0),
                         "Değer negatif olamaz: {value}",
                         'error'
                     ))

        self.add_rule('percentage', 'value',
                     ValidationRule(
                         'percentage',
                         'Yüzde Değeri',
                         'range',
                         lambda v, c: v is None or (isinstance(v, (int, float)) and 0 <= v <= 100),
                         "Yüzde değeri 0-100 arasında olmalı: {value}",
                         'error'
                     ))

        # Format kuralları
        self.add_rule('email_format', 'email',
                     ValidationRule(
                         'email_format',
                         'Email Formatı',
                         'format',
                         lambda v, c: v is None or re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', str(v)) is not None,
                         "Geçersiz email formatı: {value}",
                         'error'
                     ))

        self.add_rule('date_format', 'date',
                     ValidationRule(
                         'date_format',
                         'Tarih Formatı',
                         'format',
                         lambda v, c: self._validate_date_format(v),
                         "Geçersiz tarih formatı: {value}. YYYY-MM-DD formatında olmalı",
                         'error'
                     ))

        # Mantık kuralları
        self.add_rule('future_date_warning', 'date',
                     ValidationRule(
                         'future_date_warning',
                         'Gelecek Tarih Uyarısı',
                         'logic',
                         lambda v, c: self._check_future_date(v),
                         "Tarih gelecekte: {value}",
                         'warning'
                     ))

        # GRI özel kuralları
        self.add_rule('gri_code_format', 'indicator_code',
                     ValidationRule(
                         'gri_code_format',
                         'GRI Kod Formatı',
                         'format',
                         lambda v, c: v is None or re.match(r'^GRI\s*\d+-\d+', str(v)) is not None,
                         "Geçersiz GRI kod formatı: {value}. Örnek: GRI 302-1",
                         'error'
                     ))

    def _validate_date_format(self, value: Any) -> bool:
        """Tarih formatını kontrol et"""
        if value is None:
            return True

        try:
            datetime.strptime(str(value), '%Y-%m-%d')
            return True
        except Exception:
            return False

    def _check_future_date(self, value: Any) -> bool:
        """Gelecek tarih kontrolü"""
        if value is None:
            return True

        try:
            date = datetime.strptime(str(value), '%Y-%m-%d')
            return date <= datetime.now()
        except Exception:
            return True

    def add_rule(self, rule_id: str, field_name: str, rule: ValidationRule) -> None:
        """
        Validasyon kuralı ekle
        
        Args:
            rule_id: Kural ID
            field_name: Alan adı
            rule: ValidationRule objesi
        """
        if field_name not in self.rules:
            self.rules[field_name] = []

        self.rules[field_name].append(rule)

    def validate_field(self, field_name: str, value: Any,
                      context: Optional[Dict] = None) -> List[Dict]:
        """
        Tek bir alanı validate et
        
        Args:
            field_name: Alan adı
            value: Değer
            context: Ek bilgiler
        
        Returns:
            Hata listesi [{severity, message, rule_id}]
        """
        errors = []

        if field_name in self.rules:
            for rule in self.rules[field_name]:
                is_valid, error_msg = rule.validate(value, context)

                if not is_valid:
                    errors.append({
                        'field': field_name,
                        'severity': rule.severity,
                        'message': error_msg,
                        'rule_id': rule.rule_id
                    })

        return errors

    def validate_record(self, data: Dict, context: Optional[Dict] = None) -> Tuple[bool, List[Dict]]:
        """
        Tüm kaydı validate et
        
        Args:
            data: Veri dictionary'si
            context: Ek bilgiler
        
        Returns:
            (geçerli_mi, hata_listesi)
        """
        all_errors = []

        for field_name, value in data.items():
            field_errors = self.validate_field(field_name, value, context)
            all_errors.extend(field_errors)

        # Sadece error seviyesindeki hatalar geçerliliği etkiler
        has_errors = any(e['severity'] == 'error' for e in all_errors)

        return (not has_errors, all_errors)

    def validate_cross_field(self, data: Dict, rules: List[Dict]) -> List[Dict]:
        """
        Çapraz alan validasyonu
        
        Args:
            data: Veri dictionary'si
            rules: Çapraz kontrol kuralları
                [{'fields': ['field1', 'field2'], 'check': lambda f1, f2: f1 > f2, 'message': '...'}]
        
        Returns:
            Hata listesi
        """
        errors = []

        for rule in rules:
            fields = rule['fields']
            check_fn = rule['check']
            message = rule['message']

            # Alan değerlerini al
            values = [data.get(field) for field in fields]

            # Hiçbiri None değilse kontrol et
            if all(v is not None for v in values):
                try:
                    if not check_fn(*values):
                        errors.append({
                            'fields': fields,
                            'severity': rule.get('severity', 'error'),
                            'message': message,
                            'rule_id': rule.get('rule_id', 'cross_field_check')
                        })
                except Exception as e:
                    errors.append({
                        'fields': fields,
                        'severity': 'error',
                        'message': f"Çapraz kontrol hatası: {e}",
                        'rule_id': 'cross_field_error'
                    })

        return errors

    def compare_with_previous_year(self, company_id: int, table_name: str,
                                   field_name: str, current_value: float,
                                   current_year: int,
                                   threshold_percent: float = 50.0) -> List[Dict]:
        """
        Önceki yıl ile karşılaştır
        
        Args:
            company_id: Şirket ID
            table_name: Tablo adı
            field_name: Alan adı
            current_value: Mevcut değer
            current_year: Mevcut yıl
            threshold_percent: Uyarı eşik yüzdesi
        
        Returns:
            Uyarı listesi
        """
        warnings = []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Önceki yılın verisini al
            query = f"""
                SELECT {field_name}
                FROM {table_name}
                WHERE company_id = ? AND year = ?
                AND {field_name} IS NOT NULL
                LIMIT 1
            """

            cursor.execute(query, (company_id, current_year - 1))
            result = cursor.fetchone()
            conn.close()

            if result and result[0]:
                previous_value = float(result[0])

                if previous_value == 0:
                    if current_value > 0:
                        warnings.append({
                            'field': field_name,
                            'severity': 'warning',
                            'message': f"{field_name}: Önceki yıl 0 iken şimdi {current_value}. Kontrol edin.",
                            'rule_id': 'year_comparison'
                        })
                else:
                    change_percent = abs((current_value - previous_value) / previous_value * 100)

                    if change_percent > threshold_percent:
                        direction = "artış" if current_value > previous_value else "azalış"
                        warnings.append({
                            'field': field_name,
                            'severity': 'warning',
                            'message': f"{field_name}: Önceki yıla göre %{change_percent:.1f} {direction}. " +
                                      f"({previous_value} → {current_value}). Veriyi kontrol edin.",
                            'rule_id': 'year_comparison'
                        })

        except Exception as e:
            warnings.append({
                'field': field_name,
                'severity': 'info',
                'message': f"Yıllık karşılaştırma yapılamadı: {e}",
                'rule_id': 'year_comparison_error'
            })

        return warnings

    def log_validation_result(self, company_id: int, table_name: str,
                             record_id: int, field_name: str,
                             rule_id: str, is_valid: bool,
                             error_message: str = "") -> None:
        """Validasyon sonucunu logla"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO validation_results
                (company_id, table_name, record_id, field_name, rule_id, 
                 validation_status, error_message, validated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                table_name,
                record_id,
                field_name,
                rule_id,
                'valid' if is_valid else 'invalid',
                error_message,
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logging.info(f"Validasyon logu yazılamadı: {e}")

    def calculate_quality_score(self, company_id: int, table_name: str) -> float:
        """
        Veri kalite skoru hesapla (0-100)
        
        Args:
            company_id: Şirket ID
            table_name: Tablo adı
        
        Returns:
            Kalite skoru (0-100)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Validasyon sonuçlarını al
            cursor.execute("""
                SELECT validation_status, COUNT(*) as count
                FROM validation_results
                WHERE company_id = ? AND table_name = ?
                GROUP BY validation_status
            """, (company_id, table_name))

            results = {row[0]: row[1] for row in cursor.fetchall()}

            total = sum(results.values())
            if total == 0:
                conn.close()
                return 100.0  # Veri yoksa %100

            valid = results.get('valid', 0)

            # Basit skor: Geçerli kayıtların yüzdesi
            score = (valid / total) * 100

            # Skoru kaydet
            cursor.execute("""
                INSERT INTO data_quality_scores
                (company_id, table_name, quality_score, total_records, valid_records, 
                 error_records, calculated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                table_name,
                score,
                total,
                valid,
                results.get('invalid', 0),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            return score

        except Exception as e:
            logging.info(f"Kalite skoru hesaplanamadı: {e}")
            return 0.0

    def get_quality_report(self, company_id: int) -> Dict:
        """
        Kalite raporu al
        
        Args:
            company_id: Şirket ID
        
        Returns:
            Kalite raporu
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tablo bazında skorlar
            cursor.execute("""
                SELECT table_name, quality_score, total_records, valid_records, 
                       error_records, calculated_at
                FROM data_quality_scores
                WHERE company_id = ?
                ORDER BY calculated_at DESC
            """, (company_id,))

            table_scores = []
            for row in cursor.fetchall():
                table_scores.append({
                    'table': row[0],
                    'score': row[1],
                    'total_records': row[2],
                    'valid_records': row[3],
                    'error_records': row[4],
                    'calculated_at': row[5]
                })

            # Genel ortalama
            avg_score = sum(t['score'] for t in table_scores) / len(table_scores) if table_scores else 0

            # En çok hata olan alanlar
            cursor.execute("""
                SELECT field_name, COUNT(*) as error_count
                FROM validation_results
                WHERE company_id = ? AND validation_status = 'invalid'
                GROUP BY field_name
                ORDER BY error_count DESC
                LIMIT 10
            """, (company_id,))

            top_errors = [{'field': row[0], 'count': row[1]} for row in cursor.fetchall()]

            conn.close()

            return {
                'average_score': avg_score,
                'table_scores': table_scores,
                'top_error_fields': top_errors
            }

        except Exception as e:
            logging.info(f"Kalite raporu alınamadı: {e}")
            return {
                'average_score': 0,
                'table_scores': [],
                'top_error_fields': []
            }


# ============================================
# HAZIR VALİDASYON KURALLARI
# ============================================

# Çevresel metrikler için çapraz kontroller
ENVIRONMENTAL_CROSS_CHECKS = [
    {
        'fields': ['total_energy', 'renewable_energy'],
        'check': lambda total, renewable: total >= renewable,
        'message': 'Yenilenebilir enerji toplam enerjiden fazla olamaz',
        'severity': 'error',
        'rule_id': 'energy_logic'
    },
    {
        'fields': ['water_withdrawal', 'water_discharge'],
        'check': lambda withdrawal, discharge: withdrawal >= discharge,
        'message': 'Su deşarjı su çekiminden fazla olamaz',
        'severity': 'warning',
        'rule_id': 'water_logic'
    },
    {
        'fields': ['total_waste', 'recycled_waste'],
        'check': lambda total, recycled: total >= recycled,
        'message': 'Geri dönüştürülen atık toplam atıktan fazla olamaz',
        'severity': 'error',
        'rule_id': 'waste_logic'
    }
]

# Sosyal metrikler için çapraz kontroller
SOCIAL_CROSS_CHECKS = [
    {
        'fields': ['total_employees', 'female_employees', 'male_employees'],
        'check': lambda total, female, male: total >= (female + male),
        'message': 'Kadın + erkek çalışan sayısı toplam çalışandan fazla olamaz',
        'severity': 'error',
        'rule_id': 'employee_count_logic'
    },
    {
        'fields': ['training_hours', 'total_employees'],
        'check': lambda hours, employees: (hours / employees) < 1000 if employees > 0 else True,
        'message': 'Çalışan başına düşen eğitim saati çok yüksek (>1000 saat)',
        'severity': 'warning',
        'rule_id': 'training_logic'
    }
]

# İSG metrikleri için çapraz kontroller
OHS_CROSS_CHECKS = [
    {
        'fields': ['total_injuries', 'lost_time_injuries'],
        'check': lambda total, lost_time: total >= lost_time,
        'message': 'İş kaybına yol açan kazalar toplam kazadan fazla olamaz',
        'severity': 'error',
        'rule_id': 'injury_logic'
    },
    {
        'fields': ['total_hours_worked', 'total_employees'],
        'check': lambda hours, employees: (hours / employees) < 3000 if employees > 0 else True,
        'message': 'Çalışan başına yıllık çalışma saati çok yüksek (>3000 saat)',
        'severity': 'warning',
        'rule_id': 'hours_logic'
    }
]

