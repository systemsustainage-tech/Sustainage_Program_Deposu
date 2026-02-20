import json
import os

# Define the new keys
new_keys = {
  "dashboard_welcome": {"tr": "Hoşgeldiniz", "en": "Welcome"},
  "dashboard_role": {"tr": "Rol", "en": "Role"},
  "system_online": {"tr": "Sistem Online", "en": "System Online"},
  "btn_back": {"tr": "Geri", "en": "Back"},
  "active_surveys": {"tr": "Aktif Anketler", "en": "Active Surveys"},
  "total_responses": {"tr": "Toplam Cevap", "en": "Total Responses"},
  "recent_activities": {"tr": "Son Aktiviteler", "en": "Recent Activities"},
  "start_date": {"tr": "Başlangıç", "en": "Start Date"},
  "end_date": {"tr": "Bitiş", "en": "End Date"},
  "module_action": {"tr": "Modül / İşlem", "en": "Module / Action"},
  "search_placeholder": {"tr": "Ara...", "en": "Search..."},
  "pending_actions": {"tr": "Bekleyen İşler", "en": "Pending Actions"},
  "all_caught_up": {"tr": "Harika! Bekleyen işiniz yok.", "en": "Great! No pending actions."},
  "sustainability_modules": {"tr": "Sürdürülebilirlik Modülleri", "en": "Sustainability Modules"},
  "category_environmental": {"tr": "Çevresel", "en": "Environmental"},
  "category_social": {"tr": "Sosyal", "en": "Social"},
  "category_governance": {"tr": "Yönetişim", "en": "Governance"},
  "category_compliance": {"tr": "Uyum & Raporlama", "en": "Compliance & Reporting"},
  "top_material_topics": {"tr": "Öncelikli Konular", "en": "Top Material Topics"},
  "no_material_topics": {"tr": "Öncelikli konu bulunamadı.", "en": "No material topics found."},
  "view_details": {"tr": "Detayları Gör", "en": "View Details"},
  "esrs_status": {"tr": "ESRS Durumu", "en": "ESRS Status"},
  "completion_rate": {"tr": "Tamamlanma Oranı", "en": "Completion Rate"},
  "chart_emission_dist": {"tr": "Emisyon Dağılımı", "en": "Emission Distribution"},
  "social_performance": {"tr": "Sosyal Performans (ISO 26000)", "en": "Social Performance (ISO 26000)"},
  "chart_emission_trend": {"tr": "Emisyon Trendi", "en": "Emission Trend"},
  "satisfaction": {"tr": "Memnuniyet", "en": "Satisfaction"},
  "training": {"tr": "Eğitim", "en": "Training"},
  "ohs": {"tr": "İSG", "en": "OHS"},
  "human_rights": {"tr": "İnsan Hakları", "en": "Human Rights"},
  "fair_labor": {"tr": "Adil Çalışma", "en": "Fair Labor"},
  "social_score": {"tr": "Sosyal Skor", "en": "Social Score"},
  "emission_tco2e": {"tr": "Emisyon (tCO2e)", "en": "Emission (tCO2e)"},
  "month_jan": {"tr": "Ocak", "en": "January"},
  "month_feb": {"tr": "Şubat", "en": "February"},
  "month_mar": {"tr": "Mart", "en": "March"},
  "month_apr": {"tr": "Nisan", "en": "April"},
  "month_may": {"tr": "Mayıs", "en": "May"},
  "month_jun": {"tr": "Haziran", "en": "June"},
  "month_jul": {"tr": "Temmuz", "en": "July"},
  "month_aug": {"tr": "Ağustos", "en": "August"},
  "month_sep": {"tr": "Eylül", "en": "September"},
  "month_oct": {"tr": "Ekim", "en": "October"},
  "month_nov": {"tr": "Kasım", "en": "November"},
  "month_dec": {"tr": "Aralık", "en": "December"},
  "module_carbon": {"tr": "Karbon Ayak İzi", "en": "Carbon Footprint"},
  "module_energy": {"tr": "Enerji Yönetimi", "en": "Energy Management"},
  "module_waste": {"tr": "Atık Yönetimi", "en": "Waste Management"},
  "module_water": {"tr": "Su Yönetimi", "en": "Water Management"},
  "module_biodiversity": {"tr": "Biyoçeşitlilik", "en": "Biodiversity"},
  "module_tcfd": {"tr": "TCFD", "en": "TCFD"},
  "module_tnfd": {"tr": "TNFD", "en": "TNFD"},
  "module_cdp": {"tr": "CDP", "en": "CDP"},
  "module_social_impact": {"tr": "Sosyal Etki", "en": "Social Impact"},
  "module_supply_chain": {"tr": "Tedarik Zinciri", "en": "Supply Chain"},
  "module_corporate_governance": {"tr": "Kurumsal Yönetişim", "en": "Corporate Governance"},
  "module_economic_value": {"tr": "Ekonomik Değer", "en": "Economic Value"},
  "module_prioritization": {"tr": "Önceliklendirme", "en": "Prioritization"},
  "module_esg_score": {"tr": "ESG Skoru", "en": "ESG Score"},
  "module_cbam": {"tr": "CBAM", "en": "CBAM"},
  "module_csrd": {"tr": "CSRD", "en": "CSRD"},
  "module_eu_taxonomy": {"tr": "AB Taksonomisi", "en": "EU Taxonomy"},
  "module_gri": {"tr": "GRI", "en": "GRI"},
  "module_sdg": {"tr": "SDG", "en": "SDG"},
  "module_esrs": {"tr": "ESRS", "en": "ESRS"},
  "module_ifrs": {"tr": "IFRS", "en": "IFRS"},
  "no_recent_activity": {"tr": "Henüz aktivite yok.", "en": "No recent activity."}
}

file_path = r"c:\SUSTAINAGESERVER\tools\translation_dictionary.json"

try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Merge keys
    for key, val in new_keys.items():
        if key not in data:
            data[key] = val
        else:
            # Update missing sub-keys
            for lang, text in val.items():
                if lang not in data[key]:
                    data[key][lang] = text
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print("Translation dictionary updated successfully.")
    
except Exception as e:
    print(f"Error: {e}")
