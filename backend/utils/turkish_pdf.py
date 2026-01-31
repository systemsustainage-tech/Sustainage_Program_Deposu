#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turkce PDF Yardimcisi
Tum PDF raporlarinda Turkce karakter garantisi
"""

import logging
import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class TurkishPDF:
    """Turkce PDF islemleri icin yardimci sinif"""

    def __init__(self):
        pass

    _fonts_loaded = False
    _font_dir = None

    @classmethod
    def load_fonts(cls):
        """Turkce fontlari yukle (bir kez)"""
        if cls._fonts_loaded:
            return True

        try:
            # Font klasoru
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            cls._font_dir = os.path.join(base_dir, "raporlama", "fonts")

            # Fontlarin varligi kontrol
            if not os.path.exists(cls._font_dir):
                logging.info(f"[UYARI] Font klasoru bulunamadi: {cls._font_dir}")
                return False

            # Fontlari yukle
            regular = os.path.join(cls._font_dir, "NotoSans-Regular.ttf")
            bold = os.path.join(cls._font_dir, "NotoSans-Bold.ttf")
            italic = os.path.join(cls._font_dir, "NotoSans-Italic.ttf")

            if os.path.exists(regular):
                pdfmetrics.registerFont(TTFont('NotoSans', regular))
                logging.info("[OK] NotoSans-Regular yuklendi")

            if os.path.exists(bold):
                pdfmetrics.registerFont(TTFont('NotoSans-Bold', bold))
                logging.info("[OK] NotoSans-Bold yuklendi")

            if os.path.exists(italic):
                pdfmetrics.registerFont(TTFont('NotoSans-Italic', italic))
                logging.info("[OK] NotoSans-Italic yuklendi")

            cls._fonts_loaded = True
            return True

        except Exception as e:
            logging.error(f"[HATA] Turkce fontlar yuklenemedi: {e}")
            return False

    @classmethod
    def get_font(cls, style='regular'):
        """Font adi getir"""
        cls.load_fonts()

        fonts = {
            'regular': 'NotoSans',
            'bold': 'NotoSans-Bold',
            'italic': 'NotoSans-Italic'
        }

        return fonts.get(style, 'NotoSans')

    @classmethod
    def is_available(cls):
        """Turkce fontlar yuklendi mi?"""
        return cls._fonts_loaded or cls.load_fonts()

    @classmethod
    def clean_text(cls, text):
        """Metni temizle (ozel karakterleri koru)"""
        if not text:
            return ""

        # Turkce karakterleri koru
        return str(text).strip()

    @classmethod
    def apply_to_canvas(cls, canvas, font_size=12, font_style='regular'):
        """Canvas'a Turkce fontu uygula"""
        if cls.load_fonts():
            font_name = cls.get_font(font_style)
            canvas.setFont(font_name, font_size)
            return True
        return False

# Otomatik yukle
TurkishPDF.load_fonts()

