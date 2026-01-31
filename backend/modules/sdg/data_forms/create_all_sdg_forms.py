#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tüm SDG Formlarını Toplu Oluştur
Bu script kalan 15 SDG formu için dosyalar ve veritabanı tablolarını oluşturur.
"""

import logging
import sqlite3
from config.database import DB_PATH

# Tüm SDG form tanımları
SDG_FORMS = {
    2: {
        'name': 'Açlığa Son',
        'table': 'sdg2_hunger_data',
        'fields': [
            ('food_security_programs', 'Gıda Güvenliği Programları', 'textarea'),
            ('agricultural_support', 'Tarımsal Destek Programları', 'textarea'),
            ('nutrition_programs', 'Beslenme Programları', 'number', 'kişi'),
            ('local_food_procurement', 'Yerel Gıda Tedarik Oranı', 'number', '%'),
        ]
    },
    3: {
        'name': 'Sağlık ve Kaliteli Yaşam',
        'table': 'sdg3_health_data',
        'fields': [
            ('health_insurance_coverage', 'Sağlık Sigortası Kapsama Oranı', 'number', '%'),
            ('occupational_health_programs', 'Mesleki Sağlık Programları', 'textarea'),
            ('mental_health_support', 'Psikolojik Destek Hizmetleri', 'textarea'),
            ('health_safety_training_hours', 'Sağlık ve Güvenlik Eğitim Saati', 'number', 'saat'),
            ('workplace_accidents', 'İş Kazası Sayısı', 'number', 'adet'),
        ]
    },
    4: {
        'name': 'Nitelikli Eğitim',
        'table': 'sdg4_education_data',
        'fields': [
            ('training_hours_total', 'Toplam Eğitim Saati', 'number', 'saat'),
            ('training_hours_per_employee', 'Çalışan Başına Eğitim Saati', 'number', 'saat'),
            ('training_investment', 'Eğitim Yatırımı', 'number', 'TL'),
            ('scholarship_programs', 'Burs Programları', 'textarea'),
            ('intern_count', 'Stajyer Sayısı', 'number', 'kişi'),
        ]
    },
    5: {
        'name': 'Toplumsal Cinsiyet Eşitliği',
        'table': 'sdg5_gender_data',
        'fields': [
            ('female_employee_ratio', 'Kadın Çalışan Oranı', 'number', '%'),
            ('female_management_ratio', 'Yönetimde Kadın Oranı', 'number', '%'),
            ('gender_pay_gap', 'Cinsiyet Ücret Farkı', 'number', '%'),
            ('parental_leave_days', 'Ebeveyn İzni Günleri', 'number', 'gün'),
            ('gender_equality_programs', 'Cinsiyet Eşitliği Programları', 'textarea'),
        ]
    },
    6: {
        'name': 'Temiz Su ve Sanitasyon',
        'table': 'sdg6_water_data',
        'fields': [
            ('water_consumption_total', 'Toplam Su Tüketimi', 'number', 'm³'),
            ('water_recycled', 'Geri Dönüştürülen Su', 'number', 'm³'),
            ('water_recycling_rate', 'Su Geri Dönüşüm Oranı', 'number', '%'),
            ('wastewater_treatment', 'Atık Su Arıtma', 'textarea'),
            ('water_saving_projects', 'Su Tasarrufu Projeleri', 'textarea'),
        ]
    },
    8: {
        'name': 'İnsana Yakışır İş ve Ekonomik Büyüme',
        'table': 'sdg8_employment_data',
        'fields': [
            ('total_employees', 'Toplam Çalışan Sayısı', 'number', 'kişi'),
            ('new_hires', 'Yeni İşe Alınan', 'number', 'kişi'),
            ('turnover_rate', 'Devir Hızı', 'number', '%'),
            ('permanent_employees', 'Sürekli Çalışan Sayısı', 'number', 'kişi'),
            ('temporary_employees', 'Geçici Çalışan Sayısı', 'number', 'kişi'),
            ('parttime_employees', 'Yarı Zamanlı Çalışan', 'number', 'kişi'),
            ('average_wage', 'Ortalama Ücret', 'number', 'TL'),
            ('economic_value_generated', 'Yaratılan Ekonomik Değer', 'number', 'TL'),
        ]
    },
    9: {
        'name': 'Sanayi, Yenilikçilik ve Altyapı',
        'table': 'sdg9_innovation_data',
        'fields': [
            ('rd_investment', 'Ar-Ge Yatırımı', 'number', 'TL'),
            ('rd_investment_ratio', 'Ar-Ge/Ciro Oranı', 'number', '%'),
            ('patent_count', 'Patent Sayısı', 'number', 'adet'),
            ('innovation_projects', 'İnovasyon Proje Sayısı', 'number', 'adet'),
            ('digital_transformation_projects', 'Dijital Dönüşüm Projeleri', 'textarea'),
        ]
    },
    10: {
        'name': 'Eşitsizliklerin Azaltılması',
        'table': 'sdg10_inequality_data',
        'fields': [
            ('wage_gap_ratio', 'Ücret Uçurumu Oranı', 'number', '%'),
            ('disabled_employee_count', 'Engelli Çalışan Sayısı', 'number', 'kişi'),
            ('diversity_programs', 'Çeşitlilik Programları', 'textarea'),
            ('equal_opportunity_policies', 'Fırsat Eşitliği Politikaları', 'textarea'),
        ]
    },
    11: {
        'name': 'Sürdürülebilir Şehirler ve Topluluklar',
        'table': 'sdg11_cities_data',
        'fields': [
            ('green_building_ratio', 'Yeşil Bina Oranı', 'number', '%'),
            ('public_transport_usage', 'Toplu Taşıma Kullanım Oranı', 'number', '%'),
            ('community_development_projects', 'Toplum Geliştirme Projeleri', 'textarea'),
            ('urban_infrastructure_investment', 'Şehir Altyapı Yatırımı', 'number', 'TL'),
        ]
    },
    12: {
        'name': 'Sorumlu Üretim ve Tüketim',
        'table': 'sdg12_consumption_data',
        'fields': [
            ('total_waste', 'Toplam Atık', 'number', 'ton'),
            ('hazardous_waste', 'Tehlikeli Atık', 'number', 'ton'),
            ('recycled_waste', 'Geri Dönüştürülen Atık', 'number', 'ton'),
            ('recycling_rate', 'Geri Dönüşüm Oranı', 'number', '%'),
            ('circular_economy_projects', 'Döngüsel Ekonomi Projeleri', 'textarea'),
            ('waste_reduction_target', 'Atık Azaltma Hedefi', 'number', '%'),
        ]
    },
    13: {
        'name': 'İklim Eylemi',
        'table': 'sdg13_climate_data',
        'fields': [
            ('scope1_emissions', 'Scope 1 Emisyonlar (Doğrudan)', 'number', 'ton CO2e'),
            ('scope2_emissions', 'Scope 2 Emisyonlar (Elektrik)', 'number', 'ton CO2e'),
            ('scope3_emissions', 'Scope 3 Emisyonlar (Dolaylı)', 'number', 'ton CO2e'),
            ('total_emissions', 'Toplam GHG Emisyonları', 'number', 'ton CO2e'),
            ('emission_intensity', 'Emisyon Yoğunluğu', 'number', 'ton CO2e/milyon TL'),
            ('climate_action_plan', 'İklim Eylem Planı', 'textarea'),
            ('carbon_neutrality_target_year', 'Karbon Nötr Hedef Yılı', 'number', 'yıl'),
        ]
    },
    14: {
        'name': 'Sudaki Yaşam',
        'table': 'sdg14_ocean_data',
        'fields': [
            ('marine_protection_projects', 'Deniz Koruma Projeleri', 'textarea'),
            ('ocean_pollution_prevention', 'Okyanus Kirliliği Önleme', 'textarea'),
            ('sustainable_fishery_support', 'Sürdürülebilir Balıkçılık Desteği', 'number', 'TL'),
        ]
    },
    15: {
        'name': 'Karasal Yaşam',
        'table': 'sdg15_biodiversity_data',
        'fields': [
            ('land_conservation_area', 'Koruma Altındaki Alan', 'number', 'hektar'),
            ('reforestation_area', 'Ağaçlandırma Alanı', 'number', 'hektar'),
            ('biodiversity_projects', 'Biyoçeşitlilik Projeleri', 'textarea'),
            ('habitat_protection', 'Habitat Koruma Faaliyetleri', 'textarea'),
        ]
    },
    16: {
        'name': 'Barış, Adalet ve Güçlü Kurumlar',
        'table': 'sdg16_peace_data',
        'fields': [
            ('anticorruption_training', 'Yolsuzlukla Mücadele Eğitimleri', 'number', 'saat'),
            ('ethics_policy', 'Etik Politikaları', 'textarea'),
            ('transparency_score', 'Şeffaflık Skoru', 'number', '/100'),
            ('grievance_mechanism', 'Şikayet Mekanizması', 'textarea'),
            ('corruption_incidents', 'Yolsuzluk Vaka Sayısı', 'number', 'adet'),
        ]
    },
    17: {
        'name': 'Hedefler İçin Ortaklıklar',
        'table': 'sdg17_partnership_data',
        'fields': [
            ('partnerships_count', 'Ortaklık Sayısı', 'number', 'adet'),
            ('ngo_collaborations', 'STK İşbirlikleri', 'textarea'),
            ('public_private_partnerships', 'Kamu-Özel Ortaklıkları', 'textarea'),
            ('knowledge_sharing_platforms', 'Bilgi Paylaşım Platformları', 'textarea'),
            ('sdg_investment', 'SDG Projelerine Yatırım', 'number', 'TL'),
        ]
    },
}

def create_all_tables() -> None:
    """Tüm SDG tablolarını oluştur"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    logging.info("Tüm SDG tabloları oluşturuluyor...\n")

    for sdg_num, config in SDG_FORMS.items():
        table_name = config['table']
        logging.info(f"[{sdg_num}/16] {table_name} oluşturuluyor...")

        # Kolon tanımları oluştur
        columns = [
            'id INTEGER PRIMARY KEY',
            'company_id INTEGER',
            'task_id INTEGER',
            'reporting_year TEXT',
        ]

        for field in config['fields']:
            field_name = field[0]
            if 'TEXT' in field_name or 'programs' in field_name or 'projects' in field_name or 'policy' in field_name or 'plan' in field_name or field_name == 'notes':
                col_type = 'TEXT'
            else:
                col_type = 'REAL'
            columns.append(f"{field_name} {col_type}")

        columns.extend([
            'notes TEXT',
            'is_draft INTEGER DEFAULT 0',
            'created_at TEXT DEFAULT CURRENT_TIMESTAMP',
            'updated_at TEXT DEFAULT CURRENT_TIMESTAMP'
        ])

        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"

        try:
            cursor.execute(create_sql)
            logging.info(f"  [OK] {table_name}")
        except Exception as e:
            logging.error(f"  [HATA] {table_name}: {e}")

    conn.commit()
    conn.close()
    logging.info("\n[BAŞARILI] Tüm tablolar oluşturuldu!")

if __name__ == "__main__":
    create_all_tables()

