#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Şablonları
Hazır import şablonları ve sütun tanımlamaları
"""

import logging
from typing import Dict, List


class ImportTemplateManager:
    """Import şablonlarını yöneten sınıf"""

    def __init__(self):
        """Utility class, başlatılmasına gerek yok"""
        pass

    # GRI Import Şablonu
    GRI_TEMPLATE = {
        'name': 'GRI Göstergeleri',
        'columns': [
            'Gösterge Kodu',
            'Gösterge Adı',
            'Değer',
            'Birim',
            'Yıl',
            'Açıklama',
            'Veri Kaynağı'
        ],
        'column_mapping': {
            'Gösterge Kodu': 'indicator_code',
            'Gösterge Adı': 'indicator_name',
            'Değer': 'value',
            'Birim': 'unit',
            'Yıl': 'year',
            'Açıklama': 'description',
            'Veri Kaynağı': 'data_source'
        },
        'transformation_rules': {
            'indicator_code': {'type': 'str'},
            'value': {'type': 'float'},
            'year': {'type': 'int'}
        },
        'sample_data': [
            ['GRI 2-1', 'Organizasyon Detayları', 'ABC Şirketi', 'metin', 2024, 'Şirket adı', 'Resmi Kayıtlar'],
            ['GRI 302-1', 'Enerji Tüketimi', '125000', 'GJ', 2024, 'Toplam enerji tüketimi', 'Enerji Fatura'],
            ['GRI 305-1', 'Doğrudan Sera Gazı', '5500', 'tCO2e', 2024, 'Scope 1 emisyonlar', 'Karbon Hesaplama']
        ],
        'target_table': 'gri_indicators'
    }

    # TSRS Import Şablonu
    TSRS_TEMPLATE = {
        'name': 'TSRS Göstergeleri',
        'columns': [
            'Standart',
            'Gösterge Kodu',
            'Gösterge Adı',
            'Değer',
            'Birim',
            'Yıl',
            'Açıklama'
        ],
        'column_mapping': {
            'Standart': 'standard',
            'Gösterge Kodu': 'indicator_code',
            'Gösterge Adı': 'indicator_name',
            'Değer': 'value',
            'Birim': 'unit',
            'Yıl': 'year',
            'Açıklama': 'description'
        },
        'transformation_rules': {
            'value': {'type': 'float'},
            'year': {'type': 'int'}
        },
        'sample_data': [
            ['ESRS E1', 'E1-1', 'İklim Değişikliği Stratejisi', 'Mevcut', 'metin', 2024, 'İklim stratejisi açıklaması'],
            ['ESRS E1', 'E1-6', 'Scope 1 Emisyonları', '5500', 'tCO2e', 2024, 'Doğrudan emisyonlar'],
            ['ESRS S1', 'S1-1', 'İş Gücü', '250', 'çalışan', 2024, 'Toplam çalışan sayısı']
        ],
        'target_table': 'tsrs_indicators'
    }

    # Çevresel Veriler Şablonu
    ENVIRONMENTAL_TEMPLATE = {
        'name': 'Çevresel Veriler',
        'columns': [
            'Metrik Tipi',
            'Metrik Adı',
            'Değer',
            'Birim',
            'Tarih',
            'Lokasyon',
            'Açıklama'
        ],
        'column_mapping': {
            'Metrik Tipi': 'metric_type',
            'Metrik Adı': 'metric_name',
            'Değer': 'value',
            'Birim': 'unit',
            'Tarih': 'measurement_date',
            'Lokasyon': 'location',
            'Açıklama': 'description'
        },
        'transformation_rules': {
            'value': {'type': 'float'},
            'measurement_date': {'type': 'date'}
        },
        'sample_data': [
            ['Enerji', 'Elektrik Tüketimi', '50000', 'kWh', '2024-01-01', 'Merkez Fabrika', 'Aylık elektrik tüketimi'],
            ['Su', 'Su Çekimi', '10000', 'm³', '2024-01-01', 'Merkez Fabrika', 'Aylık su tüketimi'],
            ['Atık', 'Tehlikesiz Atık', '15', 'ton', '2024-01-01', 'Merkez Fabrika', 'Aylık atık üretimi']
        ],
        'target_table': 'environmental_metrics'
    }

    # Sosyal Veriler Şablonu
    SOCIAL_TEMPLATE = {
        'name': 'Sosyal Veriler',
        'columns': [
            'Kategori',
            'Metrik Adı',
            'Değer',
            'Birim',
            'Tarih',
            'Departman',
            'Açıklama'
        ],
        'column_mapping': {
            'Kategori': 'category',
            'Metrik Adı': 'metric_name',
            'Değer': 'value',
            'Birim': 'unit',
            'Tarih': 'measurement_date',
            'Departman': 'department',
            'Açıklama': 'description'
        },
        'transformation_rules': {
            'value': {'type': 'float'},
            'measurement_date': {'type': 'date'}
        },
        'sample_data': [
            ['İSG', 'İş Kazası Sayısı', '2', 'adet', '2024-01-01', 'Üretim', 'Aylık kaza sayısı'],
            ['Eğitim', 'Toplam Eğitim Saati', '500', 'saat', '2024-01-01', 'Tüm Departmanlar', 'Aylık eğitim'],
            ['Çeşitlilik', 'Kadın Çalışan Oranı', '45', '%', '2024-01-01', 'Tüm Departmanlar', 'Kadın oranı']
        ],
        'target_table': 'social_metrics'
    }

    # Ekonomik Veriler Şablonu
    ECONOMIC_TEMPLATE = {
        'name': 'Ekonomik Veriler',
        'columns': [
            'Kategori',
            'Metrik Adı',
            'Değer',
            'Para Birimi',
            'Yıl',
            'Açıklama'
        ],
        'column_mapping': {
            'Kategori': 'category',
            'Metrik Adı': 'metric_name',
            'Değer': 'value',
            'Para Birimi': 'currency',
            'Yıl': 'year',
            'Açıklama': 'description'
        },
        'transformation_rules': {
            'value': {'type': 'float'},
            'year': {'type': 'int'}
        },
        'sample_data': [
            ['Gelirler', 'Toplam Gelir', '10000000', 'TL', 2024, 'Yıllık toplam gelir'],
            ['Giderler', 'Çalışan Ücretleri', '3000000', 'TL', 2024, 'Yıllık ücret ödemeleri'],
            ['Yatırımlar', 'Toplum Yatırımları', '500000', 'TL', 2024, 'Sosyal sorumluluk yatırımları']
        ],
        'target_table': 'economic_metrics'
    }

    # Tedarik Zinciri Şablonu
    SUPPLY_CHAIN_TEMPLATE = {
        'name': 'Tedarikçi Değerlendirme',
        'columns': [
            'Tedarikçi Adı',
            'Tedarikçi Kodu',
            'Ülke',
            'Kategori',
            'Yıllık Harcama',
            'Para Birimi',
            'Sertifikalar',
            'Risk Skoru',
            'Değerlendirme Tarihi'
        ],
        'column_mapping': {
            'Tedarikçi Adı': 'supplier_name',
            'Tedarikçi Kodu': 'supplier_code',
            'Ülke': 'country',
            'Kategori': 'category',
            'Yıllık Harcama': 'annual_spending',
            'Para Birimi': 'currency',
            'Sertifikalar': 'certifications',
            'Risk Skoru': 'risk_score',
            'Değerlendirme Tarihi': 'assessment_date'
        },
        'transformation_rules': {
            'annual_spending': {'type': 'float'},
            'risk_score': {'type': 'int'},
            'assessment_date': {'type': 'date'}
        },
        'sample_data': [
            ['Tedarikçi A', 'SUP001', 'Türkiye', 'Hammadde', '500000', 'TL', 'ISO 9001, ISO 14001', 2, '2024-01-15'],
            ['Tedarikçi B', 'SUP002', 'Almanya', 'Ekipman', '1000000', 'EUR', 'ISO 9001', 3, '2024-01-20'],
            ['Tedarikçi C', 'SUP003', 'Türkiye', 'Ambalaj', '200000', 'TL', 'FSC', 1, '2024-01-25']
        ],
        'target_table': 'suppliers'
    }

    OPERATIONAL_COMMON_TEMPLATE = {
        'name': 'Operasyonel Metrikler (Common)',
        'columns': [
            'internal_carbon_price',
            'scope1_emissions',
            'scope2_emissions',
            'scope3_emissions',
            'total_energy_consumption',
            'renewable_energy_pct',
            'current_energy_price',
            'year'
        ],
        'column_mapping': {
            'internal_carbon_price': 'internal_carbon_price',
            'scope1_emissions': 'scope1_emissions',
            'scope2_emissions': 'scope2_emissions',
            'scope3_emissions': 'scope3_emissions',
            'total_energy_consumption': 'total_energy_consumption',
            'renewable_energy_pct': 'renewable_energy_pct',
            'current_energy_price': 'current_energy_price',
            'year': 'year'
        },
        'transformation_rules': {
            'internal_carbon_price': {'type': 'float'},
            'scope1_emissions': {'type': 'float'},
            'scope2_emissions': {'type': 'float'},
            'scope3_emissions': {'type': 'float'},
            'total_energy_consumption': {'type': 'float'},
            'renewable_energy_pct': {'type': 'float'},
            'current_energy_price': {'type': 'float'},
            'year': {'type': 'int'}
        },
        'sample_data': [
            ['75', '10000', '5000', '20000', '25000', '35', '120', 2025]
        ],
        'target_table': 'tcfd_metrics'
    }

    @classmethod
    def get_template(cls, template_name: str) -> Dict:
        """Şablonu al"""
        templates = {
            'gri': cls.GRI_TEMPLATE,
            'tsrs': cls.TSRS_TEMPLATE,
            'energy': cls.ENERGY_TEMPLATE,
            'environmental': cls.ENVIRONMENTAL_TEMPLATE,
            'social': cls.SOCIAL_TEMPLATE,
            'economic': cls.ECONOMIC_TEMPLATE,
            'supply_chain': cls.SUPPLY_CHAIN_TEMPLATE,
            'operational_common': cls.OPERATIONAL_COMMON_TEMPLATE
        }

        return templates.get(template_name.lower(), None)

    @classmethod
    def get_all_templates(cls) -> List[Dict]:
        """Tüm şablonları al"""
        return [
            {'id': 'gri', 'name': 'GRI Göstergeleri', 'description': 'GRI standartları için veri import şablonu'},
            {'id': 'tsrs', 'name': 'TSRS Göstergeleri', 'description': 'TSRS/ESRS standartları için veri import şablonu'},
            {'id': 'energy', 'name': 'Enerji Verileri', 'description': 'Detaylı enerji tüketim kayıtları (Fatura, Tedarikçi vb.)'},
            {'id': 'environmental', 'name': 'Çevresel Veriler', 'description': 'Enerji, su, atık vb. çevresel metrikleri'},
            {'id': 'social', 'name': 'Sosyal Veriler', 'description': 'İSG, eğitim, çeşitlilik metrikleri'},
            {'id': 'economic', 'name': 'Ekonomik Veriler', 'description': 'Ekonomik değer dağılımı metrikleri'},
            {'id': 'supply_chain', 'name': 'Tedarik Zinciri', 'description': 'Tedarikçi değerlendirme verileri'},
            {'id': 'operational_common', 'name': 'Operasyonel Metrikler (Common)', 'description': 'Emisyon ve enerji metrikleri ortak şablon'}
        ]

    @classmethod
    def create_template_file(cls, template_name: str, output_path: str, format: str = 'excel') -> bool:
        """
        Şablon dosyası oluştur
        
        Args:
            template_name: Şablon adı
            output_path: Çıktı dosya yolu
            format: Dosya formatı (excel veya csv)
        
        Returns:
            Başarılı ise True
        """
        try:
            import pandas as pd

            template = cls.get_template(template_name)
            if not template:
                return False

            # DataFrame oluştur
            df = pd.DataFrame(template['sample_data'], columns=template['columns'])

            # Dosyaya kaydet
            if format == 'excel':
                df.to_excel(output_path, index=False)
            else:
                df.to_csv(output_path, index=False, encoding='utf-8-sig')

            return True

        except Exception as e:
            logging.error(f"Şablon dosyası oluşturma hatası: {e}")
            return False

