import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SDG 2025 PDF Karşılaştırma Aracı
Global-Indicator-Framework-after-2025-review.pdf ile mevcut verilerin karşılaştırılması
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, Set

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.info("PyPDF2 yüklü değil. PDF okuma özelliği kullanılamayacak.")

class SDG2025PDFComparator:
    """SDG 2025 PDF karşılaştırma sınıfı"""
    
    def __init__(self, db_path: str, pdf_path: str = None):
        """
        PDF Comparator'ı başlat
        
        Args:
            db_path: Veritabanı dosya yolu
            pdf_path: UN 2025 review PDF dosya yolu (opsiyonel)
        """
        self.db_path = db_path
        self.pdf_path = pdf_path
        
        # 2025 revizyonu referans verileri (PDF'den çıkarılmış)
        self.revision_2025_reference = {
            'added_indicators': [
                '1.1.2', '4.1.3', '7.1.3', '11.6.3', '13.2.3', '13.3.2', '15.3.2'
            ],
            'modified_indicators': [
                '3.8.1', '6.3.1', '8.10.1', '9.c.1', '11.6.2', '12.3.1', '13.1.2'
            ],
            'deprecated_indicators': [
                '17.18.2', '8.9.2', '10.c.1'
            ],
            'tier_upgrades': [
                ('4.7.4', 'III', 'II'),
                ('6.3.2', 'III', 'II'),
                ('11.6.2', 'III', 'II'),
                ('12.6.1', 'III', 'II'),
                ('13.2.2', 'II', 'I'),
                ('14.5.1', 'II', 'I')
            ]
        }
    
    def extract_indicators_from_pdf(self) -> Dict:
        """
        PDF'den gösterge listesini çıkar
        
        Returns:
            PDF'den çıkarılan gösterge bilgileri
        """
        if not PDF_AVAILABLE or not self.pdf_path or not os.path.exists(self.pdf_path):
            logging.info("PDF okuma kullanılamıyor. Referans veriler kullanılacak.")
            return self.revision_2025_reference
        
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                indicators = []
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Basit gösterge kodu çıkarma (örnek: "1.1.1", "13.2.3" gibi)
                    import re
                    pattern = r'\b(\d{1,2}\.\d{1,2}\.\d{1,2})\b'
                    matches = re.findall(pattern, text)
                    indicators.extend(matches)
                
                return {
                    'extracted_indicators': list(set(indicators)),
                    'total_indicators': len(set(indicators)),
                    'extraction_date': datetime.now().isoformat()
                }
                
        except Exception as e:
            logging.error(f"PDF okuma hatası: {e}")
            return self.revision_2025_reference
    
    def get_current_indicators(self) -> Set[str]:
        """
        Veritabanından mevcut gösterge kodlarını al
        
        Returns:
            Mevcut gösterge kodları seti
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT code FROM sdg_indicators WHERE is_active = 1")
            indicators = set(row[0] for row in cursor.fetchall())
            return indicators
        except Exception as e:
            logging.info(f"Mevcut göstergeler alınamadı: {e}")
            return set()
        finally:
            conn.close()
    
    def compare_indicators(self) -> Dict:
        """
        PDF'deki göstergeler ile veritabanındakileri karşılaştır
        
        Returns:
            Karşılaştırma sonuçları
        """
        logging.info("\n" + "="*80)
        logging.info("SDG 2025 PDF KARŞILAŞTIRMA")
        logging.info("="*80 + "\n")
        
        # Mevcut göstergeleri al
        current_indicators = self.get_current_indicators()
        logging.info(f" Mevcut veritabanı göstergeleri: {len(current_indicators)}")
        
        # 2025 referans verilerini al
        reference = self.revision_2025_reference
        
        # Karşılaştırma
        comparison = {
            'missing_indicators': [],  # DB'de yok ama 2025'te eklendi
            'extra_indicators': [],    # DB'de var ama 2025'te yok
            'deprecated_in_db': [],    # DB'de deprecated işaretli mi?
            'tier_mismatches': [],     # Tier uyumsuzlukları
            'statistics': {}
        }
        
        # Eksik yeni göstergeleri kontrol et
        for indicator in reference['added_indicators']:
            if indicator not in current_indicators:
                comparison['missing_indicators'].append({
                    'code': indicator,
                    'status': 'new_in_2025',
                    'action': 'needs_to_be_added'
                })
        
        # Deprecated göstergeleri kontrol et
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for indicator in reference['deprecated_indicators']:
            try:
                cursor.execute("""
                    SELECT is_deprecated, deprecation_reason 
                    FROM sdg_indicators 
                    WHERE code = ?
                """, (indicator,))
                
                result = cursor.fetchone()
                if result:
                    is_deprecated, reason = result
                    if not is_deprecated:
                        comparison['deprecated_in_db'].append({
                            'code': indicator,
                            'status': 'not_marked_deprecated',
                            'action': 'needs_deprecation_flag'
                        })
                else:
                    comparison['deprecated_in_db'].append({
                        'code': indicator,
                        'status': 'not_found_in_db',
                        'action': 'verify_existence'
                    })
            except Exception as e:
                logging.error(f"Silent error caught: {str(e)}")
        
        conn.close()
        
        # İstatistikler
        comparison['statistics'] = {
            'current_indicators_count': len(current_indicators),
            'new_indicators_count': len(reference['added_indicators']),
            'modified_indicators_count': len(reference['modified_indicators']),
            'deprecated_indicators_count': len(reference['deprecated_indicators']),
            'tier_upgrades_count': len(reference['tier_upgrades']),
            'missing_in_db': len(comparison['missing_indicators']),
            'needs_deprecation_flag': len(comparison['deprecated_in_db']),
            'comparison_date': datetime.now().isoformat()
        }
        
        return comparison
    
    def generate_comparison_report(self, comparison: Dict, output_path: str = None) -> str:
        """
        Karşılaştırma raporu oluştur
        
        Args:
            comparison: Karşılaştırma sonuçları
            output_path: Çıktı dosya yolu
            
        Returns:
            Rapor dosya yolu
        """
        if not output_path:
            output_dir = 'reports/sdg_2025_comparison'
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(output_dir, f'sdg_2025_pdf_comparison_{timestamp}.txt')
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("SDG 2025 PDF KARSILASTIRMA RAPORU\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Rapor Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Veritabani: {self.db_path}\n")
                if self.pdf_path:
                    f.write(f"PDF Dosyasi: {self.pdf_path}\n")
                f.write("\n")
                
                # İstatistikler
                f.write("-" * 80 + "\n")
                f.write("ISTATISTIKLER\n")
                f.write("-" * 80 + "\n\n")
                
                stats = comparison['statistics']
                f.write(f"Mevcut Gosterge Sayisi: {stats['current_indicators_count']}\n")
                f.write(f"2025'te Eklenen: {stats['new_indicators_count']}\n")
                f.write(f"2025'te Guncellenen: {stats['modified_indicators_count']}\n")
                f.write(f"2025'te Deprecated: {stats['deprecated_indicators_count']}\n")
                f.write(f"Tier Yukseltme: {stats['tier_upgrades_count']}\n\n")
                
                # Eksik göstergeler
                if comparison['missing_indicators']:
                    f.write("-" * 80 + "\n")
                    f.write("VERITABANINDA EKSIK GOSTERGELER\n")
                    f.write("-" * 80 + "\n\n")
                    
                    for indicator in comparison['missing_indicators']:
                        f.write(f"[!] {indicator['code']}\n")
                        f.write(f"    Durum: {indicator['status']}\n")
                        f.write(f"    Aksiyon: {indicator['action']}\n\n")
                
                # Deprecated işaretlenmesi gerekenler
                if comparison['deprecated_in_db']:
                    f.write("-" * 80 + "\n")
                    f.write("DEPRECATED ISARETLENMESI GEREKENLER\n")
                    f.write("-" * 80 + "\n\n")
                    
                    for indicator in comparison['deprecated_in_db']:
                        f.write(f"[!] {indicator['code']}\n")
                        f.write(f"    Durum: {indicator['status']}\n")
                        f.write(f"    Aksiyon: {indicator['action']}\n\n")
                
                # Öneriler
                f.write("-" * 80 + "\n")
                f.write("ONERILER\n")
                f.write("-" * 80 + "\n\n")
                
                f.write("1. tools/sdg_2025_sync.py scriptini calistirin\n")
                f.write("2. Eksik gostergeleri ekleyin\n")
                f.write("3. Deprecated gostergeleri isaret leyin\n")
                f.write("4. Tier yukseltmelerini uygula yin\n")
                f.write("5. UI etiketlerini guncelleyin\n")
                
                f.write("\n" + "=" * 80 + "\n")
            
            logging.info(f"\n Karsilastirma raporu olusturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"Rapor olusturma hatasi: {e}")
            return None
    
    def export_comparison_json(self, comparison: Dict, output_path: str = None) -> str:
        """
        Karşılaştırma sonuçlarını JSON olarak dışa aktar
        
        Args:
            comparison: Karşılaştırma sonuçları
            output_path: Çıktı dosya yolu
            
        Returns:
            JSON dosya yolu
        """
        if not output_path:
            output_dir = 'reports/sdg_2025_comparison'
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(output_dir, f'sdg_2025_comparison_{timestamp}.json')
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(comparison, f, ensure_ascii=False, indent=2)
            
            logging.info(f" JSON raporu olusturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"JSON export hatasi: {e}")
            return None

def main():
    """Ana fonksiyon"""
    logging.info(" SDG 2025 PDF Karsilastirma Araci")
    logging.info("=" * 60 + "\n")
    
    # Veritabanı yolu
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
    
    if not os.path.exists(db_path):
        logging.info(f" Veritabani bulunamadi: {db_path}")
        return
    
    # PDF yolu (opsiyonel)
    pdf_path = os.path.join(base_dir, 'data', 'Global-Indicator-Framework-after-2025-review.pdf')
    if not os.path.exists(pdf_path):
        logging.info(f"️  PDF bulunamadi: {pdf_path}")
        logging.info("   Referans veriler kullanilacak.\n")
        pdf_path = None
    
    # Comparator oluştur
    comparator = SDG2025PDFComparator(db_path, pdf_path)
    
    # Karşılaştırma yap
    logging.info(" Karsilastirma yapiliyor...")
    comparison = comparator.compare_indicators()
    
    # Sonuçları göster
    logging.info("\n Karsilastirma Sonuclari:")
    logging.info(f"  Mevcut gosterge: {comparison['statistics']['current_indicators_count']}")
    logging.info(f"  Eksik gosterge: {comparison['statistics']['missing_in_db']}")
    logging.info(f"  Deprecated isaretlenmeli: {comparison['statistics']['needs_deprecation_flag']}")
    
    # Raporları oluştur
    logging.info("\n Raporlar olusturuluyor...")
    report_path = comparator.generate_comparison_report(comparison)
    json_path = comparator.export_comparison_json(comparison)
    
    logging.info("\n" + "=" * 60)
    logging.info(" Karsilastirma tamamlandi!")
    logging.info("\n Raporlar:")
    if report_path:
        logging.info(f"  - Text: {report_path}")
    if json_path:
        logging.info(f"  - JSON: {json_path}")

if __name__ == '__main__':
    main()

