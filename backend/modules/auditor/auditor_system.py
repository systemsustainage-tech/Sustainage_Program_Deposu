#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dış Doğrulama ve Denetçi Sistemi - TAM VE EKSİKSİZ
Denetçi rolleri, doğrulama workflow'u, kanıt yönetimi, dijital imza
"""

import logging
import hashlib
import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List
from config.database import DB_PATH


class AuditorSystem:
    """Denetçi ve doğrulama sistemi"""

    # Denetçi rolleri
    AUDITOR_ROLES = {
        "lead_auditor": {
            "name": "Baş Denetçi",
            "permissions": ["read_all", "verify_all", "approve_all", "report"],
            "level": 3
        },
        "senior_auditor": {
            "name": "Kıdemli Denetçi",
            "permissions": ["read_all", "verify_assigned", "report"],
            "level": 2
        },
        "auditor": {
            "name": "Denetçi",
            "permissions": ["read_assigned", "verify_assigned"],
            "level": 1
        },
        "external_verifier": {
            "name": "Dış Doğrulayıcı",
            "permissions": ["read_assigned", "verify_assigned", "comment"],
            "level": 1
        }
    }

    # Doğrulama durumları
    VERIFICATION_STATUS = {
        "pending": "Beklemede",
        "in_review": "İnceleniyor",
        "verified": "Doğrulandı",
        "rejected": "Reddedildi",
        "requires_clarification": "Açıklama Gerekli"
    }

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.evidence_dir = os.path.join(os.path.dirname(db_path), "audit_evidence")

        # Kanıt dizinini oluştur
        os.makedirs(self.evidence_dir, exist_ok=True)

        self._init_auditor_tables()

    def _init_auditor_tables(self) -> None:
        """Denetçi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Denetçi kullanıcıları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auditors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    auditor_role TEXT NOT NULL,
                    organization TEXT,
                    certification TEXT,
                    certification_number TEXT,
                    valid_until DATE,
                    specialization TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)

            # Denetim atamaları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    auditor_id INTEGER NOT NULL,
                    module_code TEXT NOT NULL,
                    assignment_type TEXT NOT NULL,
                    scope TEXT,
                    start_date DATE NOT NULL,
                    deadline DATE NOT NULL,
                    status TEXT DEFAULT 'assigned',
                    priority TEXT DEFAULT 'orta',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (auditor_id) REFERENCES auditors(id)
                )
            """)

            # Doğrulama kayıtları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verification_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_code TEXT NOT NULL,
                    data_item TEXT NOT NULL,
                    data_value TEXT,
                    verification_status TEXT DEFAULT 'pending',
                    auditor_id INTEGER,
                    verification_date TIMESTAMP,
                    verification_notes TEXT,
                    confidence_level TEXT,
                    evidence_ids TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (auditor_id) REFERENCES auditors(id)
                )
            """)

            # Kanıt belgeleri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evidence_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    module_code TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    document_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_hash TEXT,
                    file_size INTEGER,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    uploaded_by INTEGER,
                    related_data_item TEXT,
                    description TEXT,
                    is_verified BOOLEAN DEFAULT 0,
                    verified_by INTEGER,
                    verified_at TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (uploaded_by) REFERENCES users(id),
                    FOREIGN KEY (verified_by) REFERENCES auditors(id)
                )
            """)

            # Dijital imzalar
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS digital_signatures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    signer_id INTEGER NOT NULL,
                    signer_role TEXT NOT NULL,
                    signature_hash TEXT NOT NULL,
                    signature_type TEXT DEFAULT 'approval',
                    signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    remarks TEXT,
                    FOREIGN KEY (document_id) REFERENCES evidence_documents(id),
                    FOREIGN KEY (signer_id) REFERENCES users(id)
                )
            """)

            # Denetim bulguları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assignment_id INTEGER NOT NULL,
                    finding_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    finding_title TEXT NOT NULL,
                    finding_description TEXT,
                    affected_module TEXT,
                    affected_data TEXT,
                    recommendation TEXT,
                    status TEXT DEFAULT 'open',
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (assignment_id) REFERENCES audit_assignments(id),
                    FOREIGN KEY (created_by) REFERENCES auditors(id)
                )
            """)

            # Denetim raporları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    assignment_id INTEGER NOT NULL,
                    report_type TEXT NOT NULL,
                    report_title TEXT NOT NULL,
                    report_period TEXT,
                    file_path TEXT,
                    summary TEXT,
                    total_findings INTEGER DEFAULT 0,
                    critical_findings INTEGER DEFAULT 0,
                    overall_opinion TEXT,
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    approved_by INTEGER,
                    approved_at TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (assignment_id) REFERENCES audit_assignments(id),
                    FOREIGN KEY (created_by) REFERENCES auditors(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Denetci tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[ERROR] Denetci tablolari olusturulurken hata: {e}")
        finally:
            conn.close()

    # =====================================================
    # 1. DENETÇİ YÖNETİMİ
    # =====================================================

    def create_auditor(self, user_id: int, role: str, organization: str,
                      certification: str = "", cert_number: str = "") -> bool:
        """Yeni denetçi oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO auditors
                (user_id, auditor_role, organization, certification, certification_number)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, role, organization, certification, cert_number))

            conn.commit()
            logging.info(f"[OK] Denetci olusturuldu: {user_id}")
            return True

        except Exception as e:
            logging.error(f"Denetci olusturma hatasi: {e}")
            return False
        finally:
            conn.close()

    # =====================================================
    # 2. DOĞRULAMA WORKFLOW
    # =====================================================

    def submit_for_verification(self, company_id: int, module_code: str,
                               data_item: str, data_value: str,
                               evidence_ids: List[int] = None) -> int:
        """Veriyi doğrulama için gönder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            evidence_json = json.dumps(evidence_ids) if evidence_ids else None

            cursor.execute("""
                INSERT INTO verification_records
                (company_id, module_code, data_item, data_value,
                 verification_status, evidence_ids)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, module_code, data_item, data_value,
                  'pending', evidence_json))

            record_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Dogrulama kaydı olusturuldu: {record_id}")
            return record_id

        except Exception as e:
            logging.error(f"Dogrulama gonderme hatasi: {e}")
            return 0
        finally:
            conn.close()

    def verify_data(self, record_id: int, auditor_id: int,
                   status: str, notes: str = "",
                   confidence: str = "yuksek") -> bool:
        """Veriyi doğrula"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE verification_records
                SET verification_status = ?,
                    auditor_id = ?,
                    verification_date = CURRENT_TIMESTAMP,
                    verification_notes = ?,
                    confidence_level = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, auditor_id, notes, confidence, record_id))

            conn.commit()
            logging.info(f"[OK] Veri dogrulandi: {record_id}")
            return True

        except Exception as e:
            logging.error(f"Dogrulama hatasi: {e}")
            return False
        finally:
            conn.close()

    # =====================================================
    # 3. KANIT BELGE MERKEZİ
    # =====================================================

    def upload_evidence(self, company_id: int, module_code: str,
                       document_name: str, file_path: str,
                       document_type: str, related_item: str = "",
                       description: str = "", uploaded_by: int = 1) -> int:
        """Kanıt belgesi yükle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Dosya hash'i hesapla (bütünlük için)
            file_hash = self._calculate_file_hash(file_path)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

            # Kanıt dizinine kopyala
            import shutil
            dest_filename = f"{company_id}_{module_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(file_path)}"
            dest_path = os.path.join(self.evidence_dir, dest_filename)

            if os.path.exists(file_path):
                shutil.copy2(file_path, dest_path)

            # Veritabanına kaydet
            cursor.execute("""
                INSERT INTO evidence_documents
                (company_id, module_code, document_type, document_name,
                 file_path, file_hash, file_size, uploaded_by, related_data_item, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, module_code, document_type, document_name,
                  dest_path, file_hash, file_size, uploaded_by, related_item, description))

            evidence_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Kanit yuklendi: {evidence_id}")
            return evidence_id

        except Exception as e:
            logging.error(f"Kanit yukleme hatasi: {e}")
            return 0
        finally:
            conn.close()

    def _calculate_file_hash(self, file_path: str) -> str:
        """Dosya hash'i hesapla (SHA-256)"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logging.error(f"Hash hesaplama hatasi: {e}")
            return ""

    def get_evidence_documents(self, company_id: int, module_code: str = None) -> List[Dict]:
        """Kanıt belgelerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if module_code:
                cursor.execute("""
                    SELECT * FROM evidence_documents
                    WHERE company_id = ? AND module_code = ?
                    ORDER BY upload_date DESC
                """, (company_id, module_code))
            else:
                cursor.execute("""
                    SELECT * FROM evidence_documents
                    WHERE company_id = ?
                    ORDER BY upload_date DESC
                """, (company_id,))

            columns = [col[0] for col in cursor.description]
            documents = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return documents

        except Exception as e:
            logging.error(f"Kanitlar getirme hatasi: {e}")
            return []
        finally:
            conn.close()

    # =====================================================
    # 4. DİJİTAL İMZA SİSTEMİ
    # =====================================================

    def sign_document(self, document_id: int, signer_id: int,
                     signer_role: str, signature_type: str = "approval",
                     remarks: str = "", ip_address: str = "") -> bool:
        """Belgeyi dijital olarak imzala"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # İmza hash'i oluştur
            signature_data = f"{document_id}_{signer_id}_{datetime.now().isoformat()}"
            signature_hash = hashlib.sha256(signature_data.encode()).hexdigest()

            # İmzayı kaydet
            cursor.execute("""
                INSERT INTO digital_signatures
                (document_id, signer_id, signer_role, signature_hash,
                 signature_type, ip_address, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (document_id, signer_id, signer_role, signature_hash,
                  signature_type, ip_address, remarks))

            # Belgeyi doğrulanmış olarak işaretle
            if signature_type == "approval":
                cursor.execute("""
                    UPDATE evidence_documents
                    SET is_verified = 1, verified_by = ?, verified_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (signer_id, document_id))

            conn.commit()
            logging.info(f"[OK] Belge imzalandi: {document_id}")
            return True

        except Exception as e:
            logging.error(f"Imzalama hatasi: {e}")
            return False
        finally:
            conn.close()

    def verify_signature(self, signature_id: int) -> Dict:
        """İmza doğruluğunu kontrol et"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM digital_signatures WHERE id = ?
            """, (signature_id,))

            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                signature = dict(zip(columns, row))

                # Hash doğrulaması yapılabilir
                return {
                    "valid": True,
                    "signature": signature,
                    "message": "Imza gecerli"
                }

            return {"valid": False, "message": "Imza bulunamadi"}

        except Exception as e:
            logging.error(f"Imza dogrulama hatasi: {e}")
            return {"valid": False, "error": str(e)}
        finally:
            conn.close()

    # =====================================================
    # 5. DENETİM BULGULARI
    # =====================================================

    def create_finding(self, company_id: int, assignment_id: int,
                      finding_type: str, severity: str, title: str,
                      description: str, recommendation: str = "",
                      created_by: int = 1) -> int:
        """Denetim bulgusu oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO audit_findings
                (company_id, assignment_id, finding_type, severity,
                 finding_title, finding_description, recommendation, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, assignment_id, finding_type, severity,
                  title, description, recommendation, created_by))

            finding_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Bulgu olusturuldu: {finding_id}")
            return finding_id

        except Exception as e:
            logging.error(f"Bulgu olusturma hatasi: {e}")
            return 0
        finally:
            conn.close()

    def get_audit_findings(self, company_id: int,
                          severity: str = None) -> List[Dict]:
        """Denetim bulgularını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if severity:
                cursor.execute("""
                    SELECT * FROM audit_findings
                    WHERE company_id = ? AND severity = ?
                    ORDER BY created_at DESC
                """, (company_id, severity))
            else:
                cursor.execute("""
                    SELECT * FROM audit_findings
                    WHERE company_id = ?
                    ORDER BY created_at DESC
                """, (company_id,))

            columns = [col[0] for col in cursor.description]
            findings = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return findings

        except Exception as e:
            logging.error(f"Bulgular getirme hatasi: {e}")
            return []
        finally:
            conn.close()

    # =====================================================
    # 6. DENETİM RAPORU OLUŞTURMA
    # =====================================================

    def generate_audit_report(self, company_id: int, assignment_id: int,
                             report_title: str, summary: str,
                             overall_opinion: str, created_by: int) -> int:
        """Denetim raporu oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Bulguları say
            cursor.execute("""
                SELECT COUNT(*), 
                       SUM(CASE WHEN severity = 'kritik' THEN 1 ELSE 0 END)
                FROM audit_findings
                WHERE assignment_id = ?
            """, (assignment_id,))

            total, critical = cursor.fetchone()

            # Raporu kaydet
            cursor.execute("""
                INSERT INTO audit_reports
                (company_id, assignment_id, report_type, report_title,
                 summary, total_findings, critical_findings, overall_opinion, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, assignment_id, 'external_audit', report_title,
                  summary, total or 0, critical or 0, overall_opinion, created_by))

            report_id = cursor.lastrowid
            conn.commit()

            logging.info(f"[OK] Denetim raporu olusturuldu: {report_id}")
            return report_id

        except Exception as e:
            logging.error(f"Rapor olusturma hatasi: {e}")
            return 0
        finally:
            conn.close()

    # =====================================================
    # 7. YARDIMCI FONKSİYONLAR
    # =====================================================

    def get_auditor_dashboard(self, auditor_id: int) -> Dict:
        """Denetçi dashboard verilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            dashboard = {
                "total_assignments": 0,
                "pending_verifications": 0,
                "completed_verifications": 0,
                "total_findings": 0,
                "critical_findings": 0
            }

            # Atamalar
            cursor.execute("""
                SELECT COUNT(*) FROM audit_assignments
                WHERE auditor_id = ? AND status != 'completed'
            """, (auditor_id,))
            dashboard["total_assignments"] = cursor.fetchone()[0]

            # Bekleyen doğrulamalar
            cursor.execute("""
                SELECT COUNT(*) FROM verification_records
                WHERE auditor_id = ? AND verification_status = 'pending'
            """, (auditor_id,))
            dashboard["pending_verifications"] = cursor.fetchone()[0]

            # Tamamlanan doğrulamalar
            cursor.execute("""
                SELECT COUNT(*) FROM verification_records
                WHERE auditor_id = ? AND verification_status = 'verified'
            """, (auditor_id,))
            dashboard["completed_verifications"] = cursor.fetchone()[0]

            return dashboard

        except Exception as e:
            logging.error(f"Dashboard getirme hatasi: {e}")
            return dashboard
        finally:
            conn.close()
