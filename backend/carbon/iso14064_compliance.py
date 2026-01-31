#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISO 14064-1:2018 UYUMLULUK MODÜLÜ
Organizasyonel Sera Gazı Envanteri - ISO Standardına Özel Özellikler
"""

import logging
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, Optional
from config.icons import Icons
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ISO14064Compliance:
    """ISO 14064-1:2018 standardına uyumluluk sağlayan ek özellikler"""

    # ISO 14064-1:2018 Gereksinimleri
    ISO_REQUIREMENTS = {
        '5.2.1': 'Organizational Boundary Tanımı',
        '5.2.2': 'Operational Boundary',
        '5.2.3': 'Scope 1, 2, 3 Kategorileri',
        '5.2.4': 'Quantification Methodologies',
        '5.2.5': 'GHG Source Data Quality',
        '5.2.6': 'Base Year ve Recalculation',
        '5.2.7': 'Uncertainty Assessment',
        '5.2.8': 'GHG Removals and Offsets',
        '6.3': 'Verification/Validation',
        '6.4': 'GHG Inventory Report'
    }

    # Belirsizlik Seviyeleri (ISO Tablo A.1)
    UNCERTAINTY_LEVELS = {
        'Tier 1 - Measured': 5,      # %±5 (Doğrudan ölçüm)
        'Tier 2 - Calculated': 10,   # %±10 (Faktör bazlı hesaplama)
        'Tier 3 - Estimated': 30,    # %±30 (Tahmin/varsayım)
        'Tier 4 - Default': 50       # %±50 (Default değerler)
    }

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.create_tables()

    def get_connection(self) -> sqlite3.Connection:
        """Veritabanı bağlantısı"""
        return sqlite3.connect(self.db_path)

    def create_tables(self) -> None:
        """ISO 14064-1 için ek tablolar"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Organizational Boundary Tanımı
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS iso14064_organizational_boundary (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    boundary_name TEXT NOT NULL,
                    approach TEXT NOT NULL,              -- equity_share, financial_control, operational_control
                    description TEXT,
                    included_entities TEXT,              -- JSON list
                    excluded_entities TEXT,              -- JSON list
                    consolidation_approach TEXT,
                    reporting_period TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 2. Base Year ve Recalculation Policy
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS iso14064_base_year (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    base_year INTEGER NOT NULL,
                    base_year_emissions REAL NOT NULL,
                    recalculation_policy TEXT,
                    significance_threshold REAL DEFAULT 5.0,  -- %5 eşik değeri
                    recalculation_triggers TEXT,              -- JSON array
                    last_recalculated DATE,
                    recalculation_history TEXT,               -- JSON
                    justification TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE(company_id, base_year)
                )
            """)

            # 3. Uncertainty Assessment
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS iso14064_uncertainty (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    emission_id INTEGER,                      -- carbon_emissions referans
                    scope TEXT NOT NULL,
                    category TEXT,
                    data_quality_tier TEXT NOT NULL,          -- Tier 1-4
                    uncertainty_percentage REAL NOT NULL,
                    uncertainty_source TEXT,
                    lower_bound REAL,                         -- Değer - belirsizlik
                    upper_bound REAL,                         -- Değer + belirsizlik
                    assessment_method TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    FOREIGN KEY(emission_id) REFERENCES carbon_emissions(id) ON DELETE SET NULL
                )
            """)

            # 4. ISO Verification Records
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS iso14064_verification (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    verification_period TEXT NOT NULL,
                    verification_level TEXT,                  -- limited, reasonable
                    verification_standard TEXT DEFAULT 'ISO 14064-3:2019',
                    verifier_name TEXT NOT NULL,
                    verifier_accreditation TEXT,
                    verification_date DATE NOT NULL,
                    verification_statement_file TEXT,
                    materiality_threshold REAL,
                    findings TEXT,                            -- JSON
                    non_conformities TEXT,                    -- JSON
                    verification_opinion TEXT,                -- positive, qualified, negative
                    ghg_assertion_assured REAL,               -- Doğrulanan emisyon (tCO2e)
                    assurance_level_achieved TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            # 5. ISO Compliance Checklist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS iso14064_compliance_checklist (
                    id INTEGER PRIMARY KEY,
                    company_id INTEGER NOT NULL,
                    period TEXT NOT NULL,
                    iso_clause TEXT NOT NULL,                 -- 5.2.1, 5.2.2, vb.
                    requirement_description TEXT,
                    compliance_status TEXT DEFAULT 'pending', -- pending, compliant, non_compliant
                    evidence TEXT,
                    responsible_person TEXT,
                    completion_date DATE,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """)

            conn.commit()

        except Exception as e:
            logging.error(f"[ERROR] ISO 14064 tabloları oluşturulamadı: {e}")
            conn.rollback()
        finally:
            conn.close()

    # ==================== ORGANIZATIONAL BOUNDARY ====================

    def define_organizational_boundary(self, company_id: int, boundary_data: Dict) -> Optional[int]:
        """Organizasyonel sınır tanımla (ISO 5.2.1)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO iso14064_organizational_boundary (
                    company_id, boundary_name, approach, description,
                    included_entities, excluded_entities, consolidation_approach,
                    reporting_period
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                boundary_data.get('boundary_name'),
                boundary_data.get('approach', 'operational_control'),
                boundary_data.get('description'),
                json.dumps(boundary_data.get('included_entities', [])),
                json.dumps(boundary_data.get('excluded_entities', [])),
                boundary_data.get('consolidation_approach'),
                boundary_data.get('reporting_period')
            ))

            boundary_id = cursor.lastrowid
            conn.commit()
            return boundary_id

        except Exception as e:
            logging.error(f"[ERROR] Boundary tanımlanamadı: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    # ==================== BASE YEAR & RECALCULATION ====================

    def set_base_year(self, company_id: int, base_year_data: Dict) -> Optional[int]:
        """Base year tanımla ve recalculation policy belirle (ISO 5.2.6)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Recalculation triggers (yeniden hesaplama nedenleri)
            default_triggers = [
                'Structural changes (merger/acquisition)',
                'Calculation methodology changes',
                'Emission factor updates',
                'Discovery of significant errors',
                'Outsourcing/insourcing changes'
            ]

            cursor.execute("""
                INSERT INTO iso14064_base_year (
                    company_id, base_year, base_year_emissions,
                    recalculation_policy, significance_threshold,
                    recalculation_triggers, justification
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id, base_year) DO UPDATE SET
                    base_year_emissions = excluded.base_year_emissions,
                    recalculation_policy = excluded.recalculation_policy,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                company_id,
                base_year_data.get('base_year'),
                base_year_data.get('base_year_emissions'),
                base_year_data.get('recalculation_policy',
                    'Base year will be recalculated if changes exceed 5% threshold'),
                base_year_data.get('significance_threshold', 5.0),
                json.dumps(base_year_data.get('recalculation_triggers', default_triggers)),
                base_year_data.get('justification')
            ))

            conn.commit()
            return cursor.lastrowid

        except Exception as e:
            logging.error(f"[ERROR] Base year belirlenemedi: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def check_base_year_recalculation(self, company_id: int,
                                      current_emissions: float,
                                      structural_changes: bool = False) -> Dict:
        """Base year yeniden hesaplama gerekli mi kontrol et"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM iso14064_base_year
                WHERE company_id = ?
                ORDER BY base_year DESC
                LIMIT 1
            """, (company_id,))

            base_year_record = cursor.fetchone()

            if not base_year_record:
                return {'recalculation_needed': False, 'reason': 'No base year defined'}

            base_year_emissions = base_year_record['base_year_emissions']
            threshold = base_year_record['significance_threshold']

            # Değişim yüzdesi
            change_pct = abs((current_emissions - base_year_emissions) / base_year_emissions * 100)

            recalculation_needed = (
                change_pct > threshold or
                structural_changes
            )

            return {
                'recalculation_needed': recalculation_needed,
                'base_year': base_year_record['base_year'],
                'base_year_emissions': base_year_emissions,
                'current_emissions': current_emissions,
                'change_percentage': round(change_pct, 2),
                'threshold': threshold,
                'reason': f'Change ({change_pct:.1f}%) exceeds threshold ({threshold}%)' if recalculation_needed else 'Within threshold'
            }

        except Exception as e:
            logging.error(f"[ERROR] Recalculation kontrolü yapılamadı: {e}")
            return {}
        finally:
            conn.close()

    # ==================== UNCERTAINTY ASSESSMENT ====================

    def assess_uncertainty(self, company_id: int, period: str,
                          emission_id: Optional[int] = None) -> Dict:
        """Belirsizlik değerlendirmesi yap (ISO 5.2.7)"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Emisyon verilerini al
            if emission_id:
                query = """
                    SELECT * FROM carbon_emissions
                    WHERE id = ?
                """
                params = (emission_id,)
            else:
                query = """
                    SELECT * FROM carbon_emissions
                    WHERE company_id = ? AND period = ?
                """
                params = (company_id, period)

            cursor.execute(query, params)
            emissions = cursor.fetchall()

            total_emissions = 0
            weighted_uncertainty = 0

            uncertainty_breakdown = []

            for emission in emissions:
                co2e = emission['co2e_emissions']
                data_quality = emission['data_quality']

                # Tier belirleme
                tier_map = {
                    'measured': 'Tier 1 - Measured',
                    'calculated': 'Tier 2 - Calculated',
                    'estimated': 'Tier 3 - Estimated',
                    'default': 'Tier 4 - Default'
                }
                tier = tier_map.get(data_quality, 'Tier 3 - Estimated')
                uncertainty_pct = self.UNCERTAINTY_LEVELS[tier]

                # Ağırlıklı belirsizlik
                total_emissions += co2e
                weighted_uncertainty += co2e * (uncertainty_pct / 100)

                # Alt ve üst sınır
                lower_bound = co2e * (1 - uncertainty_pct / 100)
                upper_bound = co2e * (1 + uncertainty_pct / 100)

                uncertainty_breakdown.append({
                    'emission_id': emission['id'],
                    'scope': emission['scope'],
                    'category': emission['category'],
                    'co2e': co2e,
                    'tier': tier,
                    'uncertainty_pct': uncertainty_pct,
                    'lower_bound': round(lower_bound, 2),
                    'upper_bound': round(upper_bound, 2)
                })

            # Toplam belirsizlik
            if total_emissions > 0:
                overall_uncertainty_pct = (weighted_uncertainty / total_emissions) * 100
            else:
                overall_uncertainty_pct = 0

            return {
                'total_emissions': round(total_emissions, 2),
                'overall_uncertainty_pct': round(overall_uncertainty_pct, 2),
                'lower_bound_total': round(total_emissions - weighted_uncertainty, 2),
                'upper_bound_total': round(total_emissions + weighted_uncertainty, 2),
                'breakdown': uncertainty_breakdown,
                'assessment_date': datetime.now().isoformat()
            }

        except Exception as e:
            logging.error(f"[ERROR] Belirsizlik değerlendirmesi yapılamadı: {e}")
            return {}
        finally:
            conn.close()

    # ==================== VERIFICATION ====================

    def record_verification(self, company_id: int, verification_data: Dict) -> Optional[int]:
        """ISO 14064-3 doğrulama kaydı (ISO 6.3)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO iso14064_verification (
                    company_id, verification_period, verification_level,
                    verification_standard, verifier_name, verifier_accreditation,
                    verification_date, verification_statement_file,
                    materiality_threshold, findings, non_conformities,
                    verification_opinion, ghg_assertion_assured,
                    assurance_level_achieved, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                verification_data.get('verification_period'),
                verification_data.get('verification_level', 'reasonable'),
                verification_data.get('verification_standard', 'ISO 14064-3:2019'),
                verification_data.get('verifier_name'),
                verification_data.get('verifier_accreditation'),
                verification_data.get('verification_date'),
                verification_data.get('verification_statement_file'),
                verification_data.get('materiality_threshold', 5.0),
                json.dumps(verification_data.get('findings', [])),
                json.dumps(verification_data.get('non_conformities', [])),
                verification_data.get('verification_opinion', 'positive'),
                verification_data.get('ghg_assertion_assured'),
                verification_data.get('assurance_level_achieved'),
                verification_data.get('notes')
            ))

            verification_id = cursor.lastrowid
            conn.commit()
            return verification_id

        except Exception as e:
            logging.error(f"[ERROR] Verification kaydedilemedi: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    # ==================== COMPLIANCE CHECKLIST ====================

    def initialize_compliance_checklist(self, company_id: int, period: str) -> bool:
        """ISO 14064-1 uyumluluk kontrol listesi oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            checklist_items = [
                ('5.2.1', 'Organizational boundary defined'),
                ('5.2.2', 'Operational boundary defined'),
                ('5.2.3', 'GHG sources identified and categorized'),
                ('5.2.4', 'Quantification methodologies selected'),
                ('5.2.5', 'GHG source data collected and managed'),
                ('5.2.6', 'Base year established with recalculation policy'),
                ('5.2.7', 'Uncertainty assessment completed'),
                ('5.2.8', 'GHG removals and offsets quantified'),
                ('6.3', 'Verification/validation conducted'),
                ('6.4', 'GHG inventory report prepared')
            ]

            for clause, description in checklist_items:
                cursor.execute("""
                    INSERT INTO iso14064_compliance_checklist (
                        company_id, period, iso_clause, requirement_description
                    ) VALUES (?, ?, ?, ?)
                    ON CONFLICT DO NOTHING
                """, (company_id, period, clause, description))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"[ERROR] Checklist oluşturulamadı: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def update_compliance_status(self, company_id: int, period: str,
                                 iso_clause: str, status: str) -> bool:
        """Uyumluluk durumunu güncelle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE iso14064_compliance_checklist
                SET compliance_status = ?,
                    completion_date = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE company_id = ? AND period = ? AND iso_clause = ?
            """, (status, datetime.now().date().isoformat(),
                  company_id, period, iso_clause))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"[ERROR] Compliance durumu güncellenemedi: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_compliance_report(self, company_id: int, period: str) -> Dict:
        """ISO 14064-1 uyumluluk raporu"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM iso14064_compliance_checklist
                WHERE company_id = ? AND period = ?
                ORDER BY iso_clause
            """, (company_id, period))

            checklist = cursor.fetchall()

            total_items = len(checklist)
            compliant_items = sum(1 for item in checklist if item['compliance_status'] == 'compliant')

            compliance_percentage = (compliant_items / total_items * 100) if total_items > 0 else 0

            return {
                'period': period,
                'total_requirements': total_items,
                'compliant_count': compliant_items,
                'compliance_percentage': round(compliance_percentage, 1),
                'checklist': [dict(item) for item in checklist],
                'overall_status': 'Compliant' if compliance_percentage >= 90 else 'Partial' if compliance_percentage >= 50 else 'Non-Compliant'
            }

        except Exception as e:
            logging.error(f"[ERROR] Compliance raporu oluşturulamadı: {e}")
            return {}
        finally:
            conn.close()


if __name__ == "__main__":
    # Test
    iso_mgr = ISO14064Compliance()
    logging.info(f"{Icons.SUCCESS} ISO 14064-1:2018 tabloları oluşturuldu")

    # Test: Base year
    iso_mgr.set_base_year(1, {
        'base_year': 2020,
        'base_year_emissions': 1000.0,
        'recalculation_policy': 'Automatic recalculation when changes exceed 5%',
        'significance_threshold': 5.0
    })

    # Test: Checklist
    iso_mgr.initialize_compliance_checklist(1, '2024')

    logging.info(f"{Icons.SUCCESS} ISO 14064-1 modülü hazır!")

