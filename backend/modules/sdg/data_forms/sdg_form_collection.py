#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tüm SDG Formları - Merkezi Koleksiyon
Her SDG için form field'larını döndürür
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from typing import Dict, List, Union, cast

from modules.data_collection.form_builder import FormField

# Tüm SDG formlarının field tanımları
SDG_FORMS: Dict[int, Dict[str, Union[str, List[FormField]]]] = {
    1: {
        'title': 'SDG 1 - Yoksulluğa Son',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('employees_below_poverty', 'Yoksulluk Sınırının Altında Çalışan', 'number', False, unit='kişi'),
            FormField('living_wage_ratio', 'Yaşanabilir Ücret Oranı', 'number', False, unit='%'),
            FormField('social_support_programs', 'Sosyal Destek Programları', 'textarea', False),
            FormField('community_poverty_projects', 'Toplum Yoksulluk Projeleri', 'textarea', False),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    2: {
        'title': 'SDG 2 - Açlığa Son',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('food_security_programs', 'Gıda Güvenliği Programları', 'textarea', False),
            FormField('agricultural_support', 'Tarımsal Destek', 'textarea', False),
            FormField('nutrition_programs', 'Beslenme Programları', 'number', False, unit='kişi'),
            FormField('local_food_procurement', 'Yerel Gıda Tedarik Oranı', 'number', False, unit='%'),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    3: {
        'title': 'SDG 3 - Sağlık ve Kaliteli Yaşam',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('health_insurance_coverage', 'Sağlık Sigortası Kapsamı', 'number', True, unit='%'),
            FormField('occupational_health_programs', 'Mesleki Sağlık Programları', 'textarea', False),
            FormField('mental_health_support', 'Psikolojik Destek', 'textarea', False),
            FormField('health_safety_training_hours', 'Sağlık Güvenlik Eğitim Saati', 'number', False, unit='saat'),
            FormField('workplace_accidents', 'İş Kazası Sayısı', 'number', True, unit='adet'),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    4: {
        'title': 'SDG 4 - Nitelikli Eğitim',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('training_hours_total', 'Toplam Eğitim Saati', 'number', True, unit='saat'),
            FormField('training_hours_per_employee', 'Çalışan Başına Eğitim', 'number', True, unit='saat'),
            FormField('training_investment', 'Eğitim Yatırımı', 'number', False, unit='TL'),
            FormField('scholarship_programs', 'Burs Programları', 'textarea', False),
            FormField('intern_count', 'Stajyer Sayısı', 'number', False, unit='kişi'),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    5: {
        'title': 'SDG 5 - Toplumsal Cinsiyet Eşitliği',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('female_employee_ratio', 'Kadın Çalışan Oranı', 'number', True, unit='%'),
            FormField('female_management_ratio', 'Yönetimde Kadın Oranı', 'number', True, unit='%'),
            FormField('gender_pay_gap', 'Cinsiyet Ücret Farkı', 'number', False, unit='%'),
            FormField('parental_leave_days', 'Ebeveyn İzni', 'number', False, unit='gün'),
            FormField('gender_equality_programs', 'Cinsiyet Eşitliği Programları', 'textarea', False),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    6: {
        'title': 'SDG 6 - Temiz Su ve Sanitasyon',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('water_consumption_total', 'Toplam Su Tüketimi', 'number', True, unit='m³'),
            FormField('water_recycled', 'Geri Dönüştürülen Su', 'number', False, unit='m³'),
            FormField('water_recycling_rate', 'Su Geri Dönüşüm Oranı', 'number', False, unit='%'),
            FormField('wastewater_treatment', 'Atık Su Arıtma', 'textarea', False),
            FormField('water_saving_projects', 'Su Tasarrufu Projeleri', 'textarea', False),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    8: {
        'title': 'SDG 8 - İnsana Yakışır İş',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('total_employees', 'Toplam Çalışan', 'number', True, unit='kişi'),
            FormField('new_hires', 'Yeni İşe Alınan', 'number', True, unit='kişi'),
            FormField('turnover_rate', 'Devir Hızı', 'number', False, unit='%'),
            FormField('permanent_employees', 'Sürekli Çalışan', 'number', False, unit='kişi'),
            FormField('average_wage', 'Ortalama Ücret', 'number', False, unit='TL'),
            FormField('economic_value_generated', 'Yaratılan Ekonomik Değer', 'number', False, unit='TL'),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    9: {
        'title': 'SDG 9 - Sanayi ve Yenilikçilik',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('rd_investment', 'Ar-Ge Yatırımı', 'number', True, unit='TL'),
            FormField('rd_investment_ratio', 'Ar-Ge/Ciro Oranı', 'number', False, unit='%'),
            FormField('patent_count', 'Patent Sayısı', 'number', False, unit='adet'),
            FormField('innovation_projects', 'İnovasyon Proje Sayısı', 'number', False, unit='adet'),
            FormField('digital_transformation', 'Dijital Dönüşüm Projeleri', 'textarea', False),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    10: {
        'title': 'SDG 10 - Eşitsizliklerin Azaltılması',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('wage_gap_ratio', 'Ücret Uçurumu', 'number', False, unit='%'),
            FormField('disabled_employee_count', 'Engelli Çalışan', 'number', False, unit='kişi'),
            FormField('diversity_programs', 'Çeşitlilik Programları', 'textarea', False),
            FormField('equal_opportunity_policies', 'Fırsat Eşitliği Politikaları', 'textarea', False),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    11: {
        'title': 'SDG 11 - Sürdürülebilir Şehirler',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('green_building_ratio', 'Yeşil Bina Oranı', 'number', False, unit='%'),
            FormField('public_transport_usage', 'Toplu Taşıma Kullanımı', 'number', False, unit='%'),
            FormField('community_development', 'Toplum Geliştirme Projeleri', 'textarea', False),
            FormField('urban_infrastructure_investment', 'Şehir Altyapı Yatırımı', 'number', False, unit='TL'),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    12: {
        'title': 'SDG 12 - Sorumlu Üretim ve Tüketim',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('total_waste', 'Toplam Atık', 'number', True, unit='ton'),
            FormField('hazardous_waste', 'Tehlikeli Atık', 'number', True, unit='ton'),
            FormField('recycled_waste', 'Geri Dönüştürülen Atık', 'number', True, unit='ton'),
            FormField('recycling_rate', 'Geri Dönüşüm Oranı', 'number', False, unit='%'),
            FormField('circular_economy_projects', 'Döngüsel Ekonomi', 'textarea', False),
            FormField('waste_reduction_target', 'Atık Azaltma Hedefi', 'number', False, unit='%'),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    13: {
        'title': 'SDG 13 - İklim Eylemi',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('scope1_emissions', 'Scope 1 Emisyonlar', 'number', True, unit='ton CO2e'),
            FormField('scope2_emissions', 'Scope 2 Emisyonlar', 'number', True, unit='ton CO2e'),
            FormField('scope3_emissions', 'Scope 3 Emisyonlar', 'number', False, unit='ton CO2e'),
            FormField('total_emissions', 'Toplam GHG Emisyonları', 'number', False, unit='ton CO2e'),
            FormField('emission_intensity', 'Emisyon Yoğunluğu', 'number', False, unit='ton CO2e/milyon TL'),
            FormField('climate_action_plan', 'İklim Eylem Planı', 'textarea', False),
            FormField('carbon_neutrality_target', 'Karbon Nötr Hedef Yılı', 'number', False, unit='yıl'),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    14: {
        'title': 'SDG 14 - Sudaki Yaşam',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('marine_protection_projects', 'Deniz Koruma Projeleri', 'textarea', False),
            FormField('ocean_pollution_prevention', 'Okyanus Kirliliği Önleme', 'textarea', False),
            FormField('sustainable_fishery_support', 'Sürdürülebilir Balıkçılık Desteği', 'number', False, unit='TL'),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    15: {
        'title': 'SDG 15 - Karasal Yaşam',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('land_conservation_area', 'Koruma Altındaki Alan', 'number', False, unit='hektar'),
            FormField('reforestation_area', 'Ağaçlandırma Alanı', 'number', False, unit='hektar'),
            FormField('biodiversity_projects', 'Biyoçeşitlilik Projeleri', 'textarea', False),
            FormField('habitat_protection', 'Habitat Koruma Faaliyetleri', 'textarea', False),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    16: {
        'title': 'SDG 16 - Barış, Adalet ve Güçlü Kurumlar',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('anticorruption_training', 'Yolsuzlukla Mücadele Eğitimi', 'number', False, unit='saat'),
            FormField('ethics_policy', 'Etik Politikaları', 'textarea', False),
            FormField('transparency_score', 'Şeffaflık Skoru', 'number', False, unit='/100'),
            FormField('grievance_mechanism', 'Şikayet Mekanizması', 'textarea', False),
            FormField('corruption_incidents', 'Yolsuzluk Vaka Sayısı', 'number', False, unit='adet'),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
    17: {
        'title': 'SDG 17 - Hedefler İçin Ortaklıklar',
        'fields': [
            FormField('reporting_year', 'Raporlama Yılı', 'dropdown', True, '2024', ['2024', '2023', '2022']),
            FormField('partnerships_count', 'Ortaklık Sayısı', 'number', False, unit='adet'),
            FormField('ngo_collaborations', 'STK İşbirlikleri', 'textarea', False),
            FormField('public_private_partnerships', 'Kamu-Özel Ortaklıklar', 'textarea', False),
            FormField('knowledge_sharing', 'Bilgi Paylaşım Platformları', 'textarea', False),
            FormField('sdg_investment', 'SDG Projelerine Yatırım', 'number', False, unit='TL'),
            FormField('notes', 'Ek Notlar', 'textarea', False),
        ]
    },
}

def get_sdg_form_fields(sdg_number: int) -> List[FormField]:
    """
    SDG numarasına göre form field'larını döndür
    
    Args:
        sdg_number: SDG numarası (1-17)
    
    Returns:
        List[FormField]: Form alanları listesi
    
    Example:
        >>> fields = get_sdg_form_fields(7)
        >>> print(len(fields))  # SDG 7 için alan sayısı
    """
    # SDG 7 özel olarak dosyasında tanımlı
    if sdg_number == 7:
        from .sdg7_energy_form import get_sdg7_fields
        return get_sdg7_fields()

    # Diğerleri koleksiyonda
    if sdg_number in SDG_FORMS:
        return cast(List[FormField], SDG_FORMS[sdg_number]['fields'])

    # Tanımlı değilse boş liste
    return []

def get_sdg_form_title(sdg_number: int) -> str:
    """SDG form başlığını döndür"""
    if sdg_number == 7:
        return "SDG 7 - Erişilebilir ve Temiz Enerji"

    if sdg_number in SDG_FORMS:
        return cast(str, SDG_FORMS[sdg_number]['title'])

    return f"SDG {sdg_number} Veri Formu"

