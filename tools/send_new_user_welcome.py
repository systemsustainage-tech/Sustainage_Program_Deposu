#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yeni kullanıcı hoş geldiniz e-postası gönderim scripti
SMTP ayarları backend/config/smtp_config.json üzerinden okunur.
"""

import logging
from services.email_service import EmailService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main() -> None:
    to_email = "sdg@digage.tr"
    user_name = "Test Kullanıcı"
    login_url = "https://sustainage.cloud/login"

    service = EmailService()
    # Debug: SMTP konfigürasyonunu göster
    cfg = service._load_config()
    logging.info(f"SMTP Host: {cfg.get('host')} Port: {cfg.get('port')} TLS: {cfg.get('use_tls')} From: {cfg.get('from_email')}")
    ok = service.send_new_user_welcome(
        to_email=to_email,
        user_name=user_name,
        login_url=login_url,
        program_name="Sustainage SDG Platform",
        short_description=(
            "Kurumsal sürdürülebilirlik hedefleriniz için veri toplama ve raporlama"
            " süreçlerini kolaylaştıran Sustainage SDG programına erişiminiz tanımlandı."
        ),
        reason="Yeni kullanıcı tanımlandığı için gönderildi",
        support_email="sdg@digage.tr",
    )

    if ok:
        logging.info(" Yeni kullanıcı hoş geldiniz e-postası gönderildi.")
    else:
        logging.info(" Gönderim başarısız.")


if __name__ == "__main__":
    main()
