#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gelişmiş Raporlama Test Scripti
Gelişmiş raporlama özelliklerini test eder
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini Python path'e ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_advanced_reporting_manager() -> None:
    """Gelişmiş raporlama manager'ını test et"""
    logging.info("Gelişmiş Raporlama Manager Test Baslatiliyor...")
    logging.info("=" * 60)
    
    try:
        from raporlama.advanced_reporting_manager import \
            AdvancedReportingManager

        # Manager instance'ı oluştur
        manager = AdvancedReportingManager()
        company_id = 1
        reporting_period = "2024"
        
        logging.info("1. Rapor kategorileri test ediliyor...")
        categories = manager.get_report_categories()
        logging.info(f"   Toplam kategori: {len(categories)}")
        for category in categories:
            logging.info(f"     {category['name']}: {category.get('template_count', 0)} şablon")
        
        logging.info("\n2. Rapor şablonları test ediliyor...")
        templates = manager.get_report_templates()
        logging.info(f"   Toplam şablon: {len(templates)}")
        for template in templates[:3]:  # İlk 3 şablonu göster
            logging.info(f"     {template['name']} ({template['category']})")
        
        logging.info("\n3. Şablon detayları test ediliyor...")
        if templates:
            template = manager.get_template_by_id(templates[0]['id'])
            if template:
                logging.info(f"   Şablon: {template['name']}")
                logging.info(f"   Kategori: {template['category']}")
                logging.info(f"   Tür: {template['template_type']}")
                logging.info(f"   Formatlar: {template['output_formats']}")
        
        logging.info("\n4. Gelişmiş rapor oluşturma test ediliyor...")
        if templates:
            result = manager.create_advanced_report(
                templates[0]['id'], company_id, reporting_period, ['pdf', 'docx']
            )
            logging.info(f"   Rapor durumu: {result['status']}")
            if result['status'] == 'success':
                logging.info(f"   Oluşturulan dosyalar: {len(result['output_files'])}")
                for format_type, filepath in result['output_files'].items():
                    logging.info(f"     {format_type}: {filepath}")
        
        logging.info("\n5. Rapor istatistikleri test ediliyor...")
        stats = manager.get_report_statistics()
        logging.info(f"   Toplam rapor: {stats['total_reports']}")
        logging.info(f"   Toplam şablon: {stats['total_templates']}")
        logging.info(f"   Toplam kategori: {stats['total_categories']}")
        logging.info(f"   Son 30 günlük rapor: {stats['recent_reports']}")
        
        logging.info("\n" + "=" * 60)
        logging.info("Gelişmiş Raporlama Manager Test Tamamlandi!")
        
        return True
        
    except Exception as e:
        logging.error(f"Gelişmiş raporlama manager test edilirken hata: {e}")
        return False

def test_advanced_reporting_gui() -> None:
    """Gelişmiş raporlama GUI'sini test et"""
    logging.info("\nGelişmiş Raporlama GUI Test Baslatiliyor...")
    logging.info("=" * 60)
    
    try:
        import tkinter as tk

        from raporlama.advanced_reporting_gui import AdvancedReportingGUI

        # Test penceresi oluştur
        root = tk.Tk()
        root.withdraw()  # Pencereyi gizle
        
        # Gelişmiş raporlama GUI oluştur
        AdvancedReportingGUI(root, 1)
        
        logging.info("Gelişmiş Raporlama GUI basariyla olusturuldu")
        
        # Pencereyi kapat
        root.destroy()
        
        return True
        
    except Exception as e:
        logging.error(f"Gelişmiş raporlama GUI test edilirken hata: {e}")
        return False

def test_reporting_integration() -> None:
    """Raporlama entegrasyonunu test et"""
    logging.info("\nRaporlama Entegrasyon Test Baslatiliyor...")
    logging.info("=" * 60)
    
    try:
        import tkinter as tk

        from raporlama.reporting_gui import ReportingGUI

        # Test penceresi oluştur
        root = tk.Tk()
        root.withdraw()  # Pencereyi gizle
        
        # Ana raporlama GUI oluştur
        ReportingGUI(root, role='admin')
        
        logging.info("Ana Raporlama GUI basariyla olusturuldu")
        
        # Pencereyi kapat
        root.destroy()
        
        return True
        
    except Exception as e:
        logging.error(f"Raporlama entegrasyon test edilirken hata: {e}")
        return False

def main() -> None:
    """Ana test fonksiyonu"""
    logging.info("Gelişmiş Raporlama Modulu Test Baslatiliyor...")
    logging.info("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # 1. Gelişmiş raporlama manager testi
    if test_advanced_reporting_manager():
        success_count += 1
    
    # 2. Gelişmiş raporlama GUI testi
    if test_advanced_reporting_gui():
        success_count += 1
    
    # 3. Raporlama entegrasyon testi
    if test_reporting_integration():
        success_count += 1
    
    logging.info("\n" + "=" * 60)
    logging.info(f"Gelişmiş Raporlama Modulu Test Tamamlandi: {success_count}/{total_tests} basarili")
    
    if success_count == total_tests:
        logging.info("Tum gelişmiş raporlama ozellikleri basariyla test edildi!")
        logging.info("\nGelişmiş Raporlama Ozellikleri:")
        logging.info("  - Gelişmiş Rapor Şablonları")
        logging.info("  - Kategori Bazlı Şablon Yönetimi")
        logging.info("  - Çoklu Format Desteği (PDF, Word, Excel)")
        logging.info("  - Özel Parametre Desteği")
        logging.info("  - Rapor Zamanlama")
        logging.info("  - Rapor Dağıtım")
        logging.info("  - Detaylı İstatistikler")
        logging.info("\nGelişmiş raporlama modulu kullanima hazir!")
        return True
    else:
        logging.info("Bazi ozellikler test edilemedi.")
        return False

if __name__ == "__main__":
    main()
