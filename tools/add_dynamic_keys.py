
import json
import os

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.write('\n')

def add_keys():
    tr_path = 'c:/SUSTAINAGESERVER/locales/tr.json'
    en_path = 'c:/SUSTAINAGESERVER/locales/en.json'

    if not os.path.exists(tr_path):
        print(f"Error: {tr_path} not found")
        return
    if not os.path.exists(en_path):
        print(f"Error: {en_path} not found")
        return

    tr_data = load_json(tr_path)
    en_data = load_json(en_path)

    new_keys = {
        "status_active": {"tr": "Aktif", "en": "Active"},
        "status_pending": {"tr": "Beklemede", "en": "Pending"},
        "status_completed": {"tr": "Tamamlandı", "en": "Completed"},
        "status_assigned": {"tr": "Atandı", "en": "Assigned"},
        "status_cancelled": {"tr": "İptal Edildi", "en": "Cancelled"},
        "status_draft": {"tr": "Taslak", "en": "Draft"},
        "status_submitted": {"tr": "Gönderildi", "en": "Submitted"},
        "status_approved": {"tr": "Onaylandı", "en": "Approved"},
        "status_rejected": {"tr": "Reddedildi", "en": "Rejected"},
        "category_environmental": {"tr": "Çevresel", "en": "Environmental"},
        "category_social": {"tr": "Sosyal", "en": "Social"},
        "category_governance": {"tr": "Yönetişim", "en": "Governance"},
        "category_economic": {"tr": "Ekonomik", "en": "Economic"},
        "category_other": {"tr": "Diğer", "en": "Other"},
        "category_compliance": {"tr": "Uyumluluk", "en": "Compliance"},
        "category_reporting": {"tr": "Raporlama", "en": "Reporting"},
        "datetime": {"tr": "Tarih/Saat", "en": "Date/Time"}
    }

    added_count = 0
    for key, values in new_keys.items():
        if key not in tr_data:
            tr_data[key] = values["tr"]
            print(f"Added {key} to TR")
            added_count += 1
        
        if key not in en_data:
            en_data[key] = values["en"]
            print(f"Added {key} to EN")
            added_count += 1

    if added_count > 0:
        save_json(tr_path, tr_data)
        save_json(en_path, en_data)
        print(f"Successfully added {added_count} keys.")
    else:
        print("No new keys added.")

if __name__ == "__main__":
    add_keys()
