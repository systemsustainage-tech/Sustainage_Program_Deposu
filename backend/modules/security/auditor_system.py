#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dış Doğrulama (External Auditor) Sistemi
Denetçi hesapları, belge merkezi, güvence raporları
"""

import logging
import hashlib
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class AuditorSystem:
    """Dış denetçi sistem yöneticisi"""

    # Denetçi yetki seviyeleri
    AUDITOR_LEVELS = {
        'read_only': 'Sadece Okuma',
        'reviewer': 'İnceleme ve Yorum',
        'verifier': 'Doğrulama',
        'assurance': 'Güvence Sağlama'
    }

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self) -> None:
        """Denetçi tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Denetçi hesapları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auditor_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    auditor_name TEXT NOT NULL,
                    auditor_company TEXT NOT NULL,
                    auditor_email TEXT UNIQUE NOT NULL,
                    auditor_phone TEXT,
                    auditor_level TEXT NOT NULL,
                    certification TEXT,
                    specialization TEXT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    access_start_date TEXT,
                    access_end_date TEXT,
                    created_by INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_login TEXT
                )
            """)

            # Denetçi erişim logları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auditor_access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    auditor_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    module TEXT,
                    document_id INTEGER,
                    details TEXT,
                    ip_address TEXT,
                    access_time TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (auditor_id) REFERENCES auditor_accounts(id)
                )
            """)

            # Belge merkezi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auditor_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    document_name TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    document_category TEXT,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    version TEXT DEFAULT '1.0',
                    is_verified INTEGER DEFAULT 0,
                    verified_by INTEGER,
                    verification_date TEXT,
                    verification_notes TEXT,
                    shared_with_auditor INTEGER DEFAULT 0,
                    uploaded_by INTEGER,
                    uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (verified_by) REFERENCES auditor_accounts(id)
                )
            """)

            # Denetçi yorumları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auditor_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    auditor_id INTEGER NOT NULL,
                    document_id INTEGER,
                    module_name TEXT,
                    comment_type TEXT NOT NULL,
                    comment_text TEXT NOT NULL,
                    severity TEXT,
                    status TEXT DEFAULT 'open',
                    response TEXT,
                    responded_by INTEGER,
                    responded_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (auditor_id) REFERENCES auditor_accounts(id),
                    FOREIGN KEY (document_id) REFERENCES auditor_documents(id)
                )
            """)

            # Güvence raporları
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assurance_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    auditor_id INTEGER NOT NULL,
                    report_year INTEGER NOT NULL,
                    report_type TEXT NOT NULL,
                    assurance_level TEXT NOT NULL,
                    scope TEXT,
                    findings TEXT,
                    recommendations TEXT,
                    assurance_statement TEXT,
                    report_file_path TEXT,
                    status TEXT DEFAULT 'draft',
                    issued_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    FOREIGN KEY (auditor_id) REFERENCES auditor_accounts(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Auditor sistem tabloları hazır")

        except Exception as e:
            logging.error(f"[HATA] Auditor tablo oluşturma: {e}")
            conn.rollback()
        finally:
            conn.close()

    def create_auditor_account(self, auditor_name: str, auditor_company: str,
                              auditor_email: str, username: str, password: str,
                              auditor_level: str, certification: str = None,
                              specialization: str = None,
                              access_start: str = None, access_end: str = None,
                              created_by: int = None) -> Tuple[bool, str]:
        """
        Denetçi hesabı oluştur
        
        Returns:
            Tuple[bool, str]: (Başarı, mesaj/hata)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Şifreyi hashle
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute("""
                INSERT INTO auditor_accounts 
                (auditor_name, auditor_company, auditor_email, username, password_hash,
                 auditor_level, certification, specialization, access_start_date,
                 access_end_date, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (auditor_name, auditor_company, auditor_email, username, password_hash,
                  auditor_level, certification, specialization, access_start, access_end,
                  created_by))

            conn.commit()
            return True, f"Denetçi hesabı oluşturuldu: {username}"

        except sqlite3.IntegrityError:
            return False, "Bu email veya kullanıcı adı zaten kayıtlı"
        except Exception as e:
            conn.rollback()
            return False, f"Hesap oluşturma hatası: {e}"
        finally:
            conn.close()

    def authenticate_auditor(self, username: str, password: str) -> Optional[Dict]:
        """Denetçi girişi doğrula"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute("""
                SELECT id, auditor_name, auditor_company, auditor_email, auditor_level,
                       certification, is_active
                FROM auditor_accounts
                WHERE username = ? AND password_hash = ? AND is_active = 1
            """, (username, password_hash))

            row = cursor.fetchone()

            if row:
                # Son giriş zamanını güncelle
                cursor.execute("""
                    UPDATE auditor_accounts SET last_login = ? WHERE id = ?
                """, (datetime.now().isoformat(), row[0]))
                conn.commit()

                return {
                    'id': row[0],
                    'name': row[1],
                    'company': row[2],
                    'email': row[3],
                    'level': row[4],
                    'certification': row[5]
                }

            return None

        finally:
            conn.close()

    def log_auditor_access(self, auditor_id: int, action: str,
                          module: str = None, document_id: int = None,
                          details: str = None):
        """Denetçi erişimini logla"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO auditor_access_log
                (auditor_id, action, module, document_id, details)
                VALUES (?, ?, ?, ?, ?)
            """, (auditor_id, action, module, document_id, details))

            conn.commit()
        except Exception as e:
            logging.error(f"Auditor log hatası: {e}")
            conn.rollback()
        finally:
            conn.close()

    def share_document_with_auditor(self, document_id: int) -> bool:
        """Belgeyi denetçiyle paylaş"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE auditor_documents
                SET shared_with_auditor = 1
                WHERE id = ?
            """, (document_id,))

            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Belge paylaşma hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def add_auditor_comment(self, auditor_id: int, comment_type: str,
                           comment_text: str, module_name: str = None,
                           document_id: int = None, severity: str = 'info') -> int:
        """Denetçi yorumu ekle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO auditor_comments
                (auditor_id, document_id, module_name, comment_type, comment_text, severity)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (auditor_id, document_id, module_name, comment_type, comment_text, severity))

            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"Yorum ekleme hatası: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

    def get_auditor_comments(self, status: str = None) -> List[Dict]:
        """Denetçi yorumlarını getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if status:
                cursor.execute("""
                    SELECT c.id, a.auditor_name, c.comment_type, c.comment_text,
                           c.severity, c.status, c.created_at
                    FROM auditor_comments c
                    JOIN auditor_accounts a ON c.auditor_id = a.id
                    WHERE c.status = ?
                    ORDER BY c.id DESC
                """, (status,))
            else:
                cursor.execute("""
                    SELECT c.id, a.auditor_name, c.comment_type, c.comment_text,
                           c.severity, c.status, c.created_at
                    FROM auditor_comments c
                    JOIN auditor_accounts a ON c.auditor_id = a.id
                    ORDER BY c.id DESC
                """)

            return [{'id': r[0], 'auditor': r[1], 'type': r[2], 'text': r[3],
                    'severity': r[4], 'status': r[5], 'date': r[6]}
                   for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_auditor_list(self) -> List[Dict]:
        """Denetçi listesini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, auditor_name, auditor_company, auditor_email,
                       auditor_level, certification, is_active, last_login
                FROM auditor_accounts
                ORDER BY auditor_name
            """)

            return [{'id': r[0], 'name': r[1], 'company': r[2], 'email': r[3],
                    'level': r[4], 'certification': r[5], 'is_active': r[6],
                    'last_login': r[7]} for r in cursor.fetchall()]
        finally:
            conn.close()

    def create_assurance_report(self, company_id: int, auditor_id: int,
                               year: int, report_type: str, assurance_level: str,
                               scope: str = None, findings: str = None,
                               recommendations: str = None) -> int:
        """Güvence raporu oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO assurance_reports
                (company_id, auditor_id, report_year, report_type, assurance_level,
                 scope, findings, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (company_id, auditor_id, year, report_type, assurance_level,
                  scope, findings, recommendations))

            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"Güvence raporu oluşturma hatası: {e}")
            conn.rollback()
            return 0
        finally:
            conn.close()

