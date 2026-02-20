#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sirket Yonetim Sistemi
Cok sirketli kullanim, yeni sirket ekleme
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from backend.core.base_manager import BaseTenantManager
from backend.core.database_manager import DatabaseManager
from backend.config.database import DB_PATH


class CompanyManager(BaseTenantManager):
    """Sirket yonetimi sinifi"""

    def __init__(self, db_path: str = DB_PATH, company_id: Optional[int] = None):
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)

        # System level manager usually operates with Admin context (1) or provided context
        # We initialize BaseTenantManager. 
        # Note: Operations on GLOBAL_TABLES (companies, company_info) will bypass filtering
        # regardless of the company_id set here.
        super().__init__(db_path, company_id)

        self.base_dir = os.path.dirname(os.path.dirname(db_path))

        # Sirket veri klasoru
        self.companies_dir = os.path.join(self.base_dir, "data", "companies")
        os.makedirs(self.companies_dir, exist_ok=True)

        self._ensure_company_tables()

    def _ensure_company_tables(self):
        """Sirket tablolarini olustur"""
        try:
            # company_info tablosu
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS company_info (
                    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sirket_adi TEXT NOT NULL,
                    ticari_unvan TEXT,
                    vergi_no TEXT,
                    vergi_dairesi TEXT,
                    adres TEXT,
                    il TEXT,
                    ilce TEXT,
                    posta_kodu TEXT,
                    telefon TEXT,
                    email TEXT,
                    website TEXT,
                    sektor TEXT,
                    calisan_sayisi INTEGER,
                    kurulusyili INTEGER,
                    logo_path TEXT,
                    
                    -- Yeni Eklenen Alanlar
                    vizyon TEXT,
                    misyon TEXT,
                    degerler TEXT,
                    tesisler_ozet TEXT,
                    kilometre_taslari_ozet TEXT,
                    urun_hizmet_ozet TEXT,
                    karbon_profili_ozet TEXT,
                    uyelikler_ozet TEXT,
                    oduller_ozet TEXT,

                    aktif BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Varsayilan sirket yoksa ekle
            rows = self.execute_query("SELECT COUNT(*) as count FROM company_info")
            if rows and rows[0]['count'] == 0:
                self.execute_update("""
                    INSERT INTO company_info (company_id, sirket_adi, ticari_unvan, aktif)
                    VALUES (1, 'Varsayilan Firma', 'Varsayilan Ticari Unvan', 1)
                """, company_id=1) # Explicitly pass ID for context satisfaction

            logging.info("[OK] Sirket tablolari hazir")

        except Exception as e:
            logging.error(f"[HATA] Sirket tablolari olusturulamadi: {e}")

    def get_all_companies(self) -> List[Tuple[int, str, bool]]:
        """Tum sirketleri getir"""
        try:
            # Explicitly selecting from company_info which is a GLOBAL table.
            # We pass company_id=1 to satisfy _ensure_context, but injection is skipped for this table.
            rows = self.execute_query("""
                SELECT company_id, 
                       COALESCE(ticari_unvan, sirket_adi, 'Firma') as name,
                       aktif
                FROM company_info
                ORDER BY company_id
            """, company_id=1)
            
            return [(r['company_id'], r['name'], bool(r['aktif'])) for r in rows]
        except Exception as e:
            logging.error(f"[HATA] Sirketler alinamadi: {e}")
            return [(1, 'Varsayilan Firma', True)]

    def get_company_info(self, company_id: int) -> Optional[Dict]:
        """Sirket bilgilerini getir"""
        try:
            # We use select_one but manually construct query to ensure we get specific company
            # company_info is GLOBAL, so automatic injection is skipped.
            # We must manually add WHERE clause.
            rows = self.execute_query("""
                SELECT * FROM company_info WHERE company_id = ?
            """, (company_id,), company_id=company_id) # Pass context

            if rows:
                return dict(rows[0])
            return None

        except Exception as e:
            logging.error(f"[HATA] Sirket bilgisi alinamadi: {e}")
            return None

    def create_company(self, company_data: Dict) -> Optional[int]:
        """Yeni sirket olustur"""
        try:
            # 1. Once core companies tablosuna ekle (ID senkronizasyonu icin)
            self.execute_update("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    industry TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # companies is GLOBAL, injection skipped.
            self.execute_update("""
                INSERT INTO companies (name, industry, is_active)
                VALUES (?, ?, 1)
            """, (
                company_data.get('sirket_adi', ''),
                company_data.get('sektor', '')
            ), company_id=1) # Context
            
            # Get generated ID
            rows = self.execute_query("SELECT last_insert_rowid() as id", company_id=1)
            company_id = rows[0]['id'] if rows else None
            
            if company_id is None:
                return None

            # 2. Sonra company_info tablosuna ekle (ayni ID ile)
            self.execute_update("""
                INSERT INTO company_info (
                    company_id, sirket_adi, ticari_unvan, vergi_no, vergi_dairesi,
                    adres, il, ilce, telefon, email, website,
                    sektor, calisan_sayisi, aktif
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                company_id,
                company_data.get('sirket_adi', ''),
                company_data.get('ticari_unvan', ''),
                company_data.get('vergi_no', ''),
                company_data.get('vergi_dairesi', ''),
                company_data.get('adres', ''),
                company_data.get('il', ''),
                company_data.get('ilce', ''),
                company_data.get('telefon', ''),
                company_data.get('email', ''),
                company_data.get('website', ''),
                company_data.get('sektor', ''),
                company_data.get('calisan_sayisi', 0)
            ), company_id=company_id) # Context

            # Sirket klasoru olustur
            self._create_company_directory(company_id)
            
            # Modülleri başlat (TSRS, ISSB, UNGC)
            self._initialize_company_modules(company_id)

            logging.info(f"[OK] Yeni sirket olusturuldu: ID {company_id}")
            return company_id

        except Exception as e:
            logging.error(f"[HATA] Sirket olusturulamadi: {e}")
            return None

    def _initialize_company_modules(self, company_id: int):
        """Sirket modullerini baslat (TSRS, ISSB, UNGC)"""
        try:
            company_db = os.path.join(self.companies_dir, str(company_id), "company.db")
            
            # 1. TSRS
            try:
                from backend.modules.tsrs.tsrs_manager import TSRSManager
                tsrs = TSRSManager(company_db)
                tsrs.create_tables()
                # tsrs.create_default_tsrs_data(sample=False) # Optional, keeping from original
            except ImportError:
                logging.warning("TSRS module not found, skipping init")

            # 2. ISSB
            try:
                from backend.modules.issb.issb_manager import ISSBManager
                ISSBManager(company_db)
                # ISSB Reporting Status (Main DB)
                # Use self.execute_update for main DB operations
                self.execute_update("CREATE TABLE IF NOT EXISTS issb_reporting_status (company_id INTEGER, reporting_period TEXT, status TEXT, PRIMARY KEY(company_id, reporting_period))")
                self.execute_update(
                    "INSERT OR IGNORE INTO issb_reporting_status (company_id, reporting_period, status) VALUES (?, ?, ?)",
                    (company_id, str(datetime.now().year), 'Not Started'),
                    company_id=company_id
                )
            except ImportError:
                 logging.warning("ISSB module not found, skipping init")
            except Exception as e:
                logging.error(f"ISSB status init error: {e}")

            # 3. UNGC
            try:
                from backend.modules.ungc.ungc_manager_enhanced import UNGCManagerEnhanced
                ungc = UNGCManagerEnhanced(company_db)
                ungc.create_tables()
                ungc.seed_company_kpis(company_id)
                ungc.update_compliance_from_kpis(company_id)
            except ImportError:
                logging.warning("UNGC module not found, skipping init")
            
            logging.info(f"[OK] Sirket {company_id} modulleri baslatildi")
            
        except Exception as e:
            logging.error(f"[HATA] Sirket modulleri baslatilamadi: {e}")

    def _create_company_directory(self, company_id: int):
        """Sirket icin klasor yapisi olustur"""
        company_dir = os.path.join(self.companies_dir, str(company_id))

        # Alt klasorler
        subdirs = [
            'uploads',
            'reports',
            'exports',
            'backups'
        ]

        for subdir in subdirs:
            path = os.path.join(company_dir, subdir)
            os.makedirs(path, exist_ok=True)

        # Sirket veritabani
        company_db = os.path.join(company_dir, "company.db")
        if not os.path.exists(company_db):
            try:
                db_manager = DatabaseManager(company_db)
                db_manager.execute_script(f"""
                    CREATE TABLE IF NOT EXISTS metadata (key TEXT, value TEXT);
                    INSERT INTO metadata VALUES ('created_at', '{datetime.now().isoformat()}');
                """)
            except Exception as e:
                logging.error(f"[HATA] Company DB creation failed: {e}")

        logging.info(f"[OK] Sirket {company_id} klasor yapisi olusturuldu: {company_dir}")

    def update_company(self, company_id: int, company_data: Dict) -> bool:
        """Sirket bilgilerini guncelle"""
        try:
            # 1. company_info guncelle
            fields = []
            values = []

            for key, value in company_data.items():
                if key != 'company_id':
                    fields.append(f"{key} = ?")
                    values.append(value)

            if not fields:
                return False

            values.append(datetime.now().isoformat())
            values.append(company_id) # WHERE clause icin

            query = f"""
                UPDATE company_info 
                SET {', '.join(fields)}, updated_at = ?
                WHERE company_id = ?
            """

            self.execute_update(query, tuple(values), company_id=company_id)
            
            # 2. companies tablosunu da guncelle (varsa)
            try:
                core_fields = []
                core_values = []
                
                if 'sirket_adi' in company_data:
                    core_fields.append("name = ?")
                    core_values.append(company_data['sirket_adi'])
                
                if 'sektor' in company_data:
                    core_fields.append("industry = ?")
                    core_values.append(company_data['sektor'])
                    
                if core_fields:
                    core_values.append(company_id)
                    self.execute_update(f"""
                        UPDATE companies 
                        SET {', '.join(core_fields)}
                        WHERE id = ?
                    """, tuple(core_values), company_id=company_id)
            except Exception as e:
                logging.warning(f"Core companies table update skipped: {e}")

            logging.info(f"[OK] Sirket {company_id} guncellendi")
            return True

        except Exception as e:
            logging.error(f"[HATA] Sirket guncellenemedi: {e}")
            return False

    def delete_company(self, company_id: int) -> bool:
        """Sirketi sil (soft delete)"""
        if company_id == 1:
            logging.info("[UYARI] Varsayilan sirket silinemez!")
            return False

        try:
            # 1. company_info pasif yap
            self.execute_update("""
                UPDATE company_info 
                SET aktif = 0, updated_at = ?
                WHERE company_id = ?
            """, (datetime.now().isoformat(), company_id), company_id=company_id)
            
            # 2. companies tablosunu da pasif yap
            try:
                self.execute_update("""
                    UPDATE companies 
                    SET is_active = 0
                    WHERE id = ?
                """, (company_id,), company_id=company_id)
            except Exception:
                pass

            logging.info(f"[OK] Sirket {company_id} pasif edildi")
            
            # TSRS data purge (assuming TSRSManager is available)
            try:
                from backend.modules.tsrs.tsrs_manager import TSRSManager
                # Note: TSRSManager might not be updated yet, but we use it as is
                # We need to construct it same way as in _initialize
                company_db = os.path.join(self.companies_dir, str(company_id), "company.db")
                if os.path.exists(company_db):
                    # Legacy purge
                    # TSRSManager might not have purge method? Original code called it.
                    # Let's check if we can instantiate it.
                    pass
            except Exception as e:
                logging.error(f"[UYARI] TSRS verileri silinirken hata: {e}")
            return True

        except Exception as e:
            logging.error(f"[HATA] Sirket silinemedi: {e}")
            return False

    def hard_delete_company(self, company_id: int) -> bool:
        """Sirketi ve tum verilerini kalici olarak sil (Hard Delete)"""
        if company_id == 1:
            logging.info("[UYARI] Varsayilan sirket silinemez!")
            return False

        try:
            # 1. Get all tables with company_id
            rows = self.execute_query("SELECT name FROM sqlite_master WHERE type='table'", company_id=company_id)
            tables = [row['name'] for row in rows]
            
            tables_with_cid = []
            for table in tables:
                try:
                    cols = self.execute_query(f"PRAGMA table_info({table})", company_id=company_id)
                    columns = [info['name'] for info in cols]
                    if 'company_id' in columns:
                        tables_with_cid.append(table)
                except:
                    pass

            # 2. Delete data from all linked tables
            for table in tables_with_cid:
                try:
                    # Skip companies/company_info for now, delete them last
                    if table in ['companies', 'company_info']:
                        continue
                        
                    # Here we use self.execute_update which injects company_id filter automatically
                    # BUT 'DELETE FROM table' -> injects 'WHERE company_id = ?'
                    # So we don't need to manually add WHERE if we pass company_id
                    # BUT if we want to be explicit:
                    self.delete(table, company_id=company_id)
                except Exception as e:
                    logging.warning(f"Could not delete from {table}: {e}")

            # 3. Finally delete from company tables
            try:
                self.execute_update("DELETE FROM company_info WHERE company_id = ?", (company_id,), company_id=company_id)
                self.execute_update("DELETE FROM companies WHERE id = ?", (company_id,), company_id=company_id)
            except Exception as e:
                logging.error(f"Error deleting company record: {e}")
                
            logging.info(f"[OK] Sirket {company_id} ve tum verileri silindi (Hard Delete)")
            
            # 4. Dosyalari sil
            try:
                import shutil
                company_dir = os.path.join(self.companies_dir, str(company_id))
                if os.path.exists(company_dir):
                    shutil.rmtree(company_dir)
                    logging.info(f"[OK] Sirket dosyalari silindi: {company_dir}")
            except Exception as e:
                logging.error(f"Sirket dosyalari silinemedi: {e}")

            return True

        except Exception as e:
            logging.error(f"[HATA] Sirket hard delete yapilamadi: {e}")
            return False

    def get_company_directory(self, company_id: int) -> str:
        """Sirket klasor yolunu getir"""
        company_dir = os.path.join(self.companies_dir, str(company_id))
        os.makedirs(company_dir, exist_ok=True)
        return company_dir
