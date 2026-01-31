import json
import os

MISSING_FILE = "missing_keys.json"
TR_FILE = "locales/tr.json"

def merge():
    if not os.path.exists(MISSING_FILE):
        print("missing_keys.json not found.")
        return

    with open(MISSING_FILE, "r", encoding="utf-8") as f:
        missing = json.load(f)

    with open(TR_FILE, "r", encoding="utf-8") as f:
        current = json.load(f)

    added_count = 0
    
    # Heuristics for empty keys
    heuristics = {
        "module_water_unavailable": "Su modülü şu anda kullanılamıyor.",
        "module_waste_unavailable": "Atık modülü şu anda kullanılamıyor.",
        "module_biodiversity_unavailable": "Biyoçeşitlilik modülü şu anda kullanılamıyor.",
        "module_not_available": "Modül kullanılamıyor.",
        "total_waste": "Toplam Atık",
        "table_amount": "Miktar",
        "role_user": "Kullanıcı",
        "role_admin": "Yönetici",
        "role_manager": "Yönetici",
        "role_analyst": "Analist",
        "role_viewer": "İzleyici",
        "tcfd_list_title": "TCFD Listesi",
        "tnfd_list_title": "TNFD Listesi",
        "tnfd_page_title": "TNFD Yönetimi",
        "tcfd_page_title": "TCFD Yönetimi",
        "cdp_page_title": "CDP Yönetimi",
        "tcfd_year": "Yıl",
        "tnfd_year": "Yıl",
        "tcfd_category": "Kategori",
        "tcfd_disclosure": "Açıklama",
        "tcfd_impact": "Etki",
        "tnfd_nature_risks": "Doğa Riskleri",
        "tnfd_nature_opps": "Doğa Fırsatları",
        "tnfd_dependencies": "Bağımlılıklar",
        "tnfd_data_entry": "TNFD Veri Girişi",
        "tnfd_col_year": "Yıl",
        "tnfd_col_pillar": "Sütun",
        "tnfd_col_disclosure": "Açıklama",
        "tnfd_col_impact": "Etki",
        "draft": "Taslak",
        "no_data": "Veri Yok",
        "no_data_available": "Mevcut veri yok",
        "select_all": "Tümünü Seç",
        "back_to_list": "Listeye Dön",
        "manage_data": "Veri Yönetimi",
        "add_first_record": "İlk Kaydı Ekle",
        "help_q1": "Nasıl yardımcı olabilirim?",
        "tax_framework_mappings_desc": "Taksonomi Çerçeve Eşleştirmeleri",
        "tcfd_data_entry_desc": "TCFD Veri Girişi Açıklaması",
        "issb_data_entry_desc": "ISSB Veri Girişi Açıklaması",
        "automated_reporting_desc": "Otomatik Raporlama Modülü",
        "automation_desc": "Otomasyon Modülü",
        "analytics_desc": "Analitik Modülü",
        "strategic_desc": "Stratejik Modülü",
        "user_experience_desc": "Kullanıcı Deneyimi Modülü",
        "document_processing_desc": "Doküman İşleme Modülü",
        "digital_security_desc": "Dijital Güvenlik Modülü",
        "erp_integration_desc": "ERP Entegrasyon Modülü",
        "tracking_desc": "İzleme Modülü",
        "auto_tasks_desc": "Otomatik Görevler Modülü",
        "reporting_desc": "Raporlama Modülü",
        "ungc_desc": "UNGC Modülü",
        "waste_management_desc": "Atık Yönetimi Modülü",
        "water_management_desc": "Su Yönetimi Modülü",
        "workflow_desc": "İş Akışı Modülü",
        "validation_desc": "Doğrulama Modülü",
        "visualization_desc": "Görselleştirme Modülü",
        "advanced_calculation_desc": "Gelişmiş Hesaplama Modülü",
        "csrd_materiality_desc": "CSRD Önemlilik Analizi",
        "csrd_esrs_env_desc": "Çevresel Standartlar",
        "csrd_esrs_social": "Sosyal Standartlar",
        "csrd_esrs_gov": "Yönetişim Standartları",
        "csrd_esrs_gov_desc": "Yönetişim Standartları Açıklaması",
        "tcfd_financial_impact": "Finansal Etki",
        "tax_obj_climate_mitigation": "İklim Değişikliği Azaltımı",
        "area_size": "Alan Boyutu",
        "product": "Ürün",
        "value": "Değer",
        "description": "Açıklama",
        "unit": "Birim",
        "active": "Aktif",
        "waste": "Atık",
        "water": "Su",
        "wind": "Rüzgar",
        "lpg": "LPG",
        "diesel": "Dizel",
        "low": "Düşük",
        "email": "E-posta",
        "severity": "Ciddiyet",
        "admin_menu_security": "Güvenlik Ayarları",
        "admin_panel": "Yönetici Paneli",
        "surveys_title": "Anketler",
        "companies_title": "Şirketler",
        "standards_title": "Standartlar",
        "integration_title": "Entegrasyon",
        "innovation_title": "İnovasyon",
        "docs_title": "Dokümanlar",
        "tsrs_title": "TSRS",
        "security_title": "Güvenlik",
        "framework_mapping_title": "Çerçeve Eşleştirme",
        "analysis_title": "Analiz",
        "policy_library_title": "Politika Kütüphanesi",
        "data_collection_title": "Veri Toplama",
        "data_import_title": "Veri İçe Aktarma",
        "stakeholder_title": "Paydaşlar",
        "prioritization_title": "Önceliklendirme",
        "audit_logs_title": "Denetim Kayıtları",
        "sdg.data_entry": "SDG Veri Girişi",
        "cdp_data_entry": "CDP Veri Girişi",
        "tcfd_data_entry": "TCFD Veri Girişi",
        "add_biodiversity_data": "Biyoçeşitlilik Verisi Ekle",
        "issb_total_disclosures": "Toplam ISSB Açıklamaları",
        "issb_completion_rate": "Tamamlanma Oranı",
        "issb_col_metric": "Metrik",
        "issb_year": "Yıl",
        "tcfd_disclosure": "Açıklama",
        "confirm_delete_survey": "Anketi silmek istediğinize emin misiniz?",
        "tax_opex": "OpEx",
        "tax_turnover": "Ciro",
        "lca_implementation": "LCA Uygulaması",
        "social_incident_type": "Olay Tipi",
        "social_lost_days": "Kayıp Günler",
        "sc_country": "Ülke",
        "sc_suppliers": "Tedarikçiler",
        "sc_risk": "Risk",
        "sc_supplier_type": "Tedarikçi Tipi",
        "eco_community_investments": "Toplumsal Yatırımlar",
        "eco_gov_payments": "Devlete Ödemeler",
        "eco_corporate_tax": "Kurumlar Vergisi",
        "rd_investment_ratio": "Ar-Ge Yatırım Oranı",
        "label_tsrs_metric": "TSRS Metriği",
        "common.save": "Kaydet"
    }

    for key, val in missing.items():
        # Skip garbage keys
        if " " in key and not val: # Key has space and no default? Likely garbage parsing
             # But some keys might be sentences.
             pass
        if ")" in key or "(" in key or "'" in key or '"' in key:
            # Likely parsing error
            if "user_edit_title" in key:
                if "user_edit_title" not in current:
                    current["user_edit_title"] = "Kullanıcı Düzenle"
                    added_count += 1
                if "user_new_title" not in current:
                    current["user_new_title"] = "Yeni Kullanıcı"
                    added_count += 1
            continue
            
        if key not in current:
            if val:
                current[key] = val
            elif key in heuristics:
                current[key] = heuristics[key]
            else:
                # Fallback: title case the key
                fallback = key.replace("_", " ").title()
                current[key] = fallback
            added_count += 1

    with open(TR_FILE, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=4, ensure_ascii=False, sort_keys=True)

    print(f"Merged {added_count} new keys into {TR_FILE}")

if __name__ == "__main__":
    merge()
