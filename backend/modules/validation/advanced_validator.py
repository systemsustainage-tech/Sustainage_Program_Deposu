#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Veri Validasyon Sistemi - TAM VE EKSİKSİZ
Yıllık karşılaştırma, çapraz modül, kalite skoru, anomali tespiti
"""

import logging
import json
import os
import re
import sqlite3
import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from config.database import DB_PATH


class AdvancedDataValidator:
    """Gelişmiş veri validasyon sistemi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_validation_tables()
        self.normalization_rules = self._load_normalization_rules()

    def _init_validation_tables(self) -> None:
        """Validasyon tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Validasyon kuralları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_code TEXT UNIQUE NOT NULL,
                    rule_name TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    module_name TEXT,
                    description TEXT,
                    severity TEXT DEFAULT 'error',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if module_name column exists in validation_rules
            cursor.execute("PRAGMA table_info(validation_rules)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'module_name' not in columns:
                cursor.execute("ALTER TABLE validation_rules ADD COLUMN module_name TEXT")

            # Validasyon sonuçları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validation_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_name TEXT NOT NULL,
                    data_field TEXT NOT NULL,
                    data_value TEXT,
                    rule_code TEXT NOT NULL,
                    validation_status TEXT NOT NULL,
                    error_message TEXT,
                    severity TEXT DEFAULT 'error',
                    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT 0,
                    FOREIGN KEY (rule_code) REFERENCES validation_rules(rule_code)
                )
            """)
            
            # Check if module_name column exists in validation_results
            cursor.execute("PRAGMA table_info(validation_results)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'module_name' not in columns:
                cursor.execute("ALTER TABLE validation_results ADD COLUMN module_name TEXT NOT NULL DEFAULT 'unknown'")

            # Veri kalite skorları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_quality_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_name TEXT NOT NULL,
                    reporting_year INTEGER NOT NULL,
                    completeness_score REAL DEFAULT 0.0,
                    accuracy_score REAL DEFAULT 0.0,
                    consistency_score REAL DEFAULT 0.0,
                    timeliness_score REAL DEFAULT 0.0,
                    overall_score REAL DEFAULT 0.0,
                    total_fields INTEGER DEFAULT 0,
                    completed_fields INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    warning_count INTEGER DEFAULT 0,
                    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_id, module_name, reporting_year)
                )
            """)

            # Yıllık karşılaştırma sonuçları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS yearly_comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_name TEXT NOT NULL,
                    data_field TEXT NOT NULL,
                    current_year INTEGER NOT NULL,
                    current_value REAL,
                    previous_year INTEGER,
                    previous_value REAL,
                    change_amount REAL,
                    change_percentage REAL,
                    anomaly_detected BOOLEAN DEFAULT 0,
                    anomaly_reason TEXT,
                    compared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Eksik veri uyarıları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS missing_data_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_name TEXT NOT NULL,
                    data_field TEXT NOT NULL,
                    field_description TEXT,
                    importance_level TEXT DEFAULT 'orta',
                    alert_status TEXT DEFAULT 'aktif',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP
                )
            """)

            conn.commit()
            logging.info("[OK] Gelismis validasyon tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[ERROR] Validasyon tablolari olusturulurken hata: {e}")
        finally:
            conn.close()

    # =====================================================
    # 1. YILLIK VERİ KARŞILAŞTIRMA
    # =====================================================

    def compare_yearly_data(self, company_id: int, module_name: str,
                           current_year: int, data_field: str,
                           current_value: float) -> Dict:
        """
        Yıllık veri karşılaştırması yap
        
        Args:
            company_id: Şirket ID
            module_name: Modül adı
            current_year: Mevcut yıl
            data_field: Veri alanı
            current_value: Mevcut değer
            
        Returns:
            Karşılaştırma sonuçları
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            previous_year = current_year - 1

            # Önceki yıl verisini bul (tablo yapısına göre dinamik)
            previous_value = self._get_previous_year_value(
                company_id, module_name, data_field, previous_year
            )

            if previous_value is None:
                return {
                    "comparison_available": False,
                    "message": "Onceki yil verisi bulunamadi"
                }

            # Değişim hesapla
            change_amount = current_value - previous_value
            change_percentage = (change_amount / previous_value * 100) if previous_value != 0 else 0

            # Anomali kontrolü
            anomaly_detected, anomaly_reason = self._detect_yearly_anomaly(
                current_value, previous_value, change_percentage
            )

            # Sonuçları kaydet
            cursor.execute("""
                INSERT INTO yearly_comparisons 
                (company_id, module_name, data_field, current_year, current_value,
                 previous_year, previous_value, change_amount, change_percentage,
                 anomaly_detected, anomaly_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, module_name, data_field, current_year, current_value,
                  previous_year, previous_value, change_amount, change_percentage,
                  anomaly_detected, anomaly_reason))

            conn.commit()

            return {
                "comparison_available": True,
                "current_year": current_year,
                "current_value": current_value,
                "previous_year": previous_year,
                "previous_value": previous_value,
                "change_amount": change_amount,
                "change_percentage": change_percentage,
                "anomaly_detected": anomaly_detected,
                "anomaly_reason": anomaly_reason
            }

        except Exception as e:
            logging.error(f"Yillik karsilastirma hatasi: {e}")
            return {"comparison_available": False, "error": str(e)}
        finally:
            conn.close()

    def _get_previous_year_value(self, company_id: int, module_name: str,
                                 data_field: str, previous_year: int) -> Optional[float]:
        """Önceki yıl verisini getir (modül spesifik)"""
        # Bu fonksiyon her modül için özelleştirilmiş sorgu yapabilir
        # Örnek: Karbon emisyon verisi
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Genel bir yaklaşım - gerçek implementasyonda modüle göre özelleştirilmeli
            # Örnek tablolar: carbon_emissions, gri_data, sdg_indicators vb.

            if module_name == "karbon":
                cursor.execute("""
                    SELECT total_emissions FROM carbon_emissions
                    WHERE company_id = ? AND reporting_year = ?
                """, (company_id, previous_year))
            elif module_name == "enerji":
                cursor.execute("""
                    SELECT total_consumption FROM energy_data
                    WHERE company_id = ? AND reporting_year = ?
                """, (company_id, previous_year))
            elif module_name == "su":
                cursor.execute("""
                    SELECT total_withdrawal FROM water_data
                    WHERE company_id = ? AND reporting_year = ?
                """, (company_id, previous_year))
            else:
                return None

            result = cursor.fetchone()
            return result[0] if result else None

        except Exception as e:
            logging.error(f"Onceki yil verisi getirme hatasi: {e}")
            return None
        finally:
            conn.close()

    def _detect_yearly_anomaly(self, current: float, previous: float,
                               change_pct: float) -> Tuple[bool, str]:
        """Yıllık anomali tespit et"""
        # Anomali kriterleri
        if abs(change_pct) > 50:
            return True, f"Asiri degisim: %{change_pct:.1f}"
        elif current < 0:
            return True, "Negatif deger"
        elif previous > 0 and current == 0:
            return True, "Deger sifira dustu"
        elif previous == 0 and current > previous * 10:
            return True, "Asiri buyume"

        return False, ""

    # =====================================================
    # 2. ÇAPRAZ MODÜL VERİ TUTARLILIĞI
    # =====================================================

    def check_cross_module_consistency(self, company_id: int,
                                      reporting_year: int) -> List[Dict]:
        """
        Çapraz modül veri tutarlılığını kontrol et
        Örnek: Karbon verisi SDG, GRI, CDP'de tutarlı mı?
        """
        inconsistencies = []

        # 1. Karbon emisyon tutarlılığı
        carbon_check = self._check_carbon_consistency(company_id, reporting_year)
        if carbon_check:
            inconsistencies.extend(carbon_check)

        # 2. Enerji tüketimi tutarlılığı
        energy_check = self._check_energy_consistency(company_id, reporting_year)
        if energy_check:
            inconsistencies.extend(energy_check)

        # 3. Su tüketimi tutarlılığı
        water_check = self._check_water_consistency(company_id, reporting_year)
        if water_check:
            inconsistencies.extend(water_check)

        # 4. Çalışan sayısı tutarlılığı
        employee_check = self._check_employee_consistency(company_id, reporting_year)
        if employee_check:
            inconsistencies.extend(employee_check)

        return inconsistencies

    def _check_carbon_consistency(self, company_id: int,
                                 reporting_year: int) -> List[Dict]:
        """Karbon verisi tutarlılığı (Toplam + Scope 1/2/3, birim/doğrulama)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        inconsistencies = []

        try:
            # Farklı modüllerden karbon verilerini al
            values = {}

            # Karbon modülü
            cursor.execute("""
                SELECT total_emissions FROM carbon_emissions
                WHERE company_id = ? AND reporting_year = ?
            """, (company_id, reporting_year))
            result = cursor.fetchone()
            if result:
                values['karbon'] = result[0]

            # GRI 305 (Emissions)
            cursor.execute("""
                SELECT response FROM gri_indicators
                WHERE company_id = ? AND indicator_id LIKE 'GRI 305%' 
                AND reporting_year = ?
            """, (company_id, reporting_year))
            result = cursor.fetchone()
            if result and result[0]:
                parsed = self._parse_text_value(result[0], unit_type='emissions')
                if parsed is not None:
                    values['gri'] = parsed

            # CDP Climate Change
            cursor.execute("""
                SELECT response FROM cdp_climate_change
                WHERE company_id = ? AND question_id = 'C4.2'
                AND reporting_year = ?
            """, (company_id, reporting_year))
            result = cursor.fetchone()
            if result and result[0]:
                parsed = self._parse_text_value(result[0], unit_type='emissions')
                if parsed is not None:
                    values['cdp'] = parsed

            # Tutarlılık kontrolü
            if len(values) >= 2:
                values_list = list(values.values())
                avg_value = statistics.mean(values_list)

                for module, value in values.items():
                    deviation = abs(value - avg_value) / avg_value * 100 if avg_value > 0 else 0

                    if deviation > 10:  # %10'dan fazla sapma
                        inconsistencies.append({
                            "module": module,
                            "data_type": "Karbon Emisyonu",
                            "value": value,
                            "average": avg_value,
                            "deviation_pct": deviation,
                            "severity": "uyari" if deviation < 20 else "hata",
                            "message": f"{module} modülündeki karbon verisi ortalamadan %{deviation:.1f} sapıyor"
                        })

            # Scope 1/2/3 karşılaştırmaları (tcfd_metrics ve GRI 305-1/305-2/305-3)
            scope_map = {
                'scope1': 'GRI 305-1',
                'scope2': 'GRI 305-2',
                'scope3': 'GRI 305-3',
            }

            cursor.execute(
                """
                SELECT scope1_emissions, scope2_emissions, scope3_emissions
                FROM carbon_emissions
                WHERE company_id = ? AND reporting_year = ?
                """,
                (company_id, reporting_year),
            )
            scope_row = cursor.fetchone()
            if scope_row:
                scope_values = {
                    'scope1': scope_row[0],
                    'scope2': scope_row[1],
                    'scope3': scope_row[2],
                }
                for scope_key, gri_code in scope_map.items():
                    # GRI yanıtını al ve normalize et
                    cursor.execute(
                        """
                        SELECT response FROM gri_indicators
                        WHERE company_id = ? AND indicator_id = ? AND reporting_year = ?
                        """,
                        (company_id, gri_code, reporting_year),
                    )
                    gri_resp = cursor.fetchone()
                    gri_val = None
                    if gri_resp and gri_resp[0]:
                        gri_val = self._parse_text_value(gri_resp[0], unit_type='emissions')

                    if gri_val is None:
                        continue

                    sys_val = scope_values.get(scope_key)
                    if sys_val is None:
                        continue

                    # Negatif veya format hataları için kontrol
                    if sys_val < 0 or gri_val < 0:
                        inconsistencies.append({
                            "module": "karbon",
                            "data_type": f"{scope_key.upper()} Emisyonu",
                            "severity": "hata",
                            "message": f"{scope_key.upper()} emisyonu negatif olamaz",
                            "value": sys_val,
                            "gri_value": gri_val,
                        })
                        continue

                    avg_val = statistics.mean([sys_val, gri_val]) if (sys_val is not None and gri_val is not None) else None
                    if avg_val and avg_val > 0:
                        deviation = abs(sys_val - gri_val) / avg_val * 100
                        if deviation > 10:
                            inconsistencies.append({
                                "module": "karbon",
                                "data_type": f"{scope_key.upper()} Emisyonu",
                                "value": sys_val,
                                "gri_value": gri_val,
                                "deviation_pct": deviation,
                                "severity": "uyari" if deviation < 20 else "hata",
                                "message": f"{scope_key.upper()} emisyonu GRI ile uyumsuz (sapma %{deviation:.1f})",
                            })

        except Exception as e:
            logging.error(f"Karbon tutarlılık kontrolü hatası: {e}")
        finally:
            conn.close()

        return inconsistencies

    def _check_energy_consistency(self, company_id: int,
                                  reporting_year: int) -> List[Dict]:
        """Enerji verisi tutarlılığı (TCFD metrics vs GRI 302-1/302-3)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        inconsistencies: List[Dict] = []

        try:
            # TCFD Metrics (MWh ve yoğunluk)
            cursor.execute(
                """
                SELECT total_energy_consumption, energy_intensity
                FROM tcfd_metrics
                WHERE company_id = ? AND reporting_year = ?
                """,
                (company_id, reporting_year),
            )
            mrow = cursor.fetchone()
            tcfd_total_mwh = None
            tcfd_intensity = None
            if mrow:
                tcfd_total_mwh = mrow[0]
                tcfd_intensity = mrow[1]

            # GRI 302-1: Enerji tüketimi
            cursor.execute(
                """
                SELECT response FROM gri_indicators
                WHERE company_id = ? AND indicator_id = 'GRI 302-1' AND reporting_year = ?
                """,
                (company_id, reporting_year),
            )
            gri_3021_resp = cursor.fetchone()
            gri_total_mwh = None
            if gri_3021_resp and gri_3021_resp[0]:
                gri_total_mwh = self._parse_text_value(gri_3021_resp[0], unit_type='energy')

            # GRI 302-3: Enerji yoğunluğu
            cursor.execute(
                """
                SELECT response FROM gri_indicators
                WHERE company_id = ? AND indicator_id = 'GRI 302-3' AND reporting_year = ?
                """,
                (company_id, reporting_year),
            )
            gri_3023_resp = cursor.fetchone()
            gri_intensity = None
            if gri_3023_resp and gri_3023_resp[0]:
                gri_intensity = self._parse_text_value(gri_3023_resp[0], unit_type='energy_intensity')

            # Karşılaştırmalar
            if tcfd_total_mwh is not None and gri_total_mwh is not None:
                avg_val = statistics.mean([tcfd_total_mwh, gri_total_mwh]) if (tcfd_total_mwh and gri_total_mwh) else None
                if avg_val and avg_val > 0:
                    deviation = abs(tcfd_total_mwh - gri_total_mwh) / avg_val * 100
                    if deviation > 10:
                        inconsistencies.append({
                            "module": "enerji",
                            "data_type": "Toplam Enerji (MWh)",
                            "value": tcfd_total_mwh,
                            "gri_value": gri_total_mwh,
                            "deviation_pct": deviation,
                            "severity": "uyari" if deviation < 20 else "hata",
                            "message": f"TCFD toplam enerji GRI 302-1 ile uyumsuz (sapma %{deviation:.1f})",
                        })

            if tcfd_intensity is not None and gri_intensity is not None and tcfd_intensity >= 0 and gri_intensity >= 0:
                avg_val = statistics.mean([tcfd_intensity, gri_intensity]) if (tcfd_intensity and gri_intensity) else None
                if avg_val and avg_val > 0:
                    deviation = abs(tcfd_intensity - gri_intensity) / avg_val * 100
                    if deviation > 10:
                        inconsistencies.append({
                            "module": "enerji",
                            "data_type": "Enerji Yoğunluğu",
                            "value": tcfd_intensity,
                            "gri_value": gri_intensity,
                            "deviation_pct": deviation,
                            "severity": "uyari" if deviation < 20 else "hata",
                            "message": f"TCFD enerji yoğunluğu GRI 302-3 ile uyumsuz (sapma %{deviation:.1f})",
                        })

        except Exception as e:
            logging.error(f"Enerji tutarlılık kontrolü hatası: {e}")
        finally:
            conn.close()

        return inconsistencies

    def _check_water_consistency(self, company_id: int,
                                reporting_year: int) -> List[Dict]:
        """Su verisi tutarlılığı (TCFD metrics ve Water KPIs vs GRI 303-1/303-2/303-3)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        inconsistencies: List[Dict] = []

        try:
            # TCFD water consumption (m3)
            cursor.execute(
                """
                SELECT water_consumption, water_intensity
                FROM tcfd_metrics
                WHERE company_id = ? AND reporting_year = ?
                """,
                (company_id, reporting_year),
            )
            wrow = cursor.fetchone()
            tcfd_consumption_m3 = None
            if wrow:
                tcfd_consumption_m3 = wrow[0]
                wrow[1]

            # Water KPIs: withdrawal/discharge/consumption by year (period may be year)
            cursor.execute(
                """
                SELECT total_withdrawal_m3, total_discharge_m3, total_consumption_m3
                FROM water_kpis
                WHERE company_id = ? AND period = ?
                """,
                (company_id, str(reporting_year)),
            )
            kpi_row = cursor.fetchone()
            kpi_withdrawal = kpi_row[0] if kpi_row else None
            kpi_discharge = kpi_row[1] if kpi_row else None
            kpi_consumption = kpi_row[2] if kpi_row else None

            # GRI 303-3: Su tüketimi
            cursor.execute(
                """
                SELECT response FROM gri_indicators
                WHERE company_id = ? AND indicator_id = 'GRI 303-3' AND reporting_year = ?
                """,
                (company_id, reporting_year),
            )
            gri_3033_resp = cursor.fetchone()
            gri_consumption_m3 = None
            if gri_3033_resp and gri_3033_resp[0]:
                gri_consumption_m3 = self._parse_text_value(gri_3033_resp[0], unit_type='water')

            # GRI 303-1: Su çekimi
            cursor.execute(
                """
                SELECT response FROM gri_indicators
                WHERE company_id = ? AND indicator_id = 'GRI 303-1' AND reporting_year = ?
                """,
                (company_id, reporting_year),
            )
            gri_3031_resp = cursor.fetchone()
            gri_withdrawal_m3 = None
            if gri_3031_resp and gri_3031_resp[0]:
                gri_withdrawal_m3 = self._parse_text_value(gri_3031_resp[0], unit_type='water')

            # GRI 303-2: Su deşarj
            cursor.execute(
                """
                SELECT response FROM gri_indicators
                WHERE company_id = ? AND indicator_id = 'GRI 303-2' AND reporting_year = ?
                """,
                (company_id, reporting_year),
            )
            gri_3032_resp = cursor.fetchone()
            gri_discharge_m3 = None
            if gri_3032_resp and gri_3032_resp[0]:
                gri_discharge_m3 = self._parse_text_value(gri_3032_resp[0], unit_type='water')

            # Karşılaştırmalar
            # Tüketim (TCFD vs GRI ve KPI vs GRI)
            for label, sys_val in [
                ("TCFD", tcfd_consumption_m3),
                ("Water KPI", kpi_consumption),
            ]:
                if sys_val is not None and gri_consumption_m3 is not None:
                    avg_val = statistics.mean([sys_val, gri_consumption_m3])
                    if avg_val and avg_val > 0:
                        deviation = abs(sys_val - gri_consumption_m3) / avg_val * 100
                        if deviation > 10:
                            inconsistencies.append({
                                "module": "su",
                                "data_type": f"Su Tüketimi (m3) - {label}",
                                "value": sys_val,
                                "gri_value": gri_consumption_m3,
                                "deviation_pct": deviation,
                                "severity": "uyari" if deviation < 20 else "hata",
                                "message": f"{label} su tüketimi GRI 303-3 ile uyumsuz (sapma %{deviation:.1f})",
                            })

            # Çekim (KPI vs GRI 303-1)
            if kpi_withdrawal is not None and gri_withdrawal_m3 is not None:
                avg_val = statistics.mean([kpi_withdrawal, gri_withdrawal_m3])
                if avg_val and avg_val > 0:
                    deviation = abs(kpi_withdrawal - gri_withdrawal_m3) / avg_val * 100
                    if deviation > 10:
                        inconsistencies.append({
                            "module": "su",
                            "data_type": "Su Çekimi (m3)",
                            "value": kpi_withdrawal,
                            "gri_value": gri_withdrawal_m3,
                            "deviation_pct": deviation,
                            "severity": "uyari" if deviation < 20 else "hata",
                            "message": f"Water KPI çekim GRI 303-1 ile uyumsuz (sapma %{deviation:.1f})",
                        })

            # Deşarj (KPI vs GRI 303-2)
            if kpi_discharge is not None and gri_discharge_m3 is not None:
                avg_val = statistics.mean([kpi_discharge, gri_discharge_m3])
                if avg_val and avg_val > 0:
                    deviation = abs(kpi_discharge - gri_discharge_m3) / avg_val * 100
                    if deviation > 10:
                        inconsistencies.append({
                            "module": "su",
                            "data_type": "Su Deşarj (m3)",
                            "value": kpi_discharge,
                            "gri_value": gri_discharge_m3,
                            "deviation_pct": deviation,
                            "severity": "uyari" if deviation < 20 else "hata",
                            "message": f"Water KPI deşarj GRI 303-2 ile uyumsuz (sapma %{deviation:.1f})",
                        })

        except Exception as e:
            logging.error(f"Su tutarlılık kontrolü hatası: {e}")
        finally:
            conn.close()

        return inconsistencies

    def _check_employee_consistency(self, company_id: int,
                                   reporting_year: int) -> List[Dict]:
        """Çalışan sayısı tutarlılığı"""
        # Benzer mantık, çalışan sayısı için
        return []

    # =====================================================
    # 3. VERİ KALİTE SKORU (0-100)
    # =====================================================

    def calculate_quality_score(self, company_id: int, module_name: str,
                               reporting_year: int) -> Dict:
        """
        Veri kalite skorunu hesapla (0-100)
        
        Bileşenler:
        - Tamlık (Completeness): %40
        - Doğruluk (Accuracy): %30
        - Tutarlılık (Consistency): %20
        - Güncellik (Timeliness): %10
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 1. Tamlık Skoru (%40)
            completeness = self._calculate_completeness(company_id, module_name, reporting_year)

            # 2. Doğruluk Skoru (%30)
            accuracy = self._calculate_accuracy(company_id, module_name, reporting_year)

            # 3. Tutarlılık Skoru (%20)
            consistency = self._calculate_consistency(company_id, module_name, reporting_year)

            # 4. Güncellik Skoru (%10)
            timeliness = self._calculate_timeliness(company_id, module_name, reporting_year)

            # Genel skor
            overall_score = (
                completeness * 0.40 +
                accuracy * 0.30 +
                consistency * 0.20 +
                timeliness * 0.10
            )

            # Hata sayıları
            cursor.execute("""
                SELECT COUNT(*) FROM validation_results
                WHERE company_id = ? AND module_name = ? 
                AND validation_status = 'hata'
                AND resolved = 0
            """, (company_id, module_name))
            error_count = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM validation_results
                WHERE company_id = ? AND module_name = ? 
                AND validation_status = 'uyari'
                AND resolved = 0
            """, (company_id, module_name))
            warning_count = cursor.fetchone()[0]

            # Skorları kaydet
            cursor.execute("""
                INSERT OR REPLACE INTO data_quality_scores
                (company_id, module_name, reporting_year, completeness_score,
                 accuracy_score, consistency_score, timeliness_score, overall_score,
                 error_count, warning_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, module_name, reporting_year, completeness, accuracy,
                  consistency, timeliness, overall_score, error_count, warning_count))

            conn.commit()

            return {
                "overall_score": round(overall_score, 1),
                "completeness_score": round(completeness, 1),
                "accuracy_score": round(accuracy, 1),
                "consistency_score": round(consistency, 1),
                "timeliness_score": round(timeliness, 1),
                "error_count": error_count,
                "warning_count": warning_count,
                "grade": self._get_quality_grade(overall_score)
            }

        except Exception as e:
            logging.error(f"Kalite skoru hesaplama hatası: {e}")
            return {
                "overall_score": 0.0,
                "grade": "F",
                "error": str(e)
            }
        finally:
            conn.close()

    def _calculate_completeness(self, company_id: int, module_name: str,
                               reporting_year: int) -> float:
        """Tamlık skorunu hesapla"""
        # Modüldeki zorunlu alanların dolu olma oranı
        # Basitleştirilmiş hesaplama - gerçekte modül spesifik olmalı
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Eksik veri uyarılarını say
            cursor.execute("""
                SELECT COUNT(*) FROM missing_data_alerts
                WHERE company_id = ? AND module_name = ?
                AND alert_status = 'aktif'
            """, (company_id, module_name))
            missing_count = cursor.fetchone()[0]

            # Basit hesaplama: Her eksik alan %5 düşürür
            score = max(0, 100 - (missing_count * 5))
            return score

        except Exception:
            return 50.0  # Varsayılan
        finally:
            conn.close()

    def _calculate_accuracy(self, company_id: int, module_name: str,
                          reporting_year: int) -> float:
        """Doğruluk skorunu hesapla"""
        # Validasyon hatalarına göre
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT COUNT(*) FROM validation_results
                WHERE company_id = ? AND module_name = ?
                AND validation_status IN ('hata', 'uyari')
                AND resolved = 0
            """, (company_id, module_name))
            error_count = cursor.fetchone()[0]

            # Her hata %3 düşürür
            score = max(0, 100 - (error_count * 3))
            return score

        except Exception:
            return 70.0  # Varsayılan
        finally:
            conn.close()

    def _calculate_consistency(self, company_id: int, module_name: str,
                              reporting_year: int) -> float:
        """Tutarlılık skorunu hesapla"""
        # Çapraz modül tutarsızlıklarına göre
        inconsistencies = self.check_cross_module_consistency(company_id, reporting_year)

        # Modül spesifik tutarsızlıkları filtrele
        module_inconsistencies = [i for i in inconsistencies if i.get('module') == module_name]

        # Her tutarsızlık %10 düşürür
        score = max(0, 100 - (len(module_inconsistencies) * 10))
        return score

    def _calculate_timeliness(self, company_id: int, module_name: str,
                            reporting_year: int) -> float:
        """Güncellik skorunu hesapla"""
        # Verinin ne kadar güncel olduğu
        # Basitleştirilmiş - raporlama yılına göre
        current_year = datetime.now().year

        if reporting_year == current_year:
            return 100.0
        elif reporting_year == current_year - 1:
            return 80.0
        elif reporting_year >= current_year - 2:
            return 60.0
        else:
            return 40.0

    def _get_quality_grade(self, score: float) -> str:
        """Kalite notunu belirle"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    # =====================================================
    # 4. EKSİK VERİ UYARI SİSTEMİ
    # =====================================================

    def check_missing_data(self, company_id: int, module_name: str) -> List[Dict]:
        """Eksik verileri kontrol et ve uyar"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        missing_data = []

        try:
            # Modül spesifik zorunlu alanları kontrol et
            required_fields = self._get_required_fields(module_name)

            for field_info in required_fields:
                field_name = field_info['field_name']
                table_name = field_info['table_name']
                importance = field_info['importance']
                description = field_info['description']

                # Alanın dolu olup olmadığını kontrol et
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {table_name}
                        WHERE company_id = ? AND ({field_name} IS NULL OR {field_name} = '')
                    """, (company_id,))

                    missing_count = cursor.fetchone()[0]

                    if missing_count > 0:
                        # Uyarıyı kaydet
                        cursor.execute("""
                            INSERT OR IGNORE INTO missing_data_alerts
                            (company_id, module_name, data_field, field_description, importance_level)
                            VALUES (?, ?, ?, ?, ?)
                        """, (company_id, module_name, field_name, description, importance))

                        missing_data.append({
                            "field_name": field_name,
                            "description": description,
                            "importance": importance,
                            "missing_count": missing_count
                        })

                except Exception as e:
                    logging.error(f"Alan kontrolü hatası ({field_name}): {e}")
                    continue

            conn.commit()
            return missing_data

        except Exception as e:
            logging.error(f"Eksik veri kontrolü hatası: {e}")
            return []
        finally:
            conn.close()

    def _get_required_fields(self, module_name: str) -> List[Dict]:
        """Modül için zorunlu alanları getir"""
        # Modül spesifik zorunlu alanlar
        fields_map = {
            "karbon": [
                {"field_name": "scope1_emissions", "table_name": "carbon_emissions",
                 "importance": "yuksek", "description": "Scope 1 Emisyonları"},
                {"field_name": "scope2_emissions", "table_name": "carbon_emissions",
                 "importance": "yuksek", "description": "Scope 2 Emisyonları"},
            ],
            "enerji": [
                {"field_name": "total_consumption", "table_name": "energy_data",
                 "importance": "yuksek", "description": "Toplam Enerji Tüketimi"},
            ],
            "su": [
                {"field_name": "total_withdrawal", "table_name": "water_data",
                 "importance": "yuksek", "description": "Toplam Su Tüketimi"},
            ]
        }

        return fields_map.get(module_name, [])

    # =====================================================
    # 5. ANOMALİ TESPİTİ
    # =====================================================

    def detect_anomalies(self, company_id: int, module_name: str,
                        reporting_year: int) -> List[Dict]:
        """
        Anomali tespiti - beklenmedik değerler
        
        Yöntemler:
        - İstatistiksel anomali (standart sapma)
        - Tarihsel anomali (yıllık trend)
        - Mantıksal anomali (negatif değerler, sıfır değerler)
        """
        anomalies = []

        # 1. İstatistiksel anomali tespiti
        statistical_anomalies = self._detect_statistical_anomalies(
            company_id, module_name, reporting_year
        )
        anomalies.extend(statistical_anomalies)

        # 2. Tarihsel anomali tespiti
        historical_anomalies = self._detect_historical_anomalies(
            company_id, module_name, reporting_year
        )
        anomalies.extend(historical_anomalies)

        # 3. Mantıksal anomali tespiti
        logical_anomalies = self._detect_logical_anomalies(
            company_id, module_name, reporting_year
        )
        anomalies.extend(logical_anomalies)

        return anomalies

    def _detect_statistical_anomalies(self, company_id: int, module_name: str,
                                     reporting_year: int) -> List[Dict]:
        """İstatistiksel anomali tespiti (Z-score yöntemi)"""
        # Standart sapma üzerinden anomali tespiti
        anomalies = []

        # Bu basitleştirilmiş bir örnek
        # Gerçek implementasyonda her veri alanı için ayrı analiz yapılmalı

        return anomalies

    def _detect_historical_anomalies(self, company_id: int, module_name: str,
                                    reporting_year: int) -> List[Dict]:
        """Tarihsel anomali tespiti"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        anomalies = []

        try:
            # Yıllık karşılaştırma tablosundan anomalileri al
            cursor.execute("""
                SELECT data_field, current_value, previous_value, 
                       change_percentage, anomaly_reason
                FROM yearly_comparisons
                WHERE company_id = ? AND module_name = ? 
                AND current_year = ? AND anomaly_detected = 1
            """, (company_id, module_name, reporting_year))

            for row in cursor.fetchall():
                anomalies.append({
                    "type": "tarihsel",
                    "field": row[0],
                    "current_value": row[1],
                    "previous_value": row[2],
                    "change_pct": row[3],
                    "reason": row[4]
                })

        except Exception as e:
            logging.error(f"Tarihsel anomali tespiti hatası: {e}")
        finally:
            conn.close()

        return anomalies

    def _detect_logical_anomalies(self, company_id: int, module_name: str,
                                  reporting_year: int) -> List[Dict]:
        """Mantıksal anomali tespiti"""
        # Negatif değerler, sıfır değerler, mantıksız oranlar vb.
        anomalies = []

        # Modül spesifik mantık kontrolleri
        # Örnek: Karbon emisyonu negatif olamaz
        # Örnek: Enerji tüketimi sıfır olamaz (aktif şirket için)

        return anomalies

    # =====================================================
    # YARDIMCI FONKSİYONLAR
    # =====================================================

    def _load_normalization_rules(self) -> Dict[str, Any]:
        """Birim dönüştürme ve ölçeklendirme kurallarını JSON'dan yükle"""
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            rules_path = os.path.join(base_dir, 'modules', 'validation', 'normalization_rules.json')
            if os.path.exists(rules_path):
                with open(rules_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Normalization rules yükleme hatası: {e}")
        # Varsayılan kurallar
        return {
            "energy_units": {
                "mwh": 1.0,
                "kwh": 1.0 / 1000.0,
                "gj": 1.0 / 3.6,
            },
            "water_units": {
                "m3": 1.0,
                "m^3": 1.0,
                "litre": 1.0 / 1000.0,
                "liter": 1.0 / 1000.0,
                "l": 1.0 / 1000.0,
            },
            "emissions_units": {
                "tco2e": 1.0,
                "ton": 1.0,
                "tonne": 1.0,
                "kgco2e": 1.0 / 1000.0,
                "kg": 1.0 / 1000.0,
                "kt": 1000.0,
                "mt": 1_000_000.0,
            },
        }

    def _parse_text_value(self, text: Any, unit_type: str) -> Optional[float]:
        """
        Serbest metin yanıtından sayısal değer ve birimi ayıkla, normalize et.
        unit_type: 'energy' (MWh), 'energy_intensity' (sayısal), 'water' (m3), 'emissions' (tCO2e)
        """
        if text is None:
            return None
        if isinstance(text, (int, float)):
            # Enerji için MWh varsayımı; diğerleri doğrudan değer
            if unit_type == 'energy':
                return float(text)
            elif unit_type == 'water':
                return float(text)
            elif unit_type == 'emissions':
                return float(text)
            elif unit_type == 'energy_intensity':
                return float(text)
            return float(text)

        # Metin normalize
        s = str(text).lower().strip()
        # "1,200,000" -> "1200000"
        s = s.replace(' ', '')
        s = s.replace('\u00a0', '')  # non-breaking space
        s = s.replace(',', '')

        # Birim belirleme
        unit_scale = 1.0
        if unit_type == 'energy':
            # kwh, mwh, gj
            for unit_key, scale in self.normalization_rules.get('energy_units', {}).items():
                if unit_key in s:
                    unit_scale = scale
                    break
        elif unit_type == 'water':
            for unit_key, scale in self.normalization_rules.get('water_units', {}).items():
                if unit_key in s:
                    unit_scale = scale
                    break
        elif unit_type == 'emissions':
            for unit_key, scale in self.normalization_rules.get('emissions_units', {}).items():
                if unit_key in s:
                    unit_scale = scale
                    break
        elif unit_type == 'energy_intensity':
            # Yoğunluk için sadece sayıyı al; birim farklı olabilir
            unit_scale = 1.0

        # Sayıyı ayıkla
        m = re.search(r"([-+]?[0-9]*\.?[0-9]+)", s)
        if not m:
            return None
        try:
            val = float(m.group(1))
            return val * unit_scale
        except Exception:
            return None

    def get_validation_summary(self, company_id: int,
                              reporting_year: int = None) -> Dict:
        """Genel validasyon özeti"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            summary = {
                "total_errors": 0,
                "total_warnings": 0,
                "total_missing": 0,
                "total_anomalies": 0,
                "average_quality_score": 0.0,
                "modules": {}
            }

            # Hata ve uyarı sayıları
            cursor.execute("""
                SELECT module_name, 
                       SUM(CASE WHEN severity = 'hata' THEN 1 ELSE 0 END) as errors,
                       SUM(CASE WHEN severity = 'uyari' THEN 1 ELSE 0 END) as warnings
                FROM validation_results
                WHERE company_id = ? AND resolved = 0
                GROUP BY module_name
            """, (company_id,))

            for row in cursor.fetchall():
                module = row[0]
                summary["modules"][module] = {
                    "errors": row[1],
                    "warnings": row[2]
                }
                summary["total_errors"] += row[1]
                summary["total_warnings"] += row[2]

            # Eksik veri sayısı
            cursor.execute("""
                SELECT COUNT(*) FROM missing_data_alerts
                WHERE company_id = ? AND alert_status = 'aktif'
            """, (company_id,))
            summary["total_missing"] = cursor.fetchone()[0]

            # Anomali sayısı
            cursor.execute("""
                SELECT COUNT(*) FROM yearly_comparisons
                WHERE company_id = ? AND anomaly_detected = 1
            """, (company_id,))
            summary["total_anomalies"] = cursor.fetchone()[0]

            # Ortalama kalite skoru
            if reporting_year:
                cursor.execute("""
                    SELECT AVG(overall_score) FROM data_quality_scores
                    WHERE company_id = ? AND reporting_year = ?
                """, (company_id, reporting_year))
            else:
                cursor.execute("""
                    SELECT AVG(overall_score) FROM data_quality_scores
                    WHERE company_id = ?
                """, (company_id,))

            result = cursor.fetchone()
            summary["average_quality_score"] = round(result[0], 1) if result[0] else 0.0

            return summary

        except Exception as e:
            logging.error(f"Özet hesaplama hatası: {e}")
            return summary
        finally:
            conn.close()
