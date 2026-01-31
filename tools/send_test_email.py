#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basit test e-mail gönderim scripti
SMTP ayarları backend/config/smtp_config.json üzerinden okunur
"""

import os
import sys
import logging

# Ensure backend can be imported
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
sys.path.append(os.path.join(ROOT_DIR, 'backend'))

try:
    from backend.services.email_service import EmailService
except ImportError:
    logging.error("Could not import EmailService")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    to_email = "kivanc.kasoglu@izgienerji.com"
    subject = "SUSTAINAGE SDG - Test Maili"
    text_content = (
        "Merhaba,<br><br>"
        "Bu e-posta SUSTAINAGE SDG sistemi tarafından gönderilen bir test iletisidir.<br>"
        "SMTP: smtp.digage.tr:587 (TLS/SSL yok), kimlik doğrulama etkin.<br><br>"
        "Teşekkürler."
    )

    service = EmailService()
    success = service.send_email(
        to_email=to_email,
        subject=subject,
        body=text_content
    )

    if success:
        logging.info(" Test maili başarıyla gönderildi.")
    else:
        logging.info(" Gönderim başarısız.")


if __name__ == "__main__":
    main()
