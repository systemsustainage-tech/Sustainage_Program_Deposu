import json
import os

file_path = r'C:\SUSTAINAGESERVER\locales\tr.json'

new_keys = {
    "eco_dist_title": "Ekonomik Değer Dağılımı (GRI 201-1)",
    "year": "Yıl",
    "total_revenue": "Toplam Gelir (Revenue)",
    "dist_eco_value": "Dağıtılan Ekonomik Değer",
    "operating_costs": "Operasyonel Giderler",
    "employee_wages": "Çalışan Maaş ve Yan Hakları",
    "payments_to_capital": "Sermaye Sağlayıcılara Ödemeler",
    "payments_to_gov": "Devlete Ödemeler (Vergi)",
    "community_investments": "Toplumsal Yatırımlar",
    "financial_perf": "Finansal Performans",
    "total_assets": "Toplam Varlıklar",
    "total_liabilities": "Toplam Yükümlülükler",
    "net_profit": "Net Kâr",
    "ebitda": "EBITDA",
    "roe": "Özkaynak Kârlılığı (ROE %)",
    "cancel": "İptal",
    
    "social_employee_profile": "Çalışan Profili Verisi",
    "employee_count": "Çalışan Sayısı",
    "gender": "Cinsiyet",
    "gender_female": "Kadın",
    "gender_male": "Erkek",
    "gender_other": "Diğer",
    "gender_total": "Toplam (Belirtilmemiş)",
    "department": "Departman",
    "social_ohs_record": "İSG Olay/Kaza Kaydı",
    "incident_type": "Olay Tipi",
    "incident_work_accident": "İş Kazası",
    "incident_occupational_disease": "Meslek Hastalığı",
    "incident_near_miss": "Ramak Kala",
    "incident_dangerous_occurrence": "Tehlikeli Durum",
    "date": "Tarih",
    "severity": "Ciddiyet",
    "severity_low": "Düşük",
    "severity_medium": "Orta",
    "severity_high": "Yüksek",
    "lost_days": "Kayıp İş Günü",
    "description": "Açıklama",
    "training_record": "Eğitim Kaydı",
    "training_name": "Eğitim Adı",
    "duration_hours": "Süre (Saat)",
    "participant_count": "Katılımcı Sayısı",
    
    "company_gri_title": "Firma Bilgileri (GRI Uyumlu)",
    "go_back": "Geri Dön",
    "legal_name": "Yasal Ad (Legal Name)",
    "tax_id": "Vergi No (Tax ID)",
    "address_headquarters": "Adres (Headquarters)",
    "founded_year": "Kuruluş Yılı",
    "sector_details": "Sektör Detayları",
    "contact_person": "İletişim Kişisi",
    "company_description": "Firma Tanımı (Description)",
    "mission": "Misyon (Mission)",
    "vision": "Vizyon (Vision)"
}

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update with new keys, preserving existing ones (or overwriting if intentional, here we just update)
    # I'll only add if missing to avoid overwriting "year" if it has specific meaning, but "Yıl" is generic.
    # Actually, I should overwrite if I want to be sure it matches my expectation, 
    # but "year" might be "Year" in English, here we are editing tr.json so it should be "Yıl".
    
    for k, v in new_keys.items():
        if k not in data:
            data[k] = v
        else:
            print(f"Key '{k}' already exists with value '{data[k]}'. Keeping existing.")
            
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print("tr.json updated successfully.")
    
except Exception as e:
    print(f"Error: {e}")
