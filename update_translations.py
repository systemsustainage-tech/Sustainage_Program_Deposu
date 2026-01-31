import json
import os

files_to_update = [
    'c:/SUSTAINAGESERVER/locales/tr.json',
    'c:/SUSTAINAGESERVER/backend/config/translations_tr.json'
]

new_translations = {
    "cdp_page_title": "CDP Raporlama",
    "cdp_desc": "Karbon Saydamlık Projesi (CDP) kapsamında iklim, su ve orman verilerinin raporlanması.",
    "cdp_module_climate": "İklim Değişikliği",
    "cdp_module_water": "Su Güvenliği",
    "cdp_module_forests": "Ormansızlaşma",
    "cdp_list_title": "CDP Başvuruları",
    "cdp_col_year": "Yıl",
    "cdp_col_module": "Modül",
    "cdp_col_score": "Skor",
    "cdp_col_status": "Durum",
    
    "issb_title": "ISSB Standartları",
    "issb_desc": "Uluslararası Sürdürülebilirlik Standartları Kurulu (ISSB) IFRS S1 ve S2 uyumluluğu.",
    "issb_data_entry": "Veri Girişi",
    "issb_data_entry_desc": "IFRS S1 (Genel Gereklilikler) ve IFRS S2 (İklim) verilerini girin.",
    "issb_total_disclosures": "Toplam Açıklama",
    "issb_standards_covered": "Kapsanan Standartlar",
    "issb_completion_rate": "Tamamlanma Oranı",
    "issb_list_title": "ISSB Açıklamaları",
    "issb_col_year": "Yıl",
    "issb_col_standard": "Standart",
    "issb_col_disclosure": "Açıklama",
    "issb_col_metric": "Metrik",
    "no_data_found": "Veri bulunamadı",

    "supply_chain_title": "Tedarik Zinciri",
    "supply_chain_add_title": "Tedarikçi Ekle",
    "sc_desc": "Tedarikçi sürdürülebilirlik değerlendirmesi ve risk yönetimi.",
    "sc_total_suppliers": "Toplam Tedarikçi",
    "sc_avg_score": "Ortalama Skor",
    "sc_high_risk": "Yüksek Riskli",
    "sc_suppliers": "Tedarikçiler",
    "sc_supplier_name": "Tedarikçi Adı",
    "sc_supplier_type": "Tip",
    "sc_country": "Ülke",
    "sc_score": "Skor",
    "sc_risk": "Risk Seviyesi",
    "no_data_available": "Veri mevcut değil",

    "esg_title": "ESG Skoru",
    "esg_add_title": "ESG Verisi Ekle",
    "esg_desc": "Çevresel, Sosyal ve Yönetişim (ESG) performans takibi ve skorlama.",
    "esg_env": "Çevresel",
    "esg_social": "Sosyal",
    "esg_gov": "Yönetişim",
    "esg_total": "Toplam Skor",
    "eco_year": "Yıl",
    "eco_quarter": "Çeyrek",
    "recent_data": "Son Veriler",
    "date": "Tarih",

    "cbam_title": "Sınırda Karbon (CBAM)",
    "cbam_add_title": "CBAM Verisi Ekle",
    "cbam_desc": "Sınırda Karbon Düzenleme Mekanizması (SKDM) raporlaması ve yükümlülük takibi.",
    "cbam_total_emissions": "Toplam Emisyon",
    "cbam_total_imports": "Toplam İthalat",
    "cbam_liability_est": "Tahmini Yükümlülük",
    "cbam_sector": "Sektör",
    "cbam_origin_country": "Menşei Ülke",
    
    "iirc_title": "Entegre Raporlama (IIRC)",
    "iirc_desc": "Entegre Raporlama (<IR>) çerçevesinde değer yaratma modeli.",
    "module_active_badge": "Modül Aktif",
    "module_passive_badge": "Modül Pasif",
    
    "tnfd_title": "TNFD Raporlama",
    "tnfd_desc": "Doğa İle İlgili Finansal Beyanlar Görev Gücü (TNFD) çerçevesi.",
    "tnfd_data_entry_desc": "Doğa kaynaklı riskler ve fırsatlar için veri girişi.",
    
    "tcfd_title": "TCFD Raporlama",
    "tcfd_desc": "İklimle İlgili Finansal Beyanlar Görev Gücü (TCFD) çerçevesi.",
    
    "gov_board_member": "Yönetim Kurulu Üyesi",
    "gov_name_surname": "Ad Soyad",
    
    "economic_title": "Ekonomik Değer",
    "economic_desc": "Ekonomik performans ve değer dağılımı.",
    
    "taxonomy_title": "AB Taksonomisi",
    "taxonomy_desc": "AB Taksonomisi uyumluluk ve hizalanma raporlaması.",
    
    "csrd_title": "CSRD Raporlama",
    "csrd_desc": "Kurumsal Sürdürülebilirlik Raporlama Direktifi (CSRD) uyumluluğu.",
    
    "btn_add_data": "Veri Ekle",
    "module_environmental": "Çevresel Modüller",
    "module_carbon": "Karbon Yönetimi",
    "module_energy": "Enerji Yönetimi",
    "module_waste": "Atık Yönetimi",
    "module_water": "Su Yönetimi",
    "module_biodiversity": "Biyoçeşitlilik",
    "module_social_governance": "Sosyal & Yönetişim",
    "module_social_impact": "Sosyal Etki",
    "module_corporate_governance": "Kurumsal Yönetişim",
    "module_supply_chain": "Tedarik Zinciri",
    "module_economic_value": "Ekonomik Değer",
    "module_frameworks": "Çerçeveler & Standartlar",
    "module_esg_score": "ESG Skoru",
    "module_cbam": "Sınırda Karbon (CBAM)",
    "module_csrd": "CSRD Raporlama",
    "module_eu_taxonomy": "AB Taksonomisi",
    "module_gri": "GRI Raporlama",
    "module_sdg": "SDG (Sürdürülebilir Kalkınma Amaçları)",
    "module_advanced_reporting": "İleri Raporlama",
    "module_ifrs": "IFRS / ISSB",
    "module_tcfd": "TCFD",
    "module_tnfd": "TNFD",
    "module_cdp": "CDP",
    "chart_emission_dist": "Emisyon Dağılımı",
    "chart_emission_trend": "Emisyon Trendi",
    "sustainability_modules": "Sürdürülebilirlik Modülleri",
    "dashboard_welcome": "Hoş Geldiniz",
    "dashboard_role": "Rol",
    "system_online": "Sistem Çevrimiçi",
    "users_title": "Kullanıcılar",
    "companies_title": "Şirketler",
    "reports_title": "Raporlar",
    "data_points_title": "Veri Noktaları",
    "quick_access_menu": "Hızlı Erişim Menüsü"
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
