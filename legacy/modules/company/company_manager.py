#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sirket Yonetim Sistemi
Cok sirketli kullanim, yeni sirket ekleme
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from modules.tsrs.tsrs_manager import TSRSManager
from config.database import DB_PATH


class CompanyManager:
    """Sirket yonetimi sinifi"""

    def __init__(self, db_path: str = DB_PATH):
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)

        self.db_path = db_path
        self.base_dir = os.path.dirname(os.path.dirname(db_path))

        # Sirket veri klasoru
        self.companies_dir = os.path.join(self.base_dir, "data", "companies")
        os.makedirs(self.companies_dir, exist_ok=True)

        self._ensure_company_tables()

    def _ensure_company_tables(self):
        """Sirket tablolarini olustur"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            # company_info tablosu
            cur.execute("""
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
                    aktif BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Varsayilan sirket yoksa ekle
            cur.execute("SELECT COUNT(*) FROM company_info")
            if cur.fetchone()[0] == 0:
                cur.execute("""
                    INSERT INTO company_info (company_id, sirket_adi, ticari_unvan, aktif)
                    VALUES (1, 'Varsayilan Firma', 'Varsayilan Ticari Unvan', 1)
                """)

            conn.commit()
            logging.info("[OK] Sirket tablolari hazir")

        except Exception as e:
            logging.error(f"[HATA] Sirket tablolari olusturulamadi: {e}")
        finally:
            conn.close()

    def get_all_companies(self) -> List[Tuple[int, str, bool]]:
        """Tum sirketleri getir"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT company_id, 
                       COALESCE(ticari_unvan, sirket_adi, 'Firma'),
                       aktif
                FROM company_info
                ORDER BY company_id
            """)
            return cur.fetchall()
        except Exception as e:
            logging.error(f"[HATA] Sirketler alinamadi: {e}")
            return [(1, 'Varsayilan Firma', True)]
        finally:
            conn.close()

    def get_company_info(self, company_id: int) -> Optional[Dict]:
        """Sirket bilgilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT * FROM company_info WHERE company_id = ?
            """, (company_id,))

            row = cur.fetchone()
            if row:
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, row))
            return None

        except Exception as e:
            logging.error(f"[HATA] Sirket bilgisi alinamadi: {e}")
            return None
        finally:
            conn.close()

    def create_company(self, company_data: Dict) -> Optional[int]:
        """Yeni sirket olustur"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            # 1. Once core companies tablosuna ekle (ID senkronizasyonu icin)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    industry TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cur.execute("""
                INSERT INTO companies (name, industry, is_active)
                VALUES (?, ?, 1)
            """, (
                company_data.get('sirket_adi', ''),
                company_data.get('sektor', '')
            ))
            
            company_id = cur.lastrowid
            if company_id is None:
                conn.rollback()
                return None

            # 2. Sonra company_info tablosuna ekle (ayni ID ile)
            cur.execute("""
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
            ))

            conn.commit()

            # Sirket klasoru olustur
            self._create_company_directory(company_id)
            
            # Modülleri başlat (TSRS, ISSB, UNGC)
            self._initialize_company_modules(company_id)

            logging.info(f"[OK] Yeni sirket olusturuldu: ID {company_id}")
            return company_id

        except Exception as e:
            logging.error(f"[HATA] Sirket olusturulamadi: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def _initialize_company_modules(self, company_id: int):
        """Sirket modullerini baslat (TSRS, ISSB, UNGC)"""
        try:
            company_db = os.path.join(self.companies_dir, str(company_id), "company.db")
            
            # 1. TSRS
            try:
                from modules.tsrs.tsrs_manager import TSRSManager
                tsrs = TSRSManager(company_db)
                tsrs.create_tables()
                tsrs.create_default_tsrs_data(sample=False)
            except ImportError:
                logging.warning("TSRS module not found, skipping init")

            # 2. ISSB
            try:
                from modules.issb.issb_manager import ISSBManager
                ISSBManager(company_db)
                # ISSB Reporting Status (Main DB)
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                # Check if table exists
                cur.execute("CREATE TABLE IF NOT EXISTS issb_reporting_status (company_id INTEGER, reporting_period TEXT, status TEXT, PRIMARY KEY(company_id, reporting_period))")
                cur.execute(
                    "INSERT OR IGNORE INTO issb_reporting_status (company_id, reporting_period, status) VALUES (?, ?, ?)",
                    (company_id, str(datetime.now().year), 'Not Started')
                )
                conn.commit()
                conn.close()
            except ImportError:
                 logging.warning("ISSB module not found, skipping init")
            except Exception as e:
                logging.error(f"ISSB status init error: {e}")

            # 3. UNGC
            try:
                from modules.ungc.ungc_manager_enhanced import UNGCManagerEnhanced
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
            conn = sqlite3.connect(company_db)
            conn.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT, value TEXT)")
            conn.execute("INSERT INTO metadata VALUES ('created_at', ?)", (datetime.now().isoformat(),))
            conn.commit()
            conn.close()

        logging.info(f"[OK] Sirket {company_id} klasor yapisi olusturuldu: {company_dir}")

    def update_company(self, company_id: int, company_data: Dict) -> bool:
        """Sirket bilgilerini guncelle"""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

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

            values.append(company_id)
            values.append(datetime.now().isoformat())
            values.append(company_id) # WHERE clause icin

            query = f"""
                UPDATE company_info 
                SET {', '.join(fields)}, updated_at = ?
                WHERE company_id = ?
            """

            cur.execute(query, values)
            
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
                    cur.execute(f"""
                        UPDATE companies 
                        SET {', '.join(core_fields)}
                        WHERE id = ?
                    """, core_values)
            except Exception as e:
                logging.warning(f"Core companies table update skipped: {e}")

            conn.commit()

            logging.info(f"[OK] Sirket {company_id} guncellendi")
            return True

        except Exception as e:
            logging.error(f"[HATA] Sirket guncellenemedi: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_company(self, company_id: int) -> bool:
        """Sirketi sil (soft delete)"""
        if company_id == 1:
            logging.info("[UYARI] Varsayilan sirket silinemez!")
            return False

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            # 1. company_info pasif yap
            cur.execute("""
                UPDATE company_info 
                SET aktif = 0, updated_at = ?
                WHERE company_id = ?
            """, (datetime.now().isoformat(), company_id))
            
            # 2. companies tablosunu da pasif yap
            try:
                cur.execute("""
                    UPDATE companies 
                    SET is_active = 0
                    WHERE id = ?
                """, (company_id,))
            except Exception:
                pass

            conn.commit()
            logging.info(f"[OK] Sirket {company_id} pasif edildi")
            try:
                TSRSManager().purge_company_tsrs_data(company_id, delete_exports=True)
            except Exception as e:
                logging.error(f"[UYARI] TSRS verileri silinirken hata: {e}")
            return True

        except Exception as e:
            logging.error(f"[HATA] Sirket silinemedi: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def hard_delete_company(self, company_id: int) -> bool:
        """Sirketi ve tum verilerini kalici olarak sil (Hard Delete)"""
        if company_id == 1:
            logging.info("[UYARI] Varsayilan sirket silinemez!")
            return False

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        try:
            # 1. Get all tables with company_id
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]
            
            tables_with_cid = []
            for table in tables:
                try:
                    cur.execute(f"PRAGMA table_info({table})")
                    columns = [info[1] for info in cur.fetchall()]
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
                        
                    cur.execute(f"DELETE FROM {table} WHERE company_id = ?", (company_id,))
                except Exception as e:
                    logging.warning(f"Could not delete from {table}: {e}")

            # 3. Finally delete from company tables
            try:
                cur.execute("DELETE FROM company_info WHERE company_id = ?", (company_id,))
                cur.execute("DELETE FROM companies WHERE id = ?", (company_id,))
            except Exception as e:
                logging.error(f"Error deleting company record: {e}")
                
            conn.commit()
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
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_company_directory(self, company_id: int) -> str:
        """Sirket klasor yolunu getir"""
        company_dir = os.path.join(self.companies_dir, str(company_id))
        os.makedirs(company_dir, exist_ok=True)
        return company_dir

