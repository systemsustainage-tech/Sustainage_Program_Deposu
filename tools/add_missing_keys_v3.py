import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT_PATH = os.path.join(BASE_DIR, 'tools', 'translation_dictionary.json')

NEW_KEYS = {
    "category_compliance": {"en": "Compliance & Standards", "tr": "Uyum ve Standartlar"},
    "dashboard_welcome": {"en": "Welcome to your sustainability dashboard.", "tr": "Sürdürülebilirlik paneline hoş geldiniz."},
    "dark_mode": {"en": "Dark Mode", "tr": "Koyu Mod"},
    "light_mode": {"en": "Light Mode", "tr": "Açık Mod"},
    "completed_reports": {"en": "Completed Reports", "tr": "Tamamlanan Raporlar"},
    "carbon_emissions": {"en": "Carbon Emissions", "tr": "Karbon Emisyonu"},
    "survey_status": {"en": "Survey Status", "tr": "Anket Durumu"},
    "system_alert_title": {"en": "System Notification", "tr": "Sistem Bildirimi"},
    "completion": {"en": "Completion", "tr": "Tamamlanma"},
    "action_enter_data": {"en": "Enter Data", "tr": "Veri Gir"},
    "action_enter_data_short": {"en": "Enter", "tr": "Giriş"},
    "action_view_details": {"en": "View Details", "tr": "Detayları Gör"},
    "action_create_report": {"en": "Create Report", "tr": "Rapor Oluştur"},
    "status_completed": {"en": "Completed", "tr": "Tamamlandı"},
    "status_not_started": {"en": "Not Started", "tr": "Başlanmadı"},
    "status_active": {"en": "Active", "tr": "Aktif"},
    "status_pending": {"en": "Pending", "tr": "Bekliyor"}
}

def update_dictionary():
    if not os.path.exists(DICT_PATH):
        print(f"Error: Dictionary not found at {DICT_PATH}")
        return

    with open(DICT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Ensure structure
    if 'en' not in data: data['en'] = {}
    if 'tr' not in data: data['tr'] = {}
    
    added_count = 0
    for key, translations in NEW_KEYS.items():
        # Update logic: force update if key exists to ensure correct translation
        data['en'][key] = translations['en']
        data['tr'][key] = translations['tr']
        added_count += 1
        print(f"Added/Updated key: {key}")

    with open(DICT_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Successfully processed {added_count} keys.")
    
    # Also run the sync script
    sys.path.append(os.path.join(BASE_DIR, 'tools'))
    try:
        from update_translations import update_translations
        print("Running update_translations...")
        update_translations()
    except ImportError:
        print("Could not import update_translations script.")

if __name__ == "__main__":
    update_dictionary()
