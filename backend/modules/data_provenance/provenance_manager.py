#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Kaynağı ve İzlenebilirlik (Data Provenance) Sistemi - TAM VE EKSİKSİZ
Kaynak belgeleme, metodoloji, varsayımlar, data owner, audit trail
"""

import logging
import json
import os
import sqlite3
from typing import Dict, List
from config.database import DB_PATH


class DataProvenanceManager:
    """Veri kaynağı ve izlenebilirlik yöneticisi"""

    # Veri kaynak tipleri
    SOURCE_TYPES = {
        "internal_system": "İç Sistem",
        "manual_entry": "Manuel Giriş",
        "excel_import": "Excel İçe Aktarım",
        "api_integration": "API Entegrasyonu",
        "sensor_iot": "Sensör/IoT Cihazı",
        "third_party": "Üçüncü Taraf Sağlayıcı",
        "audit_report": "Denetim Raporu",
        "invoice_document": "Fatura/Belge",
        "survey": "Anket",
        "calculation": "Hesaplama"
    }

    # Veri toplama metodolojileri
    DATA_COLLECTION_METHODS = {
        "direct_measurement": "Doğrudan Ölçüm",
        "estimation": "Tahmin",
        "industry_average": "Sektör Ortalaması",
        "emission_factor": "Emisyon Faktörü",
        "survey_response": "Anket Yanıtı",
        "formula_calculation": "Formül Hesaplaması",
        "aggregation": "Toplama/Birleştirme",
        "extrapolation": "Ekstrapolasyon"
    }

    # Veri kalite seviyeleri
    DATA_QUALITY_LEVELS = {
        "verified": "Doğrulanmış",
        "audited": "Denetlenmiş",
        "estimated": "Tahmin Edilen",
        "unverified": "Doğrulanmamış"
    }

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self._init_provenance_tables()

    def _init_provenance_tables(self) -> None:
        """Data provenance tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Veri kaynağı kayıtları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    data_type TEXT NOT NULL,
                    data_identifier TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    source_url TEXT,
                    source_document_path TEXT,
                    collection_date DATE,
                    data_owner_id INTEGER,
                    data_quality_level TEXT DEFAULT 'unverified',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (data_owner_id) REFERENCES users(id)
                )
            """)

            # Veri toplama metodolojisi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_collection_methodology (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_source_id INTEGER NOT NULL,
                    method_type TEXT NOT NULL,
                    method_description TEXT NOT NULL,
                    measurement_unit TEXT,
                    frequency TEXT,
                    sample_size INTEGER,
                    confidence_level REAL,
                    limitations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id)
                )
            """)

            # Varsayımlar ve hesaplamalar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_assumptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_source_id INTEGER NOT NULL,
                    assumption_type TEXT NOT NULL,
                    assumption_description TEXT NOT NULL,
                    justification TEXT,
                    impact_level TEXT DEFAULT 'medium',
                    alternative_scenarios TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id)
                )
            """)

            # Hesaplama detayları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calculation_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_source_id INTEGER NOT NULL,
                    calculation_formula TEXT NOT NULL,
                    input_parameters TEXT NOT NULL,
                    constants_used TEXT,
                    calculation_steps TEXT,
                    result_value TEXT,
                    result_unit TEXT,
                    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    calculated_by INTEGER,
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id)
                )
            """)

            # Veri sahipleri (data owners)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_ownership (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    data_category TEXT NOT NULL,
                    primary_owner_id INTEGER NOT NULL,
                    backup_owner_id INTEGER,
                    responsibilities TEXT,
                    last_review_date DATE,
                    next_review_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (primary_owner_id) REFERENCES users(id),
                    FOREIGN KEY (backup_owner_id) REFERENCES users(id)
                )
            """)

            # Detaylı değişiklik geçmişi (audit trail)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_change_audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    record_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    change_type TEXT NOT NULL,
                    change_reason TEXT,
                    changed_by INTEGER,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    session_id TEXT,
                    FOREIGN KEY (changed_by) REFERENCES users(id)
                )
            """)

            # Veri doğrulama kayıtları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_verification_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_source_id INTEGER NOT NULL,
                    verified_by INTEGER NOT NULL,
                    verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verification_method TEXT,
                    verification_result TEXT DEFAULT 'approved',
                    verification_notes TEXT,
                    evidence_document_path TEXT,
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id),
                    FOREIGN KEY (verified_by) REFERENCES users(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Data provenance tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[ERROR] Provenance tablolari olusturulurken hata: {e}")
        finally:
            conn.close()

    # =====================================================
    # 1. KAYNAK BELGELEME
    # =====================================================

    def document_data_source(self, company_id: int, data_type: str,
                            data_identifier: str, source_type: str,
                            source_name: str, data_owner_id: int = None,
                            source_url: str = None,
                            source_document: str = None,
                            quality_level: str = "unverified",
                            notes: str = "") -> int:
        """
        Veri kaynağını belgele
        
        Args:
            data_type: "carbon_emission", "energy_consumption", "water_usage", vb.
            data_identifier: Verinin benzersiz tanımlayıcısı (örn: "scope1_2024")
            source_type: "manual_entry", "excel_import", "api_integration", vb.
            source_name: Kaynak adı (örn: "Fatura No: 12345", "Sensör ID: S001")
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_sources
                (company_id, data_type, data_identifier, source_type, source_name,
                 source_url, source_document_path, collection_date, data_owner_id,
                 data_quality_level, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, DATE('now'), ?, ?, ?)
            """, (company_id, data_type, data_identifier, source_type, source_name,
                  source_url, source_document, data_owner_id, quality_level, notes))

            source_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Veri kaynagi belgelendi: {data_identifier}")
            return source_id

        except Exception as e:
            logging.error(f"Kaynak belgeleme hatasi: {e}")
            return 0
        finally:
            conn.close()

    # =====================================================
    # 2. METODOLOJİ KAYDI
    # =====================================================

    def record_collection_methodology(self, data_source_id: int,
                                     method_type: str, description: str,
                                     unit: str = "", frequency: str = "",
                                     sample_size: int = None,
                                     confidence: float = None,
                                     limitations: str = "") -> int:
        """
        Veri toplama metodolojisini kaydet
        
        Args:
            method_type: "direct_measurement", "estimation", "emission_factor", vb.
            description: Metodoloji açıklaması
            unit: Ölçüm birimi
            frequency: Toplama sıklığı (günlük, aylık, vb.)
            confidence: Güven seviyesi (0.0-1.0)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_collection_methodology
                (data_source_id, method_type, method_description, measurement_unit,
                 frequency, sample_size, confidence_level, limitations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data_source_id, method_type, description, unit, frequency,
                  sample_size, confidence, limitations))

            method_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Metodoloji kaydedildi: {method_type}")
            return method_id

        except Exception as e:
            logging.error(f"Metodoloji kayit hatasi: {e}")
            return 0
        finally:
            conn.close()

    # =====================================================
    # 3. VARSAYIMLAR VE HESAPLAMALAR
    # =====================================================

    def record_assumption(self, data_source_id: int, assumption_type: str,
                         description: str, justification: str = "",
                         impact: str = "medium", created_by: int = None) -> int:
        """
        Varsayımı kaydet
        
        Args:
            assumption_type: "emission_factor", "conversion_rate", "estimation_basis", vb.
            description: Varsayım açıklaması
            justification: Gerekçe
            impact: "low", "medium", "high"
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_assumptions
                (data_source_id, assumption_type, assumption_description,
                 justification, impact_level, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data_source_id, assumption_type, description, justification,
                  impact, created_by))

            assumption_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Varsayim kaydedildi: {assumption_type}")
            return assumption_id

        except Exception as e:
            logging.error(f"Varsayim kayit hatasi: {e}")
            return 0
        finally:
            conn.close()

    def record_calculation(self, data_source_id: int, formula: str,
                          inputs: Dict, constants: Dict = None,
                          steps: str = "", result: float = None,
                          unit: str = "", calculated_by: int = None) -> int:
        """
        Hesaplama detaylarını kaydet
        
        Args:
            formula: Hesaplama formülü (örn: "Scope 1 = Fuel * Emission Factor")
            inputs: Girdi parametreleri {"fuel_amount": 1000, "emission_factor": 2.5}
            constants: Sabitler {"conversion_factor": 3.6}
            steps: Hesaplama adımları
            result: Sonuç değeri
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO calculation_details
                (data_source_id, calculation_formula, input_parameters,
                 constants_used, calculation_steps, result_value, result_unit,
                 calculated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data_source_id, formula, json.dumps(inputs),
                  json.dumps(constants) if constants else None, steps,
                  str(result) if result else None, unit, calculated_by))

            calc_id = cursor.lastrowid
            conn.commit()

            logging.info("[OK] Hesaplama kaydedildi")
            return calc_id

        except Exception as e:
            logging.error(f"Hesaplama kayit hatasi: {e}")
            return 0
        finally:
            conn.close()

    # =====================================================
    # 4. VERİ SAHİBİ (DATA OWNER) ATAMA
    # =====================================================

    def assign_data_owner(self, company_id: int, data_category: str,
                         primary_owner_id: int, backup_owner_id: int = None,
                         responsibilities: str = "") -> int:
        """
        Veri sahibi ata
        
        Args:
            data_category: "carbon_data", "water_data", "hr_data", vb.
            primary_owner_id: Ana veri sahibi (user ID)
            backup_owner_id: Yedek veri sahibi (user ID)
            responsibilities: Sorumluluklar
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_ownership
                (company_id, data_category, primary_owner_id, backup_owner_id,
                 responsibilities)
                VALUES (?, ?, ?, ?, ?)
            """, (company_id, data_category, primary_owner_id, backup_owner_id,
                  responsibilities))

            ownership_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Veri sahibi atandi: {data_category}")
            return ownership_id

        except Exception as e:
            logging.error(f"Veri sahibi atama hatasi: {e}")
            return 0
        finally:
            conn.close()

    # =====================================================
    # 5. DEĞİŞİKLİK GEÇMİŞİ (AUDIT TRAIL)
    # =====================================================

    def log_data_change(self, table_name: str, record_id: int,
                       field_name: str, old_value: str, new_value: str,
                       change_type: str, reason: str = "",
                       changed_by: int = None, ip_address: str = None) -> int:
        """
        Veri değişikliğini kaydet
        
        Args:
            table_name: Tablo adı
            record_id: Kayıt ID
            field_name: Alan adı
            old_value: Eski değer
            new_value: Yeni değer
            change_type: "insert", "update", "delete"
            reason: Değişiklik nedeni
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_change_audit_trail
                (table_name, record_id, field_name, old_value, new_value,
                 change_type, change_reason, changed_by, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (table_name, record_id, field_name, old_value, new_value,
                  change_type, reason, changed_by, ip_address))

            trail_id = cursor.lastrowid
            conn.commit()

            return trail_id

        except Exception as e:
            logging.error(f"Audit trail kayit hatasi: {e}")
            return 0
        finally:
            conn.close()

    def get_change_history(self, table_name: str, record_id: int) -> List[Dict]:
        """Bir kaydın değişiklik geçmişini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT field_name, old_value, new_value, change_type,
                       change_reason, changed_by, changed_at
                FROM data_change_audit_trail
                WHERE table_name = ? AND record_id = ?
                ORDER BY changed_at DESC
            """, (table_name, record_id))

            changes = []
            for row in cursor.fetchall():
                changes.append({
                    "field": row[0],
                    "old_value": row[1],
                    "new_value": row[2],
                    "type": row[3],
                    "reason": row[4],
                    "changed_by": row[5],
                    "changed_at": row[6]
                })

            conn.close()
            return changes

        except Exception as e:
            logging.error(f"Gecmis getirme hatasi: {e}")
            return []

    # =====================================================
    # 6. VERİ DOĞRULAMA
    # =====================================================

    def verify_data(self, data_source_id: int, verified_by: int,
                   method: str, result: str = "approved",
                   notes: str = "", evidence_path: str = None) -> int:
        """
        Veriyi doğrula
        
        Args:
            method: Doğrulama yöntemi
            result: "approved", "rejected", "conditional"
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO data_verification_records
                (data_source_id, verified_by, verification_method,
                 verification_result, verification_notes, evidence_document_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data_source_id, verified_by, method, result, notes, evidence_path))

            verification_id = cursor.lastrowid

            # Veri kalite seviyesini güncelle
            cursor.execute("""
                UPDATE data_sources
                SET data_quality_level = ?
                WHERE id = ?
            """, ("verified" if result == "approved" else "unverified", data_source_id))

            conn.commit()

            logging.info(f"[OK] Veri dogrulandi: {result}")
            return verification_id

        except Exception as e:
            logging.error(f"Dogrulama hatasi: {e}")
            return 0
        finally:
            conn.close()

    # =====================================================
    # 7. RAPOR VE SORGULAR
    # =====================================================

    def get_data_provenance_report(self, data_source_id: int) -> Dict:
        """Bir veri için tam provenance raporu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            report = {}

            # Kaynak bilgileri
            cursor.execute("""
                SELECT data_type, data_identifier, source_type, source_name,
                       source_url, collection_date, data_quality_level, notes
                FROM data_sources WHERE id = ?
            """, (data_source_id,))

            row = cursor.fetchone()
            if row:
                report["source"] = {
                    "type": row[0],
                    "identifier": row[1],
                    "source_type": row[2],
                    "source_name": row[3],
                    "url": row[4],
                    "collection_date": row[5],
                    "quality": row[6],
                    "notes": row[7]
                }

            # Metodoloji
            cursor.execute("""
                SELECT method_type, method_description, measurement_unit
                FROM data_collection_methodology WHERE data_source_id = ?
            """, (data_source_id,))

            row = cursor.fetchone()
            if row:
                report["methodology"] = {
                    "type": row[0],
                    "description": row[1],
                    "unit": row[2]
                }

            # Varsayımlar
            cursor.execute("""
                SELECT COUNT(*) FROM data_assumptions WHERE data_source_id = ?
            """, (data_source_id,))

            report["assumptions_count"] = cursor.fetchone()[0]

            # Hesaplamalar
            cursor.execute("""
                SELECT calculation_formula, result_value
                FROM calculation_details WHERE data_source_id = ?
                ORDER BY calculation_date DESC LIMIT 1
            """, (data_source_id,))

            row = cursor.fetchone()
            if row:
                report["calculation"] = {
                    "formula": row[0],
                    "result": row[1]
                }

            # Doğrulama
            cursor.execute("""
                SELECT verification_result, verification_date
                FROM data_verification_records WHERE data_source_id = ?
                ORDER BY verification_date DESC LIMIT 1
            """, (data_source_id,))

            row = cursor.fetchone()
            if row:
                report["verification"] = {
                    "status": row[0],
                    "date": row[1]
                }

            conn.close()
            return report

        except Exception as e:
            logging.error(f"Rapor olusturma hatasi: {e}")
            return {}
