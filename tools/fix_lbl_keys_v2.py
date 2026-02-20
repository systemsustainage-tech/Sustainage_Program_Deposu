import json
import os

dict_path = r'c:\SUSTAINAGESERVER\tools\translation_dictionary.json'

with open(dict_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Ensure 'tr' block exists
if 'tr' not in data:
    data['tr'] = {}

updates = {
    "lbl_companies": "Şirketler",
    "lbl_fullname": "Ad Soyad",
    "lbl_password_hint": "Şifre İpucu",
    "lbl_user_active": "Kullanıcı Aktif",
    "lbl_tax_number": "Vergi Numarası",
    "lbl_company_active": "Firma Aktif Durumu",
    "lbl_module": "Modül",
    "lbl_company_name": "Firma Adı",
    "lbl_department": "Departman:",
    "lbl_description": "Açıklama",
    "lbl_email": "E-posta",
    "lbl_password": "Şifre:",
    "lbl_report_file": "Rapor Dosyası",
    "lbl_report_name": "Rapor Adı",
    "lbl_report_type": "Rapor Türü",
    "lbl_reporting_period": "Raporlama Dönemi",
    "lbl_roles": "Roller",
    "lbl_sector": "Sektör",
    "lbl_username": "Kullanıcı Adı:",
    "lbl_phone": "Telefon",
    "lbl_website": "Web Sitesi",
    "lbl_address": "Adres",
    "lbl_city": "İl",
    "lbl_district": "İlçe",
    "lbl_postcode": "Posta Kodu",
    "lbl_country": "Ülke",
    "lbl_employees": "Çalışan Sayısı",
    "lbl_commercial_title": "Ticari Ünvan"
}

count = 0
for key, value in updates.items():
    # Only update if missing or explicitly placeholder-like (though I'm overwriting to be safe)
    # Check if current value is missing or looks like "Lbl ..."
    current_val = data['tr'].get(key, "")
    if not current_val or current_val.startswith("Lbl ") or current_val == key:
        data['tr'][key] = value
        count += 1
        print(f"Updated {key}: {value}")
    elif current_val != value:
        # If it exists but different, update it to standard
        data['tr'][key] = value
        count += 1
        print(f"Updated {key}: {value} (was {current_val})")

print(f"Total updates: {count}")

with open(dict_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
