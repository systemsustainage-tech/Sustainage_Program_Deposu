import json
import os

file_path = r"c:\SUSTAINAGESERVER\locales\tr.json"

def fix_json():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading json: {e}")
        return

    # Fix corrupted keys
    corrections = {
        "module_passive_badge', 'Pasif": ("module_passive_badge", "Pasif"),
        "module_active_badge', 'Aktif": ("module_active_badge", "Aktif")
    }

    modified = False
    for bad_key, (correct_key, correct_value) in corrections.items():
        if bad_key in data:
            del data[bad_key]
            data[correct_key] = correct_value
            modified = True
            print(f"Fixed: {bad_key} -> {correct_key}")

    # Ensure other keys exist
    keys_to_ensure = {
        "btn_add_data": "Yeni Veri Girişi",
        "add_new_supplier": "Yeni Tedarikçi Ekle",
        "import_risks": "Riskleri İçe Aktar",
        "risk_alerts_title": "Önemli Risk Uyarıları",
        "supply_chain_title": "Tedarik Zinciri Sürdürülebilirliği",
        "supply_chain_desc": "Tedarikçilerinizi yönetin, risk değerlendirmeleri yapın ve sürdürülebilirlik performanslarını izleyin.",
        "search": "Ara",
        "search_placeholder": "Tedarikçi adı, sektör veya bölge...",
        "risk_level": "Risk Seviyesi",
        "all": "Tümü",
        "low_risk": "Düşük Risk (Skor > 70)",
        "medium_risk": "Orta Risk (50-70)",
        "high_risk": "Yüksek Risk (< 50)",
        "filter": "Filtrele",
        "clear": "Temizle",
        "supplier_list": "Tedarikçi Listesi",
        "supplier_name": "Tedarikçi Adı",
        "sector": "Sektör",
        "region_country": "Bölge",
        "risk_score": "Risk Skoru",
        "actions": "İşlemler",
        "details": "Detay",
        "no_supplier_defined": "Henüz bir tedarikçi tanımlanmamış.",
        "add_first_supplier": "İlk Tedarikçiyi Ekle",
        "contact_info": "İletişim Bilgileri",
        "cancel": "İptal",
        "save": "Kaydet",
        "import_risk_data": "Risk Verilerini İçe Aktar (Excel)",
        "excel_columns_info": "Excel dosyanız şu sütunları içermelidir: Tedarikçi Adı, Risk Kategorisi, Risk Açıklaması, Olasılık (1-5), Etki (1-5), Azaltma Planı",
        "select_excel_file": "Excel Dosyası Seç",
        "upload_and_import": "Yükle ve İçe Aktar",
        "btn_back": "Geri",
        "back": "Geri",
        "respondent_info": "Katılımcı Bilgileri",
        "respondent_name": "İsim Soyisim",
        "company": "Firma",
        "email": "E-posta",
        "submission_date": "Gönderim Tarihi",
        "answers": "Yanıtlar",
        "question": "Soru",
        "category": "Kategori",
        "answer": "Verilen Yanıt",
        "no_answers_found": "Yanıt bulunamadı.",
        "survey_response_details": "Anket Yanıt Detayı",
        "not_specified": "Belirtilmemiş"
    }

    for k, v in keys_to_ensure.items():
        if k not in data:
            data[k] = v
            modified = True
            print(f"Added missing key: {k}")
        elif data[k] != v:
            # Optional: update value if it matches the new standard (e.g. btn_add_data)
            if k == "btn_add_data" and data[k] != "Yeni Veri Girişi":
                data[k] = "Yeni Veri Girişi"
                modified = True
                print(f"Updated key: {k}")

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("locales/tr.json updated.")
    else:
        print("No changes needed for locales/tr.json.")

if __name__ == "__main__":
    fix_json()
