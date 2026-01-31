import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Font Utilities for Report Generation
- Registers Turkish-compatible fonts (NotoSans) for ReportLab
"""

import os

try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.pdfmetrics import registerFontFamily
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


def register_turkish_fonts_reportlab():
    """Register NotoSans Turkish-compatible fonts for ReportLab.

    Safe to call multiple times; will no-op if ReportLab is not available.
    """
    if not REPORTLAB_AVAILABLE:
        return

    try:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.abspath(os.path.join(module_dir, '..', '..'))
        fonts_dir = os.path.join(base_dir, 'raporlama', 'fonts')

        noto_regular = os.path.join(fonts_dir, 'NotoSans-Regular.ttf')
        noto_bold = os.path.join(fonts_dir, 'NotoSans-Bold.ttf')
        noto_italic = os.path.join(fonts_dir, 'NotoSans-Italic.ttf')

        if os.path.exists(noto_regular):
            try:
                pdfmetrics.registerFont(TTFont('NotoSans', noto_regular))
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        if os.path.exists(noto_bold):
            try:
                pdfmetrics.registerFont(TTFont('NotoSans-Bold', noto_bold))
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        if os.path.exists(noto_italic):
            try:
                pdfmetrics.registerFont(TTFont('NotoSans-Italic', noto_italic))
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")

        # Register family mapping for bold/italic resolution
        try:
            registerFontFamily(
                'NotoSans',
                normal='NotoSans',
                bold='NotoSans-Bold' if os.path.exists(noto_bold) else 'NotoSans',
                italic='NotoSans-Italic' if os.path.exists(noto_italic) else 'NotoSans',
                boldItalic='NotoSans-Bold' if os.path.exists(noto_bold) else 'NotoSans',
            )
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")
    except Exception as e:
        # Swallow to avoid breaking report generation, default fonts will be used.
        logging.error(f"Silent error caught: {str(e)}")
