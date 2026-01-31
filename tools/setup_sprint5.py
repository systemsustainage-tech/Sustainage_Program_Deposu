#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sprint 5 Kurulum Scripti
- Sektör standartları iş akışları
- Denetim izi sistemi
- Gelişmiş doğrulama kuralları
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini Python path'e ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def setup_sector_workflows() -> None:
    """Sektör standartları iş akışlarını kur"""
    logging.info("Sektor standartlari is akislari kuruluyor...")
    try:
        from gri.gri_sector_workflows import create_sector_workflows
        create_sector_workflows()
        logging.info("Sektor standartlari is akislari basariyla kuruldu")
        return True
    except Exception as e:
        logging.error(f"Sektor standartlari kurulum hatasi: {e}")
        return False

def setup_audit_trail() -> None:
    """Denetim izi sistemini kur"""
    logging.info("Denetim izi sistemi kuruluyor...")
    try:
        from gri.gri_audit_trail import create_audit_trail
        create_audit_trail()
        logging.info("Denetim izi sistemi basariyla kuruldu")
        return True
    except Exception as e:
        logging.error(f"Denetim izi sistemi kurulum hatasi: {e}")
        return False

def setup_validation_rules() -> None:
    """Gelişmiş doğrulama kurallarını kur"""
    logging.info("Gelismis dogrulama kurallari kuruluyor...")
    try:
        from gri.gri_validation_rules import create_gri_validation_rules
        create_gri_validation_rules()
        logging.info("Gelismis dogrulama kurallari basariyla kuruldu")
        return True
    except Exception as e:
        logging.error(f"Dogrulama kurallari kurulum hatasi: {e}")
        return False

def test_sprint5_features() -> None:
    """Sprint 5 özelliklerini test et"""
    logging.info("Sprint 5 ozellikleri test ediliyor...")
    
    try:
        # Sektör standartları testi
        from gri.gri_sector_workflows import GRISectorWorkflows
        workflows = GRISectorWorkflows()
        standards = workflows.get_sector_standards()
        logging.info(f"Sektor standartlari testi: {len(standards)} sektor bulundu")
        
        # Denetim izi testi
        from gri.gri_audit_trail import GRIAuditTrail
        audit = GRIAuditTrail()
        logs = audit.get_audit_log(limit=5)
        logging.info(f"Denetim izi testi: {len(logs)} kayit bulundu")
        
        # Doğrulama kuralları testi
        from gri.gri_validation_rules import GRIValidationRules
        rules = GRIValidationRules()
        # Basit test - tablo varlığını kontrol et
        conn = rules.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM gri_validation_rules")
        count = cursor.fetchone()[0]
        conn.close()
        logging.info(f"Dogrulama kurallari testi: {count} kural bulundu")
        
        return True
        
    except Exception as e:
        logging.error(f"Sprint 5 test hatasi: {e}")
        return False

def main() -> None:
    """Ana kurulum fonksiyonu"""
    logging.info("Sprint 5 Kurulum Baslatiliyor...")
    logging.info("=" * 50)
    
    success_count = 0
    total_tasks = 4
    
    # 1. Sektör standartları
    if setup_sector_workflows():
        success_count += 1
    
    # 2. Denetim izi sistemi
    if setup_audit_trail():
        success_count += 1
    
    # 3. Doğrulama kuralları
    if setup_validation_rules():
        success_count += 1
    
    # 4. Test
    if test_sprint5_features():
        success_count += 1
    
    logging.info("=" * 50)
    logging.info(f"Sprint 5 Kurulum Tamamlandi: {success_count}/{total_tasks} basarili")
    
    if success_count == total_tasks:
        logging.info("Tum Sprint 5 ozellikleri basariyla kuruldu!")
        logging.info("\nSprint 5 Ozellikleri:")
        logging.info("  - Sektor Standartlari Is Akislari (GRI 11/12/13/14)")
        logging.info("  - Denetim Izi ve Rol Bazli Yetkilendirme")
        logging.info("  - Gelismis Dogrulama Kurallari")
        logging.info("  - Turkce Font Desteği (PDF/Word)")
        logging.info("\nGRI Modulu artik tam kapsamli ve profesyonel!")
        return True
    else:
        logging.error("Bazi ozellikler kurulamadi. Lutfen hatalari kontrol edin.")
        return False

if __name__ == "__main__":
    main()
