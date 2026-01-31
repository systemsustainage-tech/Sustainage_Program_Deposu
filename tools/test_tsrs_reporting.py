#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS Raporlama Test Scripti
TSRS raporlama özelliklerini test eder
"""

import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Proje kök dizinini Python path'e ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def test_tsrs_reporting() -> None:
    """TSRS raporlama özelliklerini test et"""
    logging.info("TSRS Raporlama Test Baslatiliyor...")
    logging.info("=" * 50)
    
    try:
        from tsrs.tsrs_reporting import TSRSReporting

        # TSRS Raporlama instance'ı oluştur
        reporting = TSRSReporting()
        company_id = 1
        reporting_period = "2024"
        
        # Test dizini oluştur
        test_dir = os.path.join(project_root, 'data', 'test_reports')
        os.makedirs(test_dir, exist_ok=True)
        
        logging.info("1. Şirket bilgileri test ediliyor...")
        company_info = reporting.get_company_info(company_id)
        logging.info(f"   Şirket: {company_info['company_name']}")
        logging.info(f"   Sektör: {company_info['sector']}")
        
        logging.info("\n2. TSRS rapor verileri test ediliyor...")
        report_data = reporting.get_tsrs_report_data(company_id, reporting_period)
        logging.info(f"   Toplam kayıt: {len(report_data['data'])}")
        logging.info(f"   Kategori sayısı: {len(report_data['categories'])}")
        
        logging.info("\n3. PDF raporu test ediliyor...")
        pdf_path = os.path.join(test_dir, 'test_tsrs_report.pdf')
        pdf_success = reporting.create_tsrs_pdf_report(company_id, reporting_period, pdf_path)
        logging.info(f"   PDF raporu: {'Başarılı' if pdf_success else 'Başarısız'}")
        
        logging.info("\n4. Word raporu test ediliyor...")
        docx_path = os.path.join(test_dir, 'test_tsrs_report.docx')
        docx_success = reporting.create_tsrs_docx_report(company_id, reporting_period, docx_path)
        logging.info(f"   Word raporu: {'Başarılı' if docx_success else 'Başarısız'}")
        
        logging.info("\n5. Excel raporu test ediliyor...")
        excel_path = os.path.join(test_dir, 'test_tsrs_report.xlsx')
        excel_success = reporting.create_tsrs_excel_report(company_id, reporting_period, excel_path)
        logging.info(f"   Excel raporu: {'Başarılı' if excel_success else 'Başarısız'}")
        
        logging.info("\n6. Kapsamlı rapor test ediliyor...")
        results = reporting.create_comprehensive_tsrs_report(company_id, reporting_period, test_dir)
        logging.info(f"   Kapsamlı rapor sonuçları: {results}")
        
        # Test sonuçları
        success_count = sum([pdf_success, docx_success, excel_success])
        total_tests = 3
        
        logging.info("\n" + "=" * 50)
        logging.info(f"TSRS Raporlama Test Tamamlandi: {success_count}/{total_tests} basarili")
        
        if success_count == total_tests:
            logging.info("Tum TSRS raporlama ozellikleri basariyla test edildi!")
            logging.info(f"Test raporlari: {test_dir}")
            return True
        else:
            logging.info("Bazi raporlama ozellikleri test edilemedi.")
            return False
            
    except Exception as e:
        logging.error(f"TSRS raporlama test edilirken hata: {e}")
        return False

def test_tsrs_gui() -> None:
    """TSRS GUI özelliklerini test et"""
    logging.info("\nTSRS GUI Test Baslatiliyor...")
    logging.info("=" * 50)
    
    try:
        import tkinter as tk

        from tsrs.tsrs_gui import TSRSGUI

        # Test penceresi oluştur
        root = tk.Tk()
        root.withdraw()  # Pencereyi gizle
        
        # TSRS GUI oluştur
        TSRSGUI(root, 1)
        
        logging.info("TSRS GUI basariyla olusturuldu")
        
        # Pencereyi kapat
        root.destroy()
        
        return True
        
    except Exception as e:
        logging.error(f"TSRS GUI test edilirken hata: {e}")
        return False

def main() -> None:
    """Ana test fonksiyonu"""
    logging.info("TSRS Modulu Test Baslatiliyor...")
    logging.info("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    # 1. TSRS Raporlama testi
    if test_tsrs_reporting():
        success_count += 1
    
    # 2. TSRS GUI testi
    if test_tsrs_gui():
        success_count += 1
    
    logging.info("\n" + "=" * 50)
    logging.info(f"TSRS Modulu Test Tamamlandi: {success_count}/{total_tests} basarili")
    
    if success_count == total_tests:
        logging.info("Tum TSRS ozellikleri basariyla test edildi!")
        return True
    else:
        logging.info("Bazi ozellikler test edilemedi.")
        return False

if __name__ == "__main__":
    main()
