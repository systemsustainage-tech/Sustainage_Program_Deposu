#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firma Profil Yönetimi - Logo ve Bilgiler
Admin tarafından güncellenebilir firma logosu ve bilgileri
"""

import logging
import os
import sqlite3
from typing import Dict, Optional

from PIL import Image
from config.database import DB_PATH


class CompanyProfileManager:
    """Firma profil ve logo yönetimi"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        if not os.path.isabs(db_path):
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            db_path = os.path.join(base_dir, db_path)
        self.db_path = db_path
        self.logo_dir = os.path.join(os.path.dirname(db_path), "company_logos")

        # Logo dizinini oluştur
        os.makedirs(self.logo_dir, exist_ok=True)

        self._init_profile_tables()

    def _init_profile_tables(self) -> None:
        """Profil tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Firma profil bilgileri
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER UNIQUE NOT NULL,
                    company_name TEXT NOT NULL,
                    sector TEXT,
                    logo_path TEXT,
                    logo_width INTEGER DEFAULT 200,
                    logo_height INTEGER DEFAULT 100,
                    primary_color TEXT DEFAULT '#1976D2',
                    secondary_color TEXT DEFAULT '#388E3C',
                    contact_email TEXT,
                    contact_phone TEXT,
                    address TEXT,
                    website TEXT,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Firma profil tablolari olusturuldu")

        except Exception as e:
            logging.error(f"[ERROR] Profil tablolari olusturulurken hata: {e}")
        finally:
            conn.close()

    def upload_logo(self, company_id: int, logo_file_path: str,
                   max_width: int = 400, max_height: int = 200) -> bool:
        """
        Firma logosu yükle
        
        Args:
            company_id: Şirket ID
            logo_file_path: Logo dosya yolu
            max_width: Maksimum genişlik (px)
            max_height: Maksimum yükseklik (px)
        """
        try:
            if not os.path.exists(logo_file_path):
                logging.info(f"Logo dosyasi bulunamadi: {logo_file_path}")
                return False

            # Resmi aç ve boyutlandır
            img = Image.open(logo_file_path)

            # Aspect ratio koruyarak boyutlandır
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            # Yeni dosya adı
            file_ext = os.path.splitext(logo_file_path)[1]
            new_filename = f"company_{company_id}_logo{file_ext}"
            new_path = os.path.join(self.logo_dir, new_filename)

            # Kaydet
            img.save(new_path, quality=95)
            try:
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                resimler_dir = os.path.join(base_dir, 'resimler')
                os.makedirs(resimler_dir, exist_ok=True)
                company_logo_png = os.path.join(resimler_dir, 'company_logo.png')
                img.save(company_logo_png, format='PNG', quality=95)
            except Exception as e:
                logging.error(f"[WARNING] Logo yedeklenirken hata: {e}")

            # Veritabanını güncelle
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE company_profiles
                SET logo_path = ?, logo_width = ?, logo_height = ?, updated_at = CURRENT_TIMESTAMP
                WHERE company_id = ?
            """, (new_path, img.width, img.height, company_id))

            if cursor.rowcount == 0:
                # Yoksa yeni kayıt oluştur
                cursor.execute("""
                    INSERT INTO company_profiles (company_id, company_name, logo_path, logo_width, logo_height)
                    VALUES (?, ?, ?, ?, ?)
                """, (company_id, f"Company {company_id}", new_path, img.width, img.height))

            conn.commit()
            conn.close()

            logging.info(f"[OK] Logo yuklendi: {new_path}")
            return True

        except Exception as e:
            logging.error(f"Logo yukleme hatasi: {e}")
            return False

    def get_logo_path(self, company_id: int) -> Optional[str]:
        """Firma logosunun yolunu getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT logo_path FROM company_profiles
                WHERE company_id = ?
            """, (company_id,))

            result = cursor.fetchone()
            if result and result[0] and os.path.exists(result[0]):
                return result[0]

            # Varsayılan logo
            default_logo = "resimler/default_company_logo.png"
            if os.path.exists(default_logo):
                return default_logo

            return None

        except Exception as e:
            logging.error(f"Logo yolu getirme hatasi: {e}")
            return None
        finally:
            conn.close()

    def get_company_profile(self, company_id: int) -> Dict:
        """Firma profil bilgilerini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT * FROM company_profiles
                WHERE company_id = ?
            """, (company_id,))

            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))

            # Varsayılan profil
            return {
                "company_id": company_id,
                "company_name": f"Şirket {company_id}",
                "logo_path": None,
                "primary_color": "#1976D2",
                "secondary_color": "#388E3C"
            }

        except Exception as e:
            logging.error(f"Profil getirme hatasi: {e}")
            return {}
        finally:
            conn.close()

    def update_profile(self, company_id: int, profile_data: Dict) -> bool:
        """Firma profil bilgilerini güncelle"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE company_profiles
                SET company_name = ?,
                    sector = ?,
                    primary_color = ?,
                    secondary_color = ?,
                    contact_email = ?,
                    contact_phone = ?,
                    address = ?,
                    website = ?,
                    description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE company_id = ?
            """, (
                profile_data.get('company_name', ''),
                profile_data.get('sector', ''),
                profile_data.get('primary_color', '#1976D2'),
                profile_data.get('secondary_color', '#388E3C'),
                profile_data.get('contact_email', ''),
                profile_data.get('contact_phone', ''),
                profile_data.get('address', ''),
                profile_data.get('website', ''),
                profile_data.get('description', ''),
                company_id
            ))

            if cursor.rowcount == 0:
                # Yeni kayıt oluştur
                cursor.execute("""
                    INSERT INTO company_profiles
                    (company_id, company_name, sector, primary_color, secondary_color,
                     contact_email, contact_phone, address, website, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id,
                    profile_data.get('company_name', ''),
                    profile_data.get('sector', ''),
                    profile_data.get('primary_color', '#1976D2'),
                    profile_data.get('secondary_color', '#388E3C'),
                    profile_data.get('contact_email', ''),
                    profile_data.get('contact_phone', ''),
                    profile_data.get('address', ''),
                    profile_data.get('website', ''),
                    profile_data.get('description', '')
                ))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Profil guncelleme hatasi: {e}")
            return False
        finally:
            conn.close()

    def delete_logo(self, company_id: int) -> bool:
        """Firma logosunu sil"""
        try:
            logo_path = self.get_logo_path(company_id)

            if logo_path and os.path.exists(logo_path):
                os.remove(logo_path)

            # Veritabanından kaldır
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE company_profiles
                SET logo_path = NULL, updated_at = CURRENT_TIMESTAMP
                WHERE company_id = ?
            """, (company_id,))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            logging.error(f"Logo silme hatasi: {e}")
            return False
