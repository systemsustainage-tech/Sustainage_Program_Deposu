#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program tamamlama hatırlatma e-postası (1 hafta kaldı)
SMTP ayarları backend/config/smtp_config.json üzerinden okunur.
"""

import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.email_service import EmailService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    to_email = "kivanc.kasoglu@izgienerji.com"
    subject = "SUSTAINAGE SDG - Program Tamamlanmasına 1 Hafta Kaldı"
    
    # Simple HTML content
    body_content = (
        "<p>Merhaba,</p>"
        "<p>Sürdürülebilirlik programımızın tamamlanmasına 1 hafta kaldı.</p>"
        "<h3>Özet:</h3>"
        "<ul>"
        "<li>Kalan süre: 7 gün</li>"
        "<li>Bekleyen görevler: Kontrol listesi üzerinde gözden geçiriniz</li>"
        "<li>Aksiyon: Gerekli veri girişlerini tamamlayın ve onay akışını başlatın</li>"
        "</ul>"
        "<p>Herhangi bir sorunuz varsa yanıtlayabilirim.</p>"
        "<p>Teşekkürler,<br>SUSTAINAGE SDG</p>"
    )

    service = EmailService()
    success = service.send_email(
        to_email=to_email,
        subject=subject,
        body=body_content
    )

    if success:
        logging.info(" Hatırlatma maili başarıyla gönderildi.")
    else:
        logging.info(" Gönderim başarısız.")


if __name__ == "__main__":
    main()
