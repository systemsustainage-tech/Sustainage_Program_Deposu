#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ürün & Teknoloji modülü için veritabanı tablolarını oluşturur/garanti eder.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kökünü path'e ekle
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

 


def ensure_tables(db_path: str) -> None:
    from yonetim.product_technology.digital_security import \
        DigitalSecurityModule
    from yonetim.product_technology.emergency_management import \
        EmergencyManagementModule
    from yonetim.product_technology.innovation import InnovationModule
    from yonetim.product_technology.quality import QualityModule
    logging.info(f"[INFO] DB Path: {db_path}")
    # İnovasyon
    try:
        InnovationModule(db_path).create_innovation_tables()
        logging.info("[OK] innovation_tables")
    except Exception as e:
        logging.error(f"[ERROR] innovation_tables: {e}")
    # Kalite
    try:
        QualityModule(db_path).create_quality_tables()
        logging.info("[OK] quality_tables")
    except Exception as e:
        logging.error(f"[ERROR] quality_tables: {e}")
    # Dijital Güvenlik
    try:
        DigitalSecurityModule(db_path).create_digital_security_tables()
        logging.info("[OK] digital_security_tables")
    except Exception as e:
        logging.error(f"[ERROR] digital_security_tables: {e}")
    # Acil Durum
    try:
        EmergencyManagementModule(db_path).create_emergency_management_tables()
        logging.info("[OK] emergency_management_tables")
    except Exception as e:
        logging.error(f"[ERROR] emergency_management_tables: {e}")


if __name__ == "__main__":
    # Manager'dan db_path al
    from yonetim.product_technology.product_tech_manager import \
        ProductTechManager
    manager = ProductTechManager()
    ensure_tables(manager.db_path)
    logging.info("[DONE] Ürün & Teknoloji tabloları hazır")
