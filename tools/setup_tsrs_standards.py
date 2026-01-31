#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TSRS Standartları ve Göstergelerini Veritabanına Yükleme
Türkiye Sürdürülebilirlik Raporlama Standardı (TSRS) standartları
"""

import logging
import os
import sqlite3
import sys
from config.database import DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ana dizini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_tsrs_standards() -> None:
    """TSRS standartlarını ve göstergelerini veritabanına yükle"""
    
    logging.info("=" * 70)
    logging.info("TSRS STANDARTLARI VE GÖSTERGELERİ YÜKLEME")
    logging.info("=" * 70)
    
    # Veritabanı yolu
    db_path = DB_PATH
    
    if not os.path.exists(db_path):
        logging.error(f"HATA: Veritabanı bulunamadı: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Önce mevcut TSRS standartlarını temizle (opsiyonel)
        # cursor.execute("DELETE FROM tsrs_indicators")
        # cursor.execute("DELETE FROM tsrs_standards")
        # print("Mevcut TSRS standartları temizlendi")
        
        # TSRS Standartlarını ekle
        tsrs_standards = [
            # ÇEVRESEL STANDARTLAR (TSRS-E)
            {
                'code': 'TSRS-E1',
                'title': 'İklim Değişikliği',
                'description': 'Sera gazı emisyonları, iklim değişikliği riskleri ve fırsatları, azaltım ve adaptasyon stratejileri',
                'category': 'metrics',
                'subcategory': 'Çevresel',
                'requirement_level': 'Zorunlu',
                'reporting_frequency': 'Yıllık',
                'effective_date': '2024-01-01'
            },
            {
                'code': 'TSRS-E2',
                'title': 'Kirlilik',
                'description': 'Hava, su ve toprak kirliliği, atık yönetimi ve kirletici maddelerin kontrolü',
                'category': 'metrics',
                'subcategory': 'Çevresel',
                'requirement_level': 'Zorunlu',
                'reporting_frequency': 'Yıllık',
                'effective_date': '2024-01-01'
            },
            {
                'code': 'TSRS-E3',
                'title': 'Su ve Deniz Kaynakları',
                'description': 'Su tüketimi, su kalitesi, su stres analizi ve deniz ekosistemlerinin korunması',
                'category': 'metrics',
                'subcategory': 'Çevresel',
                'requirement_level': 'Zorunlu',
                'reporting_frequency': 'Yıllık',
                'effective_date': '2024-01-01'
            },
            {
                'code': 'TSRS-E4',
                'title': 'Biyoçeşitlilik ve Ekosistemler',
                'description': 'Biyoçeşitlilik etkileri, habitat koruması ve ekosistem hizmetlerinin sürdürülebilirliği',
                'category': 'metrics',
                'subcategory': 'Çevresel',
                'requirement_level': 'Zorunlu',
                'reporting_frequency': 'Yıllık',
                'effective_date': '2024-01-01'
            },
            {
                'code': 'TSRS-E5',
                'title': 'Kaynak Kullanımı ve Döngüsel Ekonomi',
                'description': 'Malzeme kullanımı, geri dönüşüm oranları, döngüsel ekonomi uygulamaları ve kaynak verimliliği',
                'category': 'metrics',
                'subcategory': 'Çevresel',
                'requirement_level': 'Zorunlu',
                'reporting_frequency': 'Yıllık',
                'effective_date': '2024-01-01'
            },
            
            # SOSYAL STANDARTLAR (TSRS-S)
            {
                'code': 'TSRS-S1',
                'title': 'Kendi İşgücü',
                'description': 'Çalışan hakları, iş sağlığı ve güvenliği, eğitim ve gelişim, çeşitlilik ve fırsat eşitliği',
                'category': 'metrics',
                'subcategory': 'Sosyal',
                'requirement_level': 'Zorunlu',
                'reporting_frequency': 'Yıllık',
                'effective_date': '2024-01-01'
            },
            {
                'code': 'TSRS-S2',
                'title': 'Değer Zincirindeki İşçiler',
                'description': 'Tedarikçi iş gücü hakları, çalışma koşulları ve sürdürülebilir tedarik zinciri yönetimi',
                'category': 'metrics',
                'subcategory': 'Sosyal',
                'requirement_level': 'Zorunlu',
                'reporting_frequency': 'Yıllık',
                'effective_date': '2024-01-01'
            },
            {
                'code': 'TSRS-S3',
                'title': 'Etkilenen Topluluklar',
                'description': 'Yerel topluluk etkileri, paydaş katılımı ve sosyal yatırımlar',
                'category': 'metrics',
                'subcategory': 'Sosyal',
                'requirement_level': 'Zorunlu',
                'reporting_frequency': 'Yıllık',
                'effective_date': '2024-01-01'
            },
            {
                'code': 'TSRS-S4',
                'title': 'Tüketiciler ve Son Kullanıcılar',
                'description': 'Ürün güvenliği, veri gizliliği, müşteri memnuniyeti ve sorumlu pazarlama',
                'category': 'metrics',
                'subcategory': 'Sosyal',
                'requirement_level': 'Zorunlu',
                'reporting_frequency': 'Yıllık',
                'effective_date': '2024-01-01'
            },
            
            # YÖNETİŞİM STANDARTLARI (TSRS-G)
            {
                'code': 'TSRS-G1',
                'title': 'İş Davranışı',
                'description': 'Kurumsal yönetişim, etik, rüşvetle mücadele, uyum ve şeffaflık',
                'category': 'governance',
                'subcategory': 'Yönetişim',
                'requirement_level': 'Zorunlu',
                'reporting_frequency': 'Yıllık',
                'effective_date': '2024-01-01'
            },
            
            # GENEL AÇIKLAMALAR
            {
                'code': 'TSRS-2',
                'title': 'Genel Açıklamalar',
                'description': 'Raporlama kapsamı, metodoloji, paydaş katılımı ve materiality analizi',
                'category': 'governance',
                'subcategory': 'Genel',
                'requirement_level': 'Zorunlu',
                'reporting_frequency': 'Yıllık',
                'effective_date': '2024-01-01'
            }
        ]
        
        logging.info(f"\n{len(tsrs_standards)} adet TSRS standardı ekleniyor...")
        
        for std in tsrs_standards:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO tsrs_standards 
                    (code, title, description, category, subcategory, 
                     requirement_level, reporting_frequency, effective_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    std['code'], std['title'], std['description'], 
                    std['category'], std['subcategory'],
                    std['requirement_level'], std['reporting_frequency'], 
                    std['effective_date']
                ))
                logging.info(f"  [OK] {std['code']} - {std['title']}")
            except Exception as e:
                logging.error(f"  [HATA] {std['code']} eklenirken hata: {e}")
        
        # Standartların ID'lerini al
        cursor.execute("SELECT id, code FROM tsrs_standards")
        standard_ids = {code: id for id, code in cursor.fetchall()}
        
        # TSRS Göstergelerini ekle
        logging.info("\nTSRS Göstergeleri ekleniyor...")
        
        tsrs_indicators = []
        
        # TSRS-E1 Göstergeleri (İklim Değişikliği)
        if 'TSRS-E1' in standard_ids:
            tsrs_indicators.extend([
                {
                    'standard_id': standard_ids['TSRS-E1'],
                    'code': 'TSRS-E1-1',
                    'title': 'Sera Gazı Emisyonları (Scope 1)',
                    'description': 'Şirketin doğrudan kontrol ettiği kaynaklardan kaynaklanan toplam sera gazı emisyonları',
                    'unit': 'tCO2e',
                    'methodology': 'GHG Protocol Corporate Standard',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-E1'],
                    'code': 'TSRS-E1-2',
                    'title': 'Sera Gazı Emisyonları (Scope 2)',
                    'description': 'Satın alınan elektrik, ısı veya buhardan kaynaklanan dolaylı sera gazı emisyonları',
                    'unit': 'tCO2e',
                    'methodology': 'GHG Protocol Corporate Standard',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-E1'],
                    'code': 'TSRS-E1-3',
                    'title': 'Sera Gazı Emisyonları (Scope 3)',
                    'description': 'Değer zincirindeki diğer dolaylı sera gazı emisyonları',
                    'unit': 'tCO2e',
                    'methodology': 'GHG Protocol Corporate Value Chain Standard',
                    'data_type': 'numeric',
                    'is_mandatory': 0,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-E1'],
                    'code': 'TSRS-E1-4',
                    'title': 'İklim Değişikliği Risk Değerlendirmesi',
                    'description': 'İklim değişikliğine bağlı fiziksel ve geçiş risklerinin değerlendirilmesi',
                    'unit': None,
                    'methodology': 'TCFD Framework',
                    'data_type': 'text',
                    'is_mandatory': 1,
                    'is_quantitative': 0
                },
                {
                    'standard_id': standard_ids['TSRS-E1'],
                    'code': 'TSRS-E1-5',
                    'title': 'Emisyon Azaltım Hedefleri',
                    'description': 'Sera gazı emisyonlarını azaltmak için belirlenen hedefler ve ilerleme durumu',
                    'unit': '%',
                    'methodology': 'Science Based Targets Initiative (SBTi)',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                }
            ])
        
        # TSRS-E2 Göstergeleri (Kirlilik)
        if 'TSRS-E2' in standard_ids:
            tsrs_indicators.extend([
                {
                    'standard_id': standard_ids['TSRS-E2'],
                    'code': 'TSRS-E2-1',
                    'title': 'Hava Kirletici Emisyonları',
                    'description': 'NOx, SOx, partikül madde ve diğer hava kirleticileri emisyonları',
                    'unit': 'ton',
                    'methodology': 'Ulusal Emisyon Envanteri',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-E2'],
                    'code': 'TSRS-E2-2',
                    'title': 'Su Kirliliği',
                    'description': 'Atık suyun kalitesi ve arıtma süreçleri',
                    'unit': 'm³',
                    'methodology': 'Su Kirliliği Kontrol Yönetmeliği',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-E2'],
                    'code': 'TSRS-E2-3',
                    'title': 'Tehlikeli Atık Yönetimi',
                    'description': 'Üretilen, depolanan ve bertaraf edilen tehlikeli atık miktarları',
                    'unit': 'ton',
                    'methodology': 'Atık Yönetimi Yönetmeliği',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                }
            ])
        
        # TSRS-E3 Göstergeleri (Su ve Deniz Kaynakları)
        if 'TSRS-E3' in standard_ids:
            tsrs_indicators.extend([
                {
                    'standard_id': standard_ids['TSRS-E3'],
                    'code': 'TSRS-E3-1',
                    'title': 'Toplam Su Tüketimi',
                    'description': 'Tüm kaynaklardan çekilen toplam su miktarı',
                    'unit': 'm³',
                    'methodology': 'GRI 303: Water and Effluents',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-E3'],
                    'code': 'TSRS-E3-2',
                    'title': 'Su Stresi Analizi',
                    'description': 'Su stresinin yüksek olduğu bölgelerdeki su çekimi',
                    'unit': 'm³',
                    'methodology': 'WRI Aqueduct Tool',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-E3'],
                    'code': 'TSRS-E3-3',
                    'title': 'Su Geri Dönüşüm ve Yeniden Kullanım Oranı',
                    'description': 'Geri dönüştürülen ve yeniden kullanılan su oranı',
                    'unit': '%',
                    'methodology': 'GRI 303: Water and Effluents',
                    'data_type': 'numeric',
                    'is_mandatory': 0,
                    'is_quantitative': 1
                }
            ])
        
        # TSRS-E4 Göstergeleri (Biyoçeşitlilik)
        if 'TSRS-E4' in standard_ids:
            tsrs_indicators.extend([
                {
                    'standard_id': standard_ids['TSRS-E4'],
                    'code': 'TSRS-E4-1',
                    'title': 'Biyoçeşitlilik Etki Değerlendirmesi',
                    'description': 'Korunan alanlara veya yüksek biyoçeşitlilik değerine sahip alanlara olan etkiler',
                    'unit': None,
                    'methodology': 'GRI 304: Biodiversity',
                    'data_type': 'text',
                    'is_mandatory': 1,
                    'is_quantitative': 0
                },
                {
                    'standard_id': standard_ids['TSRS-E4'],
                    'code': 'TSRS-E4-2',
                    'title': 'Arazi Kullanımı ve Habitat Kaybı',
                    'description': 'Faaliyetler sonucu etkilenen arazi ve habitat alanları',
                    'unit': 'hektar',
                    'methodology': 'GRI 304: Biodiversity',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                }
            ])
        
        # TSRS-E5 Göstergeleri (Kaynak Kullanımı)
        if 'TSRS-E5' in standard_ids:
            tsrs_indicators.extend([
                {
                    'standard_id': standard_ids['TSRS-E5'],
                    'code': 'TSRS-E5-1',
                    'title': 'Toplam Malzeme Kullanımı',
                    'description': 'Yenilenebilir ve yenilenemeyen malzeme kullanımı',
                    'unit': 'ton',
                    'methodology': 'GRI 301: Materials',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-E5'],
                    'code': 'TSRS-E5-2',
                    'title': 'Geri Dönüştürülmüş Malzeme Oranı',
                    'description': 'Ürün ve ambalajlarda kullanılan geri dönüştürülmüş malzeme oranı',
                    'unit': '%',
                    'methodology': 'GRI 301: Materials',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-E5'],
                    'code': 'TSRS-E5-3',
                    'title': 'Atık Üretimi ve Bertaraf Yöntemleri',
                    'description': 'Üretilen atık miktarları ve bertaraf yöntemlerine göre dağılım',
                    'unit': 'ton',
                    'methodology': 'GRI 306: Waste',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                }
            ])
        
        # TSRS-S1 Göstergeleri (Kendi İşgücü)
        if 'TSRS-S1' in standard_ids:
            tsrs_indicators.extend([
                {
                    'standard_id': standard_ids['TSRS-S1'],
                    'code': 'TSRS-S1-1',
                    'title': 'Toplam Çalışan Sayısı',
                    'description': 'İstihdam türüne, sözleşme türüne ve bölgeye göre toplam çalışan sayısı',
                    'unit': 'kişi',
                    'methodology': 'GRI 2-7: Employees',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-S1'],
                    'code': 'TSRS-S1-2',
                    'title': 'Çeşitlilik ve Fırsat Eşitliği',
                    'description': 'Cinsiyet, yaş, engellilik durumu ve diğer çeşitlilik göstergeleri',
                    'unit': '%',
                    'methodology': 'GRI 405: Diversity and Equal Opportunity',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-S1'],
                    'code': 'TSRS-S1-3',
                    'title': 'İş Sağlığı ve Güvenliği',
                    'description': 'İş kazaları, meslek hastalıkları, kayıp gün oranları',
                    'unit': 'oran',
                    'methodology': 'GRI 403: Occupational Health and Safety',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-S1'],
                    'code': 'TSRS-S1-4',
                    'title': 'Eğitim ve Gelişim',
                    'description': 'Çalışan başına ortalama eğitim saati',
                    'unit': 'saat/kişi',
                    'methodology': 'GRI 404: Training and Education',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-S1'],
                    'code': 'TSRS-S1-5',
                    'title': 'Ücret Eşitliği',
                    'description': 'Kadın ve erkek çalışanlar arasında temel maaş ve ücret oranı',
                    'unit': 'oran',
                    'methodology': 'GRI 405-2: Ratio of basic salary and remuneration',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                }
            ])
        
        # TSRS-S2 Göstergeleri (Değer Zincirindeki İşçiler)
        if 'TSRS-S2' in standard_ids:
            tsrs_indicators.extend([
                {
                    'standard_id': standard_ids['TSRS-S2'],
                    'code': 'TSRS-S2-1',
                    'title': 'Tedarikçi İş Gücü Değerlendirmesi',
                    'description': 'Sosyal kriterler açısından değerlendirilen tedarikçi sayısı ve oranı',
                    'unit': '%',
                    'methodology': 'GRI 414: Supplier Social Assessment',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-S2'],
                    'code': 'TSRS-S2-2',
                    'title': 'Tedarik Zincirinde İnsan Hakları',
                    'description': 'İnsan hakları riskleri tespit edilen ve iyileştirme yapılan tedarikçiler',
                    'unit': 'adet',
                    'methodology': 'GRI 414: Supplier Social Assessment',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                }
            ])
        
        # TSRS-S3 Göstergeleri (Etkilenen Topluluklar)
        if 'TSRS-S3' in standard_ids:
            tsrs_indicators.extend([
                {
                    'standard_id': standard_ids['TSRS-S3'],
                    'code': 'TSRS-S3-1',
                    'title': 'Yerel Topluluk Etkisi',
                    'description': 'Faaliyetlerin yerel topluluklara olan etkileri ve risk değerlendirmesi',
                    'unit': None,
                    'methodology': 'GRI 413: Local Communities',
                    'data_type': 'text',
                    'is_mandatory': 1,
                    'is_quantitative': 0
                },
                {
                    'standard_id': standard_ids['TSRS-S3'],
                    'code': 'TSRS-S3-2',
                    'title': 'Sosyal Yatırımlar',
                    'description': 'Toplumsal kalkınma programlarına yapılan yatırımlar',
                    'unit': 'TRY',
                    'methodology': 'GRI 413: Local Communities',
                    'data_type': 'numeric',
                    'is_mandatory': 0,
                    'is_quantitative': 1
                }
            ])
        
        # TSRS-S4 Göstergeleri (Tüketiciler ve Son Kullanıcılar)
        if 'TSRS-S4' in standard_ids:
            tsrs_indicators.extend([
                {
                    'standard_id': standard_ids['TSRS-S4'],
                    'code': 'TSRS-S4-1',
                    'title': 'Ürün ve Hizmet Güvenliği',
                    'description': 'Güvenlik ve sağlık etkileri açısından değerlendirilen ürün ve hizmet kategorileri',
                    'unit': '%',
                    'methodology': 'GRI 416: Customer Health and Safety',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-S4'],
                    'code': 'TSRS-S4-2',
                    'title': 'Veri Gizliliği',
                    'description': 'Müşteri gizliliğinin ihlali ve müşteri verilerinin kaybolmasına ilişkin şikayetler',
                    'unit': 'adet',
                    'methodology': 'GRI 418: Customer Privacy',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                }
            ])
        
        # TSRS-G1 Göstergeleri (İş Davranışı)
        if 'TSRS-G1' in standard_ids:
            tsrs_indicators.extend([
                {
                    'standard_id': standard_ids['TSRS-G1'],
                    'code': 'TSRS-G1-1',
                    'title': 'Yönetişim Yapısı',
                    'description': 'Yönetim kurulu kompozisyonu, bağımsızlık ve sürdürülebilirlik komiteleri',
                    'unit': None,
                    'methodology': 'GRI 2-9 to 2-21: Governance',
                    'data_type': 'text',
                    'is_mandatory': 1,
                    'is_quantitative': 0
                },
                {
                    'standard_id': standard_ids['TSRS-G1'],
                    'code': 'TSRS-G1-2',
                    'title': 'Etik ve Uyum',
                    'description': 'Etik ihlalleri, rüşvet ve yolsuzluk vakaları',
                    'unit': 'adet',
                    'methodology': 'GRI 205: Anti-corruption',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-G1'],
                    'code': 'TSRS-G1-3',
                    'title': 'Rekabete Aykırı Davranış',
                    'description': 'Rekabete aykırı davranış, tröst ve tekelcilik uygulamalarına ilişkin yasal işlemler',
                    'unit': 'adet',
                    'methodology': 'GRI 206: Anti-competitive Behavior',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                },
                {
                    'standard_id': standard_ids['TSRS-G1'],
                    'code': 'TSRS-G1-4',
                    'title': 'Whistleblowing Mekanizması',
                    'description': 'İhbar mekanizması ve bildirilen vakaların yönetimi',
                    'unit': 'adet',
                    'methodology': 'GRI 2-26: Mechanisms for seeking advice',
                    'data_type': 'numeric',
                    'is_mandatory': 1,
                    'is_quantitative': 1
                }
            ])
        
        # TSRS-2 Göstergeleri (Genel Açıklamalar)
        if 'TSRS-2' in standard_ids:
            tsrs_indicators.extend([
                {
                    'standard_id': standard_ids['TSRS-2'],
                    'code': 'TSRS-2-1',
                    'title': 'Raporlama Kapsamı ve Sınırları',
                    'description': 'Raporlama dönemi, kapsam, sınırlar ve konsolidasyon yaklaşımı',
                    'unit': None,
                    'methodology': 'GRI 2: General Disclosures',
                    'data_type': 'text',
                    'is_mandatory': 1,
                    'is_quantitative': 0
                },
                {
                    'standard_id': standard_ids['TSRS-2'],
                    'code': 'TSRS-2-2',
                    'title': 'Materiality (Önemlilik) Analizi',
                    'description': 'Materyal konuların belirlenmesi ve önceliklendirme süreci',
                    'unit': None,
                    'methodology': 'GRI 3: Material Topics',
                    'data_type': 'text',
                    'is_mandatory': 1,
                    'is_quantitative': 0
                },
                {
                    'standard_id': standard_ids['TSRS-2'],
                    'code': 'TSRS-2-3',
                    'title': 'Paydaş Katılımı',
                    'description': 'Paydaş grupları, katılım yöntemleri ve sıklığı',
                    'unit': None,
                    'methodology': 'GRI 2-29: Approach to stakeholder engagement',
                    'data_type': 'text',
                    'is_mandatory': 1,
                    'is_quantitative': 0
                }
            ])
        
        # Göstergeleri ekle
        logging.info(f"{len(tsrs_indicators)} adet TSRS göstergesi ekleniyor...")
        
        for ind in tsrs_indicators:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO tsrs_indicators 
                    (standard_id, code, title, description, unit, methodology, 
                     data_type, is_mandatory, is_quantitative)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ind['standard_id'], ind['code'], ind['title'], 
                    ind['description'], ind['unit'], ind['methodology'],
                    ind['data_type'], ind['is_mandatory'], ind['is_quantitative']
                ))
                logging.info(f"  [OK] {ind['code']} - {ind['title']}")
            except Exception as e:
                logging.error(f"  [HATA] {ind['code']} eklenirken hata: {e}")
        
        conn.commit()
        
        # İstatistikleri göster
        cursor.execute("SELECT COUNT(*) FROM tsrs_standards")
        total_standards = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tsrs_indicators")
        total_indicators = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tsrs_indicators WHERE is_mandatory = 1")
        mandatory_indicators = cursor.fetchone()[0]
        
        logging.info("\n" + "=" * 70)
        logging.info("TSRS STANDARTLARI VE GÖSTERGELERİ BAŞARIYLA YÜKLENDI!")
        logging.info("=" * 70)
        logging.info("\nIstatistikler:")
        logging.info(f"  - Toplam TSRS Standardı: {total_standards}")
        logging.info(f"  - Toplam TSRS Göstergesi: {total_indicators}")
        logging.info(f"  - Zorunlu Göstergeler: {mandatory_indicators}")
        logging.info(f"  - İsteğe Bağlı Göstergeler: {total_indicators - mandatory_indicators}")
        
        return True
        
    except Exception as e:
        logging.error(f"\n[HATA]: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = setup_tsrs_standards()
    if success:
        logging.info("\n[BASARILI] Islem tamamlandi!")
    else:
        logging.info("\n[BASARISIZ] Islem basarisiz!")
    
    input("\nDevam etmek icin Enter'a basin...")

