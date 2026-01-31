#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Marka Kimliği Entegrasyonu
Logo, renkler, fontlar ve profesyonel tasarım yönetimi
"""

import logging
import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from PIL import Image


class BrandIdentityManager:
    """Marka kimliği yönetim sistemi"""

    # Varsayılan renk paleti
    DEFAULT_COLORS = {
        'primary': '#2c3e50',      # Koyu lacivert
        'secondary': '#3498db',     # Mavi
        'success': '#27ae60',       # Yeşil
        'warning': '#f39c12',       # Turuncu
        'danger': '#e74c3c',        # Kırmızı
        'info': '#16a085',          # Turkuaz
        'light': '#ecf0f1',         # Açık gri
        'dark': '#34495e',          # Koyu gri
        'white': '#ffffff',
        'text_primary': '#2c3e50',
        'text_secondary': '#7f8c8d'
    }

    def __init__(self, db_path: str, company_id: int = 1) -> None:
        self.db_path = db_path
        self.company_id = company_id
        self._init_tables()

    def _init_tables(self) -> None:
        """Marka kimliği tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brand_identity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER UNIQUE NOT NULL,
                    company_name TEXT,
                    logo_path TEXT,
                    logo_width INTEGER DEFAULT 200,
                    logo_height INTEGER DEFAULT 100,
                    color_primary TEXT DEFAULT '#2c3e50',
                    color_secondary TEXT DEFAULT '#3498db',
                    color_accent TEXT DEFAULT '#27ae60',
                    font_heading TEXT DEFAULT 'Segoe UI',
                    font_body TEXT DEFAULT 'Segoe UI',
                    report_header_text TEXT,
                    report_footer_text TEXT,
                    watermark_text TEXT,
                    custom_styles TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            """)

            conn.commit()
            logging.info("[OK] Brand identity tablosu hazır")

        except Exception as e:
            logging.error(f"[HATA] Brand identity tablo: {e}")
            conn.rollback()
        finally:
            conn.close()

    def save_brand_identity(self, company_id: int, logo_path: Optional[str] = None,
                           colors: Optional[Dict[str, Any]] = None,
                           fonts: Optional[Dict[str, Any]] = None,
                           texts: Optional[Dict[str, Any]] = None) -> bool:
        """
        Marka kimliğini kaydet
        
        Args:
            company_id: Şirket ID
            logo_path: Logo dosya yolu
            colors: {'primary': '#hex', 'secondary': '#hex', ...}
            fonts: {'heading': 'Segoe UI', 'body': 'Georgia'}
            texts: {'header': 'text', 'footer': 'text', 'watermark': 'text'}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Mevcut kayıt var mı kontrol et
            cursor.execute("SELECT id FROM brand_identity WHERE company_id = ?", (company_id,))
            exists = cursor.fetchone()

            if exists:
                # Güncelle
                update_fields = ['updated_at = ?']
                values: list[object] = [datetime.now().isoformat()]

                if logo_path:
                    update_fields.append('logo_path = ?')
                    values.append(logo_path)

                if colors:
                    if 'primary' in colors:
                        update_fields.append('color_primary = ?')
                        values.append(colors['primary'])
                    if 'secondary' in colors:
                        update_fields.append('color_secondary = ?')
                        values.append(colors['secondary'])
                    if 'accent' in colors:
                        update_fields.append('color_accent = ?')
                        values.append(colors['accent'])

                if fonts:
                    if 'heading' in fonts:
                        update_fields.append('font_heading = ?')
                        values.append(fonts['heading'])
                    if 'body' in fonts:
                        update_fields.append('font_body = ?')
                        values.append(fonts['body'])

                if texts:
                    if 'header' in texts:
                        update_fields.append('report_header_text = ?')
                        values.append(texts['header'])
                    if 'footer' in texts:
                        update_fields.append('report_footer_text = ?')
                        values.append(texts['footer'])
                    if 'watermark' in texts:
                        update_fields.append('watermark_text = ?')
                        values.append(texts['watermark'])

                values.append(company_id)

                query = f"UPDATE brand_identity SET {', '.join(update_fields)} WHERE company_id = ?"
                cursor.execute(query, values)
            else:
                # Yeni kayıt
                cursor.execute("""
                    INSERT INTO brand_identity
                    (company_id, logo_path, color_primary, color_secondary, color_accent,
                     font_heading, font_body, report_header_text, report_footer_text, watermark_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (company_id,
                      logo_path,
                      colors.get('primary', self.DEFAULT_COLORS['primary']) if colors else self.DEFAULT_COLORS['primary'],
                      colors.get('secondary', self.DEFAULT_COLORS['secondary']) if colors else self.DEFAULT_COLORS['secondary'],
                      colors.get('accent', self.DEFAULT_COLORS['success']) if colors else self.DEFAULT_COLORS['success'],
                      fonts.get('heading', 'Segoe UI') if fonts else 'Segoe UI',
                      fonts.get('body', 'Segoe UI') if fonts else 'Segoe UI',
                      texts.get('header', '') if texts else '',
                      texts.get('footer', '') if texts else '',
                      texts.get('watermark', '') if texts else ''))

            conn.commit()
            return True

        except Exception as e:
            logging.error(f"Marka kimliği kaydetme hatası: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_brand_identity(self, company_id: int) -> Dict:
        """Marka kimliğini getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        result = {
            'logo_path': None,
            'colors': self.DEFAULT_COLORS,
            'fonts': {'heading': 'Segoe UI', 'body': 'Segoe UI'},
            'texts': {}
        }

        try:
            cursor.execute("""
                SELECT logo_path, color_primary, color_secondary, color_accent,
                       font_heading, font_body, report_header_text, report_footer_text,
                       watermark_text
                FROM brand_identity
                WHERE company_id = ?
            """, (company_id,))

            row = cursor.fetchone()

            if row:
                result = {
                    'logo_path': row[0],
                    'colors': {
                        'primary': row[1],
                        'secondary': row[2],
                        'accent': row[3]
                    },
                    'fonts': {
                        'heading': row[4],
                        'body': row[5]
                    },
                    'texts': {
                        'header': row[6],
                        'footer': row[7],
                        'watermark': row[8]
                    }
                }
            
            # Logo fallback mantığı: Eğer brand_identity'de yoksa veya dosya yoksa
            if not result['logo_path'] or not os.path.exists(result['logo_path']):
                # 1. company_profiles tablosuna bak
                try:
                    # Tablo var mı kontrol et (emin olmak için)
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_profiles'")
                    if cursor.fetchone():
                        cursor.execute("SELECT logo_path FROM company_profiles WHERE company_id = ?", (company_id,))
                        cp_row = cursor.fetchone()
                        if cp_row and cp_row[0] and os.path.exists(cp_row[0]):
                            result['logo_path'] = cp_row[0]
                except Exception as e:
                    logging.warning(f"Company profiles logo check error: {e}")

                # 2. Hala yoksa dosya sistemine bak
                if not result['logo_path'] or not os.path.exists(result['logo_path']):
                    data_dir = os.path.dirname(self.db_path)
                    possible_path = os.path.join(data_dir, "company_logos", f"company_{company_id}_logo.png")
                    if os.path.exists(possible_path):
                        result['logo_path'] = possible_path
                    else:
                        possible_path = possible_path.replace(".png", ".jpg")
                        if os.path.exists(possible_path):
                            result['logo_path'] = possible_path

        except Exception as e:
            logging.error(f"Marka kimliği getirme hatası: {e}")
        finally:
            conn.close()
            
        return result

    def validate_logo(self, logo_path: str) -> Tuple[bool, str]:
        """Logo dosyasını doğrula"""
        try:
            if not os.path.exists(logo_path):
                return False, "Dosya bulunamadı"

            # Dosya boyutu kontrolü (max 5MB)
            file_size = os.path.getsize(logo_path)
            if file_size > 5 * 1024 * 1024:
                return False, "Dosya çok büyük (max 5MB)"

            # Görüntü formatı kontrolü
            try:
                img = Image.open(logo_path)
                if img.format not in ['PNG', 'JPEG', 'JPG', 'GIF']:
                    return False, "Geçersiz format (PNG, JPEG veya GIF olmalı)"

                # Boyut önerisi
                width, height = img.size
                if width > 1000 or height > 500:
                    return True, f"Uyarı: Logo çok büyük ({width}x{height}). 800x400 önerilir."

                return True, "Logo geçerli"

            except Exception as e:
                return False, f"Görüntü okunamadı: {e}"

        except Exception as e:
            return False, f"Doğrulama hatası: {e}"

    def get_color_palette(self, company_id: int) -> Dict:
        """Renk paletini getir"""
        brand = self.get_brand_identity(company_id)
        return brand['colors']

    def apply_brand_to_report(self, report_config: Dict, company_id: int) -> Dict:
        """Rapora marka kimliğini uygula"""
        brand = self.get_brand_identity(company_id)

        # Rapor config'e marka bilgilerini ekle
        report_config['brand'] = {
            'logo': brand['logo_path'],
            'colors': brand['colors'],
            'fonts': brand['fonts'],
            'header': brand['texts']['header'],
            'footer': brand['texts']['footer'],
            'watermark': brand['texts']['watermark']
        }

        return report_config

