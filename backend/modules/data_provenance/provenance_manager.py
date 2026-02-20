#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veri Kaynağı ve İzlenebilirlik (Data Provenance) Sistemi - TAM VE EKSİKSİZ
Kaynak belgeleme, metodoloji, varsayımlar, data owner, audit trail
"""

import logging
import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional
try:
    from backend.core.base_manager import BaseTenantManager
    from config.database import DB_PATH
except ImportError:
    from backend.core.base_manager import BaseTenantManager
    from backend.config.database import DB_PATH


class DataProvenanceManager(BaseTenantManager):
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

    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        super().__init__(db_path, company_id)
        self._init_provenance_tables()

    def _init_provenance_tables(self) -> None:
        """Data provenance tablolarını oluştur"""
        try:
            # Veri kaynağı kayıtları
            self.execute_update("""
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
            """, skip_tenant_filter=True)

            # Veri toplama metodolojisi
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS data_collection_methodology (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    data_source_id INTEGER NOT NULL,
                    method_type TEXT NOT NULL,
                    method_description TEXT NOT NULL,
                    measurement_unit TEXT,
                    frequency TEXT,
                    sample_size INTEGER,
                    confidence_level REAL,
                    limitations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id)
                )
            """, skip_tenant_filter=True)

            # Varsayımlar ve hesaplamalar
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS data_assumptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    data_source_id INTEGER NOT NULL,
                    assumption_type TEXT NOT NULL,
                    assumption_description TEXT NOT NULL,
                    justification TEXT,
                    impact_level TEXT DEFAULT 'medium',
                    alternative_scenarios TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id)
                )
            """, skip_tenant_filter=True)

            # Hesaplama detayları
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS calculation_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    data_source_id INTEGER NOT NULL,
                    calculation_formula TEXT NOT NULL,
                    input_parameters TEXT NOT NULL,
                    constants_used TEXT,
                    calculation_steps TEXT,
                    result_value TEXT,
                    result_unit TEXT,
                    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    calculated_by INTEGER,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id)
                )
            """, skip_tenant_filter=True)

            # Veri sahipleri (data owners)
            self.execute_update("""
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
            """, skip_tenant_filter=True)

            # Detaylı değişiklik geçmişi (audit trail)
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS data_change_audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
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
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (changed_by) REFERENCES users(id)
                )
            """, skip_tenant_filter=True)

            # Veri doğrulama kayıtları
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS data_verification_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    data_source_id INTEGER NOT NULL,
                    verified_by INTEGER NOT NULL,
                    verification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verification_method TEXT,
                    verification_result TEXT DEFAULT 'approved',
                    verification_notes TEXT,
                    evidence_document_path TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (data_source_id) REFERENCES data_sources(id),
                    FOREIGN KEY (verified_by) REFERENCES users(id)
                )
            """, skip_tenant_filter=True)

            logging.info("[OK] Data provenance tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[ERROR] Provenance tablolari olusturulurken hata: {e}")

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
        """
        try:
            cid = self._ensure_context(company_id)
            data = {
                'data_type': data_type,
                'data_identifier': data_identifier,
                'source_type': source_type,
                'source_name': source_name,
                'source_url': source_url,
                'source_document_path': source_document,
                'data_owner_id': data_owner_id,
                'data_quality_level': quality_level,
                'notes': notes,
                'collection_date': date.today().isoformat()
            }
            
            source_id = self.insert('data_sources', data, company_id=cid)
            logging.info(f"[OK] Veri kaynagi belgelendi: {data_identifier}")
            return source_id

        except Exception as e:
            logging.error(f"Kaynak belgeleme hatasi: {e}")
            return 0

    # =====================================================
    # 2. METODOLOJİ KAYDI
    # =====================================================

    def record_collection_methodology(self, company_id: int, data_source_id: int,
                                     method_type: str, description: str,
                                     unit: str = "", frequency: str = "",
                                     sample_size: int = None,
                                     confidence: float = None,
                                     limitations: str = "") -> int:
        """
        Veri toplama metodolojisini kaydet
        """
        try:
            cid = self._ensure_context(company_id)
            query = """
                INSERT INTO data_collection_methodology
                (company_id, data_source_id, method_type, method_description, measurement_unit,
                 frequency, sample_size, confidence_level, limitations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (cid, data_source_id, method_type, description, unit, frequency,
                      sample_size, confidence, limitations)
            
            method_id = self.execute_update(query, params, company_id=cid)
            logging.info(f"[OK] Metodoloji kaydedildi: {method_type}")
            return method_id

        except Exception as e:
            logging.error(f"Metodoloji kayit hatasi: {e}")
            return 0

    # =====================================================
    # 3. VARSAYIMLAR VE HESAPLAMALAR
    # =====================================================

    def record_assumption(self, company_id: int, data_source_id: int, assumption_type: str,
                         description: str, justification: str = "",
                         impact: str = "medium", created_by: int = None) -> int:
        """
        Varsayımı kaydet
        """
        try:
            cid = self._ensure_context(company_id)
            query = """
                INSERT INTO data_assumptions
                (company_id, data_source_id, assumption_type, assumption_description,
                 justification, impact_level, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (cid, data_source_id, assumption_type, description, justification,
                      impact, created_by)
            
            assumption_id = self.execute_update(query, params, company_id=cid)
            logging.info(f"[OK] Varsayim kaydedildi: {assumption_type}")
            return assumption_id

        except Exception as e:
            logging.error(f"Varsayim kayit hatasi: {e}")
            return 0

    def record_calculation(self, company_id: int, data_source_id: int, formula: str,
                          inputs: Dict, constants: Dict = None,
                          steps: str = "", result: float = None,
                          unit: str = "", calculated_by: int = None) -> int:
        """
        Hesaplama detaylarını kaydet
        """
        try:
            cid = self._ensure_context(company_id)
            query = """
                INSERT INTO calculation_details
                (company_id, data_source_id, calculation_formula, input_parameters,
                 constants_used, calculation_steps, result_value, result_unit,
                 calculated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (cid, data_source_id, formula, json.dumps(inputs),
                      json.dumps(constants) if constants else None, steps,
                      str(result) if result else None, unit, calculated_by)
            
            calc_id = self.execute_update(query, params, company_id=cid)
            logging.info("[OK] Hesaplama kaydedildi")
            return calc_id

        except Exception as e:
            logging.error(f"Hesaplama kayit hatasi: {e}")
            return 0

    # =====================================================
    # 4. VERİ SAHİBİ (DATA OWNER) ATAMA
    # =====================================================

    def assign_data_owner(self, company_id: int, data_category: str,
                         primary_owner_id: int, backup_owner_id: int = None,
                         responsibilities: str = "") -> int:
        """
        Veri sahibi ata
        """
        try:
            cid = self._ensure_context(company_id)
            data = {
                'data_category': data_category,
                'primary_owner_id': primary_owner_id,
                'backup_owner_id': backup_owner_id,
                'responsibilities': responsibilities
            }
            ownership_id = self.insert('data_ownership', data, company_id=cid)
            logging.info(f"[OK] Veri sahibi atandi: {data_category}")
            return ownership_id

        except Exception as e:
            logging.error(f"Veri sahibi atama hatasi: {e}")
            return 0

    # =====================================================
    # 5. DEĞİŞİKLİK GEÇMİŞİ (AUDIT TRAIL)
    # =====================================================

    def log_data_change(self, company_id: int, table_name: str, record_id: int,
                       field_name: str, old_value: str, new_value: str,
                       change_type: str, reason: str = "",
                       changed_by: int = None, ip_address: str = None) -> int:
        """
        Veri değişikliğini kaydet
        """
        try:
            cid = self._ensure_context(company_id)
            query = """
                INSERT INTO data_change_audit_trail
                (company_id, table_name, record_id, field_name, old_value, new_value,
                 change_type, change_reason, changed_by, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (cid, table_name, record_id, field_name, old_value, new_value,
                      change_type, reason, changed_by, ip_address)
            
            trail_id = self.execute_update(query, params, company_id=cid)
            return trail_id

        except Exception as e:
            logging.error(f"Audit trail kayit hatasi: {e}")
            return 0

    def get_change_history(self, company_id: int, table_name: str, record_id: int) -> List[Dict]:
        """Bir kaydın değişiklik geçmişini getir"""
        try:
            cid = self._ensure_context(company_id)
            query = """
                SELECT field_name, old_value, new_value, change_type,
                       change_reason, changed_by, changed_at
                FROM data_change_audit_trail
                WHERE table_name = ? AND record_id = ? AND company_id = ?
                ORDER BY changed_at DESC
            """
            rows = self.execute_query(query, (table_name, record_id, cid), company_id=cid)

            changes = []
            for row in rows:
                changes.append({
                    "field": row['field_name'],
                    "old_value": row['old_value'],
                    "new_value": row['new_value'],
                    "type": row['change_type'],
                    "reason": row['change_reason'],
                    "changed_by": row['changed_by'],
                    "changed_at": row['changed_at']
                })
            return changes

        except Exception as e:
            logging.error(f"Gecmis getirme hatasi: {e}")
            return []

    # =====================================================
    # 6. VERİ DOĞRULAMA
    # =====================================================

    def verify_data(self, company_id: int, data_source_id: int, verified_by: int,
                   method: str, result: str = "approved",
                   notes: str = "", evidence_path: str = None) -> int:
        """
        Veriyi doğrula
        """
        try:
            cid = self._ensure_context(company_id)
            # 1. Verification kaydı
            query1 = """
                INSERT INTO data_verification_records
                (company_id, data_source_id, verified_by, verification_method,
                 verification_result, verification_notes, evidence_document_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params1 = (cid, data_source_id, verified_by, method, result, notes, evidence_path)
            verification_id = self.execute_update(query1, params1, company_id=cid)

            # 2. Kalite seviyesi güncellemesi
            query2 = """
                UPDATE data_sources
                SET data_quality_level = ?
                WHERE id = ? AND company_id = ?
            """
            quality_level = "verified" if result == "approved" else "unverified"
            self.execute_update(query2, (quality_level, data_source_id, cid), company_id=cid)

            logging.info(f"[OK] Veri dogrulandi: {result}")
            return verification_id

        except Exception as e:
            logging.error(f"Dogrulama hatasi: {e}")
            return 0
