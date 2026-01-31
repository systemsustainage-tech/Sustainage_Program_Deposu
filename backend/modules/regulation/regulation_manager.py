import sqlite3
import logging
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional, Tuple

class RegulationManager:
    """
    Regülasyon Takip Modülü Yöneticisi
    Ulusal ve uluslararası mevzuatı takip eder, uyum tarihlerini hatırlatır.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_tables()
        
    def _init_tables(self):
        """Veritabanı tablolarını oluşturur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Regülasyonlar tablosu
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS regulations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    description TEXT,
                    scope TEXT, -- 'ulusal' veya 'uluslararasi'
                    authority TEXT, -- 'AB', 'TC', 'BM' vb.
                    status TEXT DEFAULT 'active', -- 'active', 'draft', 'repealed'
                    publication_date DATE,
                    effective_date DATE,
                    compliance_deadline DATE,
                    related_sectors TEXT, -- JSON veya CSV
                    source_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Şirket uyum durumu tablosu (Hangi şirket hangi regülasyona ne kadar uyumlu)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS regulation_compliance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    regulation_id INTEGER NOT NULL,
                    compliance_status TEXT DEFAULT 'unknown', -- 'compliant', 'partial', 'non_compliant', 'not_applicable'
                    notes TEXT,
                    last_audit_date DATE,
                    next_audit_date DATE,
                    assigned_to INTEGER, -- User ID
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (regulation_id) REFERENCES regulations(id),
                    FOREIGN KEY (company_id) REFERENCES companies(id),
                    UNIQUE(company_id, regulation_id)
                )
            """)
            
            conn.commit()
        except Exception as e:
            logging.error(f"RegulationManager init_tables error: {e}")
        finally:
            conn.close()

    def add_regulation(self, code: str, title: str, scope: str, authority: str, **kwargs) -> int:
        """Yeni bir regülasyon ekler"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            fields = ["code", "title", "scope", "authority"]
            values = [code, title, scope, authority]
            placeholders = ["?", "?", "?", "?"]
            
            for key, value in kwargs.items():
                if key in ["description", "status", "publication_date", "effective_date", "compliance_deadline", "related_sectors", "source_url"]:
                    fields.append(key)
                    values.append(value)
                    placeholders.append("?")
            
            query = f"INSERT INTO regulations ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"add_regulation error: {e}")
            return 0
        finally:
            conn.close()

    def get_regulations(self, scope: Optional[str] = None, status: str = 'active') -> List[Dict]:
        """Regülasyonları listeler"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            query = "SELECT * FROM regulations WHERE status = ?"
            params = [status]
            
            if scope:
                query += " AND scope = ?"
                params.append(scope)
                
            query += " ORDER BY compliance_deadline ASC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"get_regulations error: {e}")
            return []
        finally:
            conn.close()

    def get_upcoming_deadlines(self, days: int = 90) -> List[Dict]:
        """Yaklaşan uyum tarihlerini getirir"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            target_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute("""
                SELECT * FROM regulations 
                WHERE compliance_deadline BETWEEN ? AND ? 
                AND status = 'active'
                ORDER BY compliance_deadline ASC
            """, (today, target_date))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"get_upcoming_deadlines error: {e}")
            return []
        finally:
            conn.close()
            
    def update_compliance_status(self, company_id: int, regulation_id: int, status: str, notes: str = None) -> bool:
        """Şirketin uyum durumunu günceller"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO regulation_compliance 
                (company_id, regulation_id, compliance_status, notes, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (company_id, regulation_id, status, notes))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"update_compliance_status error: {e}")
            return False
        finally:
            conn.close()

    def get_company_compliance(self, company_id: int) -> List[Dict]:
        """Şirketin regülasyon uyum raporunu getirir"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # LEFT JOIN ile tüm aktif regülasyonları ve varsa şirketin durumunu getir
            cursor.execute("""
                SELECT r.*, 
                       rc.compliance_status, rc.notes, rc.last_audit_date, rc.next_audit_date
                FROM regulations r
                LEFT JOIN regulation_compliance rc ON r.id = rc.regulation_id AND rc.company_id = ?
                WHERE r.status = 'active'
                ORDER BY r.compliance_deadline ASC
            """, (company_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"get_company_compliance error: {e}")
            return []
        finally:
            conn.close()

    def populate_initial_data(self):
        """Başlangıç verilerini yükle (Eğer tablo boşsa)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM regulations")
            if cursor.fetchone()[0] == 0:
                # Örnek veriler
                regulations = [
                    ("EU-CBAM", "Carbon Border Adjustment Mechanism", "uluslararasi", "AB", "AB Sınırda Karbon Düzenleme Mekanizması", "2023-05-16", "2023-10-01", "2026-01-01", "Demir-Çelik,Çimento,Gübre,Alüminyum,Elektrik,Hidrojen"),
                    ("EU-CSRD", "Corporate Sustainability Reporting Directive", "uluslararasi", "AB", "Kurumsal Sürdürülebilirlik Raporlama Direktifi", "2022-12-14", "2024-01-01", "2025-01-01", "Tüm Büyük Şirketler"),
                    ("TR-IKLIM", "İklim Kanunu Taslağı", "ulusal", "TC", "Türkiye İklim Kanunu (Taslak)", "2024-01-01", "2024-06-01", "2025-01-01", "Tüm Sektörler"),
                    ("EU-EUDR", "EU Deforestation Regulation", "uluslararasi", "AB", "AB Ormansızlaşma Yönetmeliği", "2023-06-29", "2023-06-29", "2024-12-30", "Tarım,Orman,Mobilya,Kağıt"),
                    ("TR-SIFIR-ATIK", "Sıfır Atık Yönetmeliği", "ulusal", "TC", "Sıfır Atık Yönetimi ve Uygulamaları", "2019-07-12", "2019-07-12", "2020-01-01", "Tüm Sektörler")
                ]
                
                for reg in regulations:
                    self.add_regulation(
                        code=reg[0],
                        title=reg[1],
                        scope=reg[2],
                        authority=reg[3],
                        description=reg[4],
                        publication_date=reg[5],
                        effective_date=reg[6],
                        compliance_deadline=reg[7],
                        related_sectors=reg[8]
                    )
                logging.info("RegulationManager: Initial data populated.")
        except Exception as e:
            logging.error(f"populate_initial_data error: {e}")
        finally:
            conn.close()
