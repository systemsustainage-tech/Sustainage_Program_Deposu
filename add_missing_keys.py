import json
import os

files_to_update = [
    'c:/SUSTAINAGESERVER/locales/tr.json',
    'c:/SUSTAINAGESERVER/backend/config/translations_tr.json'
]

# Map of missing keys to Turkish translations
new_translations = {
    # Common / App
    "app.title": "Sustainage",
    "common.back": "Geri",
    "common.btn_save": "Kaydet",
    "common.save": "Kaydet",
    "save": "Kaydet",
    "common.btn_cancel": "İptal",
    "common.cancel": "İptal",
    "cancel": "İptal",
    "no_data_yet": "Henüz veri girişi yapılmamış.",
    "recent_data_entries": "Son Veri Girişleri",
    "coming_soon": "Çok Yakında",
    "module_ready": "Modül Hazır",
    "btn_start_analysis": "Analizi Başlat",
    "col_detail": "Detay",
    "select_score": "Puan Seçiniz",

    # Tables Generic
    "table_date": "Tarih",
    "table_amount": "Miktar",
    "table_quantity": "Miktar",
    "table_unit": "Birim",
    "table_cost": "Maliyet",
    "table_scope": "Kapsam",
    "table_category": "Kategori",
    "table_source": "Kaynak",
    "table_period": "Dönem",
    "table_emissions": "Emisyon (tCO2e)",
    "table_energy_type": "Enerji Türü",
    "table_waste_type": "Atık Türü",
    "table_consumption": "Tüketim",
    "table_disposal_method": "Bertaraf Yöntemi",
    
    # Environmental Modules (Carbon, Water, Waste, Energy)
    "total_carbon_footprint": "Toplam Karbon Ayak İzi",
    "total_water_consumption": "Toplam Su Tüketimi",
    "total_waste": "Toplam Atık",
    "recent_energy_records": "Son Enerji Kayıtları",

    # SDG
    "sdg.data_entry": "SDG Veri Girişi",
    "sdg_data_entry_title": "SDG İlerleme Girişi",
    "sdg_data_entry_desc": "Sürdürülebilir Kalkınma Amaçları kapsamındaki ilerlemelerinizi kaydedin.",
    "sdg_total_goals": "Toplam Amaç",
    "sdg_avg_progress": "Ortalama İlerleme",
    "sdg_completed_actions": "Tamamlanan Aksiyonlar",
    "sdg_target": "Hedef",
    "sdg_action": "Aksiyon",
    "sdg_col_progress": "İlerleme (%)",
    "sdg_col_status": "Durum",

    # GRI
    "gri_data_entry_title": "GRI Veri Girişi",
    "gri_data_entry_desc": "Küresel Raporlama Girişimi (GRI) standartlarına uygun veri girişi.",
    "gri_covered_standards": "Kapsanan Standartlar",
    "gri_completed_disclosures": "Tamamlanan Açıklamalar",
    "gri_completion_rate": "Tamamlanma Oranı",
    "gri_year": "Yıl",
    "gri_disclosure": "Açıklama (Disclosure)",
    "gri_value": "Değer",
    "gri_last_update": "Son Güncelleme",

    # Social
    "social_type_employee": "Çalışan Verisi",
    "social_type_ohs": "İSG Olayı",
    "social_type_training": "Eğitim Kaydı",
    "gender_male": "Erkek",
    "gender_female": "Kadın",

    # Governance
    "gov_member_count": "Üye Sayısı",
    "gov_is_independent": "Bağımsız Üye?",
    "gov_position": "Pozisyon",
    "gov_committee_name": "Komite Adı",
    "gov_committee_def": "Komite Tanımı",
    "gov_responsibilities": "Sorumluluklar",
    "gov_participants": "Katılımcı Sayısı",
    "gov_total_hours": "Toplam Saat",
    "gov_training_name": "Eğitim Adı",
    "gov_expertise": "Uzmanlık Alanı",
    "gov_ethics_training": "Etik Eğitimi",
    "gov_membership_type": "Üyelik Tipi",
    "gov_type_executive": "İcracı",
    "gov_type_non_executive": "İcracı Olmayan",
    "gov_comm_audit": "Denetim Komitesi",
    "gov_comm_risk": "Risk Komitesi",
    "gov_comm_governance": "Yönetişim Komitesi",
    "gov_comm_nomination": "Aday Gösterme Komitesi",
    "gov_comm_remuneration": "Ücret Komitesi",

    # CSRD
    "csrd_materiality_title": "Çifte Önemlilik Analizi",
    "csrd_materiality_desc": "Etki ve finansal önemlilik değerlendirmesi.",
    "csrd_esrs_general": "Genel Gereklilikler",
    "csrd_esrs_general_desc": "ESRS 1 ve ESRS 2 standartları.",
    "csrd_esrs_env": "Çevresel Standartlar",
    "csrd_esrs_env_desc": "İklim, kirlilik, su, biyoçeşitlilik, döngüsel ekonomi.",
    "csrd_esrs_social": "Sosyal Standartlar",
    "csrd_esrs_social_desc": "Çalışanlar, değer zinciri, toplum, tüketiciler.",
    "csrd_esrs_gov": "Yönetişim Standartları",
    "csrd_esrs_gov_desc": "İş yapış biçimi.",
    "csrd_topic": "Konu",
    "csrd_impact_score": "Etki Skoru",
    "csrd_financial_score": "Finansal Skor",
    "csrd_rationale": "Gerekçe",
    "csrd_matrix": "Önemlilik Matrisi",

    # EU Taxonomy
    "tax_analysis": "Uygunluk Analizi",
    "tax_analysis_desc": "Ekonomik faaliyetlerin AB Taksonomisi kriterlerine göre değerlendirilmesi.",
    "tax_eligible": "Uygun (Eligible)",
    "tax_aligned": "Uyumlu (Aligned)",
    "tax_turnover": "Ciro (Turnover)",
    "tax_capex": "Yatırım (CapEx)",
    "tax_opex": "Gider (OpEx)",
    "tax_activity": "Ekonomik Faaliyet",
    "tax_nace": "NACE Kodu",
    "tax_tech_criteria": "Teknik Tarama Kriterleri",
    "tax_tech_criteria_desc": "Önemli katkı ve zarar vermeme kriterleri.",

    # CBAM
    "cbam_product_code": "CN Kodu",
    "cbam_direct_emissions": "Doğrudan Emisyonlar",
    "cbam_indirect_emissions": "Dolaylı Emisyonlar",

    # Economic
    "eco_category": "Kategori",
    "eco_amount": "Tutar",
    "eco_description": "Açıklama",
    "eco_revenue_desc": "Gelir ve ekonomik değer dağılımı.",

    # TCFD
    "tcfd_data_entry": "TCFD Veri Girişi",
    "tcfd_data_entry_desc": "İklimle ilgili risk ve fırsatların finansal etkileri.",
    "tcfd_total_risks": "Toplam Risk",
    "tcfd_total_opps": "Toplam Fırsat",
    "tcfd_financial_impact": "Finansal Etki",
    "tcfd_year": "Yıl",
    "tcfd_category": "Kategori",
    "tcfd_disclosure": "Açıklama",
    "tcfd_impact": "Etki",
    "tcfd_col_year": "Yıl",
    "tcfd_col_category": "Kategori",
    "tcfd_col_disclosure": "Açıklama",
    "tcfd_col_impact": "Finansal Etki",

    # TNFD
    "tnfd_data_entry": "TNFD Veri Girişi",
    "tnfd_nature_risks": "Doğa Riskleri",
    "tnfd_nature_opps": "Doğa Fırsatları",
    "tnfd_dependencies": "Bağımlılıklar",
    "tnfd_nature_impact": "Doğa Etkisi",
    "tnfd_year": "Yıl",
    "tnfd_pillar": "Sütun (Pillar)",
    "tnfd_disclosure": "Açıklama",
    "tnfd_col_year": "Yıl",
    "tnfd_col_pillar": "Sütun",
    "tnfd_col_disclosure": "Açıklama",
    "tnfd_col_impact": "Etki",

    # CDP
    "cdp_data_entry": "CDP Veri Girişi",
    "cdp_status_submitted": "Gönderildi",
    "cdp_status_inprogress": "Devam Ediyor",
    "cdp_status_notstarted": "Başlanmadı",

    # ISSB
    "issb_standard": "Standart",
    "issb_disclosure": "Açıklama",
    "issb_metric": "Metrik",
    "issb_year": "Yıl",
    
    # IIRC
    "iirc_module_ready_desc": "Entegre raporlama modülü kullanıma hazırdır.",
    "iirc_module_failed_desc": "Modül yüklenirken bir hata oluştu."
}

for file_path in files_to_update:
    if os.path.exists(file_path):
        print(f"Updating {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update with new keys
            data.update(new_translations)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Success.")
        except Exception as e:
            print(f"Error updating {file_path}: {e}")
    else:
        print(f"File not found: {file_path}")
