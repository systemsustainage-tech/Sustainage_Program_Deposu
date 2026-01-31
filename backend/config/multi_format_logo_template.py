#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUSTAINAGE SDG - Multi Format Logo Email Şablonu
- Farklı formatlarla logo test
"""

import logging
import base64
import os


def get_logo_base64(format_type='png'):
    """Logo dosyasını base64 olarak döndür"""
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'resimler', f'mail.{format_type}')

    if os.path.exists(logo_path):
        try:
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
                logo_base64 = base64.b64encode(logo_data).decode('utf-8')
                return f"data:image/{format_type};base64,{logo_base64}"
        except Exception as e:
            logging.error(f"Logo yükleme hatası ({format_type}): {e}")
            return None
    else:
        logging.info(f"Logo dosyası bulunamadı: {logo_path}")
        return None

# Farklı formatlarla logo base64 verisi
LOGO_PNG = get_logo_base64('png')
LOGO_JPG = get_logo_base64('jpg')
LOGO_WEBP = get_logo_base64('webp')

# En iyi formatı seç
BEST_LOGO = LOGO_WEBP or LOGO_JPG or LOGO_PNG

# Multi format email şablonu
MULTI_FORMAT_LOGO_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SUSTAINAGE SDG</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .logo {{
            width: 60px;
            height: 60px;
            margin: 0 auto 20px;
            display: block;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0;
            font-size: 16px;
            opacity: 0.9;
        }}
        .content {{
            padding: 40px 30px;
        }}
        .content h2 {{
            color: #2E8B57;
            font-size: 24px;
            margin: 0 0 20px;
            font-weight: 400;
        }}
        .content p {{
            font-size: 16px;
            margin: 0 0 20px;
            line-height: 1.6;
        }}
        .footer {{
            background-color: #f8f9fa;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }}
        .footer p {{
            margin: 0 0 10px;
            font-size: 14px;
            color: #666;
        }}
        .footer .company {{
            font-weight: bold;
            color: #2E8B57;
            font-size: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="{BEST_LOGO if BEST_LOGO else ''}" alt="SUSTAINAGE Logo" class="logo">
            <h1>SUSTAINAGE SDG</h1>
            <p>Sürdürülebilir Kalkınma Hedefleri</p>
        </div>
        
        <div class="content">
            <h2>{{subject}}</h2>
            
            <p>{{message}}</p>
            
            <p>İyi çalışmalar,<br>
            <strong>SUSTAINAGE SDG Ekibi</strong></p>
        </div>
        
        <div class="footer">
            <p class="company">SUSTAINAGE SDG</p>
            <p>Sürdürülebilir Kalkınma Hedefleri Yönetim Sistemi</p>
            <p>Bu email otomatik olarak gönderilmiştir.</p>
        </div>
    </div>
</body>
</html>
"""
