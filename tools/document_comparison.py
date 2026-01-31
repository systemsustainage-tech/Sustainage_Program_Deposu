import logging
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doküman Karşılaştırma ve İçe Aktarma Aracı
PDF/DOCX içeriklerini parse edip modüllerle fark raporu üretme
"""

import io
import json
import os
import re
import sqlite3
import sys
from datetime import datetime
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Windows ortamında UTF-8 desteğini güvenli şekilde etkinleştir
if os.name == 'nt' and not os.getenv('PYTEST_CURRENT_TEST'):
    try:
        # stdout
        if getattr(sys.stdout, 'buffer', None) is not None and not getattr(sys.stdout, 'closed', False):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        elif sys.stdout is None:
            sys.stdout = open(os.devnull, 'w', encoding='utf-8')

        # stderr
        if getattr(sys.stderr, 'buffer', None) is not None and not getattr(sys.stderr, 'closed', False):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        elif sys.stderr is None or getattr(sys.stderr, 'closed', False):
            sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    except Exception:
        # Bazı GUI ortamlarında (pythonw.exe) stdout/stderr None olabilir; devnull ile yut
        try:
            if sys.stdout is None or getattr(sys.stdout, 'closed', False):
                sys.stdout = open(os.devnull, 'w', encoding='utf-8')
            if sys.stderr is None or getattr(sys.stderr, 'closed', False):
                sys.stderr = open(os.devnull, 'w', encoding='utf-8')
        except Exception as e:
            logging.error(f"Silent error caught: {str(e)}")

# PDF parsing
try:
    from pdfminer.high_level import extract_text as pdf_extract_text
    from pdfminer.layout import LAParams
    PDF_AVAILABLE = True
except ImportError:
    logging.info("️  pdfminer.six yüklü değil. PDF desteği için: pip install pdfminer.six")
    PDF_AVAILABLE = False

# DOCX parsing
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    logging.info("️  python-docx yüklü değil. DOCX desteği için: pip install python-docx")
    DOCX_AVAILABLE = False

class DocumentComparison:
    """Doküman karşılaştırma ve analiz"""
    
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        
        # Anahtar kelime kategorileri
        self.keyword_categories = {
            'SDG': [
                'sürdürülebilir kalkınma', 'sustainable development', 'sdg',
                'yoksulluk', 'poverty', 'açlık', 'hunger', 'sağlık', 'health',
                'eğitim', 'education', 'cinsiyet eşitliği', 'gender equality',
                'temiz su', 'clean water', 'enerji', 'energy', 'istihdam', 'employment',
                'altyapı', 'infrastructure', 'eşitsizlik', 'inequality',
                'şehir', 'city', 'tüketim', 'consumption', 'iklim', 'climate',
                'okyanus', 'ocean', 'karasal yaşam', 'terrestrial', 'barış', 'peace'
            ],
            'GRI': [
                'gri', 'global reporting', 'raporlama', 'reporting',
                'ekonomik performans', 'economic performance',
                'çevresel', 'environmental', 'sosyal', 'social',
                'emisyon', 'emission', 'atık', 'waste', 'su', 'water',
                'çalışan', 'employee', 'tedarikçi', 'supplier',
                'insan hakları', 'human rights', 'toplum', 'community'
            ],
            'TSRS': [
                'tsrs', 'türkiye sürdürülebilirlik', 'turkish sustainability',
                'çevresel', 'sosyal', 'yönetişim', 'governance',
                'iklim değişikliği', 'climate change', 'su yönetimi', 'water management',
                'atık yönetimi', 'waste management', 'biyoçeşitlilik', 'biodiversity',
                'çalışan hakları', 'employee rights', 'tedarik zinciri', 'supply chain'
            ],
            'ESG': [
                'esg', 'environmental social governance',
                'çevresel sosyal yönetişim', 'sürdürülebilirlik', 'sustainability',
                'karbon ayak izi', 'carbon footprint', 'sera gazı', 'greenhouse gas',
                'enerji verimliliği', 'energy efficiency', 'yenilenebilir enerji', 'renewable energy',
                'çeşitlilik', 'diversity', 'kapsayıcılık', 'inclusion',
                'etik', 'ethics', 'uyum', 'compliance', 'risk yönetimi', 'risk management'
            ],
            'Carbon': [
                'karbon', 'carbon', 'emisyon', 'emission', 'sera gazı', 'greenhouse',
                'co2', 'kapsam 1', 'scope 1', 'kapsam 2', 'scope 2', 'kapsam 3', 'scope 3',
                'karbon nötr', 'carbon neutral', 'net sıfır', 'net zero'
            ],
            'Water': [
                'su', 'water', 'su tüketimi', 'water consumption',
                'su ayak izi', 'water footprint', 'atık su', 'wastewater',
                'su verimliliği', 'water efficiency', 'su tasarrufu', 'water saving'
            ],
            'Waste': [
                'atık', 'waste', 'geri dönüşüm', 'recycling',
                'döngüsel ekonomi', 'circular economy', 'sıfır atık', 'zero waste',
                'kompost', 'compost', 'tehlikeli atık', 'hazardous waste'
            ],
            'Supply_Chain': [
                'tedarik zinciri', 'supply chain', 'tedarikçi', 'supplier',
                'satın alma', 'procurement', 'sorumlu tedarik', 'responsible sourcing',
                'tedarikçi değerlendirme', 'supplier assessment'
            ]
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF'den metin çıkar"""
        if not PDF_AVAILABLE:
            raise ImportError("pdfminer.six yüklü değil")
        
        try:
            text = pdf_extract_text(pdf_path, laparams=LAParams())
            return text
        except Exception as e:
            logging.error(f"PDF metin çıkarma hatası: {e}")
            return ""
    
    def extract_text_from_docx(self, docx_path: str) -> str:
        """DOCX'den metin çıkar"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx yüklü değil")
        
        try:
            doc = Document(docx_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            logging.error(f"DOCX metin çıkarma hatası: {e}")
            return ""
    
    def extract_text(self, file_path: str) -> str:
        """Dosyadan metin çıkar"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Desteklenmeyen dosya formatı: {ext}")
    
    def analyze_keywords(self, text: str) -> Dict[str, List[Tuple[str, int]]]:
        """Metindeki anahtar kelimeleri analiz et"""
        text_lower = text.lower()
        results = {}
        
        for category, keywords in self.keyword_categories.items():
            matches = []
            for keyword in keywords:
                count = len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower))
                if count > 0:
                    matches.append((keyword, count))
            
            # En çok geçen kelimelere göre sırala
            matches.sort(key=lambda x: x[1], reverse=True)
            results[category] = matches
        
        return results
    
    def extract_metrics(self, text: str) -> List[Dict]:
        """Metinden metrikleri çıkar"""
        metrics = []
        
        # Sayısal değerler ve birimler
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*(?:ton|kg|g)\s*(?:co2|karbon|emisyon)', 'carbon', 'emission'),
            (r'(\d+(?:\.\d+)?)\s*(?:m3|litre|lt)\s*(?:su|water)', 'water', 'consumption'),
            (r'(\d+(?:\.\d+)?)\s*(?:ton|kg)\s*(?:atık|waste)', 'waste', 'amount'),
            (r'(\d+(?:\.\d+)?)\s*(?:%|yüzde)\s*(?:geri dönüşüm|recycling)', 'waste', 'recycling_rate'),
            (r'(\d+(?:\.\d+)?)\s*(?:kwh|mwh|gwh)\s*(?:enerji|energy)', 'energy', 'consumption'),
        ]
        
        for pattern, module, metric_type in patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                value = match.group(1)
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                metrics.append({
                    'module': module,
                    'metric_type': metric_type,
                    'value': value,
                    'context': context.strip()
                })
        
        return metrics
    
    def get_module_data(self, company_id: int) -> Dict:
        """Modül verilerini al"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        module_data = {}
        
        try:
            # SDG verileri
            cursor.execute("""
                SELECT COUNT(DISTINCT r.indicator_id) as answered,
                       COUNT(DISTINCT i.id) as total
                FROM sdg_indicators i
                LEFT JOIN responses r ON i.id = r.indicator_id AND r.company_id = ?
            """, (company_id,))
            row = cursor.fetchone()
            module_data['SDG'] = {
                'answered': row[0] if row else 0,
                'total': row[1] if row else 0,
                'percentage': (row[0] / row[1] * 100) if row and row[1] > 0 else 0
            }
            
            # GRI verileri
            cursor.execute("""
                SELECT COUNT(DISTINCT r.indicator_id) as answered,
                       COUNT(DISTINCT i.id) as total
                FROM gri_indicators i
                LEFT JOIN gri_responses r ON i.id = r.indicator_id AND r.company_id = ?
            """, (company_id,))
            row = cursor.fetchone()
            module_data['GRI'] = {
                'answered': row[0] if row else 0,
                'total': row[1] if row else 0,
                'percentage': (row[0] / row[1] * 100) if row and row[1] > 0 else 0
            }
            
            # TSRS verileri
            cursor.execute("""
                SELECT COUNT(DISTINCT r.indicator_id) as answered,
                       COUNT(DISTINCT i.id) as total
                FROM tsrs_indicators i
                LEFT JOIN tsrs_responses r ON i.id = r.indicator_id AND r.company_id = ?
            """, (company_id,))
            row = cursor.fetchone()
            module_data['TSRS'] = {
                'answered': row[0] if row else 0,
                'total': row[1] if row else 0,
                'percentage': (row[0] / row[1] * 100) if row and row[1] > 0 else 0
            }
            
            # Karbon verileri
            cursor.execute("""
                SELECT COUNT(*) FROM carbon_footprint WHERE company_id = ?
            """, (company_id,))
            module_data['Carbon'] = {'records': cursor.fetchone()[0] or 0}
            
            # Su verileri
            cursor.execute("""
                SELECT COUNT(*) FROM water_consumption WHERE company_id = ?
            """, (company_id,))
            module_data['Water'] = {'records': cursor.fetchone()[0] or 0}
            
            # Atık verileri
            cursor.execute("""
                SELECT COUNT(*) FROM waste_records WHERE company_id = ?
            """, (company_id,))
            module_data['Waste'] = {'records': cursor.fetchone()[0] or 0}
            
            # Tedarik zinciri verileri
            cursor.execute("""
                SELECT COUNT(*) FROM supplier_assessments WHERE company_id = ?
            """, (company_id,))
            module_data['Supply_Chain'] = {'records': cursor.fetchone()[0] or 0}
            
        except Exception as e:
            logging.error(f"Modül verileri alma hatası: {e}")
        finally:
            conn.close()
        
        return module_data
    
    def compare_document_with_modules(self, file_path: str, company_id: int) -> Dict:
        """Dokümanı modüllerle karşılaştır"""
        logging.info(f"\n Doküman Analiz Ediliyor: {os.path.basename(file_path)}")
        logging.info("=" * 60)
        
        # Metni çıkar
        try:
            text = self.extract_text(file_path)
            if not text:
                return {'error': 'Metin çıkarılamadı'}
            
            logging.info(f" Metin çıkarıldı: {len(text)} karakter")
        except Exception as e:
            return {'error': f'Metin çıkarma hatası: {e}'}
        
        # Anahtar kelime analizi
        logging.info("\n Anahtar Kelime Analizi...")
        keywords = self.analyze_keywords(text)
        
        for category, matches in keywords.items():
            if matches:
                logging.info(f"\n  {category}:")
                for keyword, count in matches[:5]:  # İlk 5
                    logging.info(f"    - {keyword}: {count} kez")
        
        # Metrik çıkarma
        logging.info("\n Metrik Çıkarma...")
        metrics = self.extract_metrics(text)
        logging.info(f"  Bulunan metrik sayısı: {len(metrics)}")
        
        for metric in metrics[:5]:  # İlk 5
            logging.info(f"    - {metric['module']}.{metric['metric_type']}: {metric['value']}")
        
        # Modül verileri
        logging.info("\n Modül Verileri Kontrol Ediliyor...")
        module_data = self.get_module_data(company_id)
        
        # Karşılaştırma
        comparison = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'analyzed_at': datetime.now().isoformat(),
            'text_length': len(text),
            'keywords': keywords,
            'metrics': metrics,
            'module_data': module_data,
            'gaps': self.identify_gaps(keywords, metrics, module_data),
            'recommendations': self.generate_recommendations(keywords, metrics, module_data)
        }
        
        return comparison
    
    def identify_gaps(self, keywords: Dict, metrics: List[Dict], module_data: Dict) -> List[Dict]:
        """Eksiklikleri belirle"""
        gaps = []
        
        # Anahtar kelime var ama modül verisi yok
        for category, matches in keywords.items():
            if matches and category in module_data:
                data = module_data[category]
                
                # SDG/GRI/TSRS için
                if 'percentage' in data and data['percentage'] < 50:
                    gaps.append({
                        'type': 'low_coverage',
                        'category': category,
                        'severity': 'high',
                        'description': f"{category} dokümanda bahsedilmiş ama sistem verisi düşük (%{data['percentage']:.1f})",
                        'keyword_count': sum(count for _, count in matches),
                        'current_coverage': data['percentage']
                    })
                
                # Karbon/Su/Atık için
                if 'records' in data and data['records'] == 0:
                    gaps.append({
                        'type': 'missing_data',
                        'category': category,
                        'severity': 'high',
                        'description': f"{category} dokümanda bahsedilmiş ama sistemde veri yok",
                        'keyword_count': sum(count for _, count in matches),
                        'current_records': 0
                    })
        
        # Metrik var ama modülde kayıt yok
        metric_modules = set(m['module'] for m in metrics)
        for module in metric_modules:
            module_key = module.capitalize()
            if module_key in module_data:
                data = module_data[module_key]
                if 'records' in data and data['records'] == 0:
                    gaps.append({
                        'type': 'metric_without_data',
                        'category': module_key,
                        'severity': 'medium',
                        'description': f"{module_key} metrikleri dokümanda var ama sistemde kayıt yok",
                        'metric_count': len([m for m in metrics if m['module'] == module])
                    })
        
        return gaps
    
    def generate_recommendations(self, keywords: Dict, metrics: List[Dict], module_data: Dict) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        # Her kategori için öneriler
        for category, matches in keywords.items():
            if not matches:
                continue
            
            if category in module_data:
                data = module_data[category]
                
                # SDG/GRI/TSRS önerileri
                if 'percentage' in data:
                    if data['percentage'] < 30:
                        recommendations.append(
                            f" {category}: Dokümanda yüksek vurgu var ama sistem verisi çok düşük. "
                            f"Öneri: {category} modülünde veri girişi yapın."
                        )
                    elif data['percentage'] < 70:
                        recommendations.append(
                            f" {category}: Sistem verisi orta seviyede. "
                            f"Öneri: Eksik göstergeleri tamamlayın."
                        )
                    else:
                        recommendations.append(
                            f" {category}: İyi seviyede veri var. Düzenli güncelleyin."
                        )
                
                # Karbon/Su/Atık önerileri
                if 'records' in data:
                    if data['records'] == 0:
                        recommendations.append(
                            f" {category}: Dokümanda metrikler var ama sistemde kayıt yok. "
                            f"Öneri: {category} modülünde veri girişi başlatın."
                        )
                    elif data['records'] < 10:
                        recommendations.append(
                            f" {category}: Az sayıda kayıt var. "
                            f"Öneri: Düzenli veri girişi yapın."
                        )
        
        # Metrik bazlı öneriler
        if metrics:
            recommendations.append(
                f" Dokümanda {len(metrics)} adet ölçülebilir metrik bulundu. "
                f"Bu metrikleri ilgili modüllere aktarın."
            )
        
        return recommendations
    
    def generate_comparison_report(self, comparison: Dict, output_path: str = None) -> str:
        """Karşılaştırma raporu oluştur"""
        if not output_path:
            output_dir = 'reports/document_comparison'
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(output_dir, f'comparison_report_{timestamp}.txt')
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("DOKÜMAN KARŞILAŞTIRMA RAPORU\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Dosya: {comparison['file_name']}\n")
                f.write(f"Analiz Tarihi: {comparison['analyzed_at']}\n")
                f.write(f"Metin Uzunluğu: {comparison['text_length']} karakter\n\n")
                
                # Anahtar kelime özeti
                f.write("-" * 80 + "\n")
                f.write("ANAHTAR KELİME ANALİZİ\n")
                f.write("-" * 80 + "\n\n")
                
                for category, matches in comparison['keywords'].items():
                    if matches:
                        f.write(f"{category}:\n")
                        for keyword, count in matches[:10]:
                            f.write(f"  - {keyword}: {count} kez\n")
                        f.write("\n")
                
                # Metrik özeti
                f.write("-" * 80 + "\n")
                f.write("BULUNAN METRİKLER\n")
                f.write("-" * 80 + "\n\n")
                
                for metric in comparison['metrics']:
                    f.write(f"Modül: {metric['module']}\n")
                    f.write(f"Metrik: {metric['metric_type']}\n")
                    f.write(f"Değer: {metric['value']}\n")
                    f.write(f"Bağlam: {metric['context']}\n\n")
                
                # Modül durumu
                f.write("-" * 80 + "\n")
                f.write("MODÜL DURUM KARŞILAŞTIRMASI\n")
                f.write("-" * 80 + "\n\n")
                
                for module, data in comparison['module_data'].items():
                    f.write(f"{module}:\n")
                    if 'percentage' in data:
                        f.write(f"  Tamamlanma: %{data['percentage']:.1f}\n")
                        f.write(f"  Cevaplanan: {data['answered']}/{data['total']}\n")
                    if 'records' in data:
                        f.write(f"  Kayıt Sayısı: {data['records']}\n")
                    f.write("\n")
                
                # Eksiklikler
                f.write("-" * 80 + "\n")
                f.write("TESPİT EDİLEN EKSİKLİKLER\n")
                f.write("-" * 80 + "\n\n")
                
                for gap in comparison['gaps']:
                    severity_icon = {'high': '', 'medium': '', 'low': ''}.get(gap['severity'], '')
                    f.write(f"{severity_icon} {gap['type'].upper()}\n")
                    f.write(f"Kategori: {gap['category']}\n")
                    f.write(f"Açıklama: {gap['description']}\n\n")
                
                # Öneriler
                f.write("-" * 80 + "\n")
                f.write("ÖNERİLER\n")
                f.write("-" * 80 + "\n\n")
                
                for i, recommendation in enumerate(comparison['recommendations'], 1):
                    f.write(f"{i}. {recommendation}\n\n")
                
                f.write("=" * 80 + "\n")
            
            logging.info(f"\n Rapor oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"Rapor oluşturma hatası: {e}")
            return None
    
    def generate_json_report(self, comparison: Dict, output_path: str = None) -> str:
        """JSON formatında rapor oluştur"""
        if not output_path:
            output_dir = 'reports/document_comparison'
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(output_dir, f'comparison_report_{timestamp}.json')
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(comparison, f, ensure_ascii=False, indent=2)
            
            logging.info(f" JSON raporu oluşturuldu: {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"JSON rapor oluşturma hatası: {e}")
            return None

def main() -> None:
    """Ana fonksiyon"""
    logging.info(" Doküman Karşılaştırma Aracı")
    logging.info("=" * 60)
    
    # Komut satırı argümanları
    if len(sys.argv) < 2:
        logging.info("Kullanım: python tools/document_comparison.py <dosya_yolu> [company_id]")
        logging.info("\nÖrnek:")
        logging.info("  python tools/document_comparison.py rapor.pdf 1")
        logging.info("  python tools/document_comparison.py surdurulebilirlik_raporu.docx 1")
        return
    
    file_path = sys.argv[1]
    company_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    # Dosya kontrolü
    if not os.path.exists(file_path):
        logging.info(f" Dosya bulunamadı: {file_path}")
        return
    
    # Veritabanı yolu
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'data', 'sdg_desktop.sqlite')
    
    # Karşılaştırma yap
    comparator = DocumentComparison(db_path)
    comparison = comparator.compare_document_with_modules(file_path, company_id)
    
    if 'error' in comparison:
        logging.error(f"\n Hata: {comparison['error']}")
        return
    
    # Raporları oluştur
    logging.info("\n Raporlar Oluşturuluyor...")
    txt_report = comparator.generate_comparison_report(comparison)
    json_report = comparator.generate_json_report(comparison)
    
    # Özet
    logging.info("\n" + "=" * 60)
    logging.info(" Analiz Tamamlandı!")
    logging.info("\n Özet:")
    logging.info(f"  Anahtar Kelime Kategorisi: {len([k for k in comparison['keywords'].values() if k])}")
    logging.info(f"  Bulunan Metrik: {len(comparison['metrics'])}")
    logging.info(f"  Tespit Edilen Eksiklik: {len(comparison['gaps'])}")
    logging.info(f"  Öneri Sayısı: {len(comparison['recommendations'])}")
    
    logging.info("\n Raporlar:")
    if txt_report:
        logging.info(f"  - TXT: {txt_report}")
    if json_report:
        logging.info(f"  - JSON: {json_report}")

if __name__ == '__main__':
    main()
