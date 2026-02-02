import json
import os

TR_JSON_PATH = 'c:/SUSTAINAGESERVER/locales/tr.json'
BACKEND_TR_JSON_PATH = 'c:/SUSTAINAGESERVER/backend/locales/tr.json'

KEYS_TO_ADD = {
    "total_responses": "Toplam Cevap",
    "btn_add_data": "Yeni Veri Girişi",
    "excel_report": "Excel Raporu",
    "satisfaction_score": "Memnuniyet Skoru",
    "turnover_rate": "Devir Hızı (%)",
    "surveys_title": "Anket Yönetimi",
    "active_surveys": "Aktif Anketler",
    "delete_survey": "Anketi Sil",
    "confirm_delete_survey": "Bu anketi silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.",
    "cancel": "İptal",
    "delete": "Sil",
    "statistics": "İstatistikler",
    "records": "Kayıtlar",
    "survey_title_col": "Anket Başlığı",
    "status_label": "Durum",
    "response_count": "Yanıt Sayısı",
    "created_at": "Oluşturulma Tarihi",
    "actions": "İşlemler",
    "manage": "Yönet",
    "view": "Görüntüle",
    "no_records_found": "Henüz kayıt bulunamadı.",
    "add_first_survey": "İlk Anketi Oluştur",
    "module_under_construction": "Modül Yapım Aşamasında",
    "module_coming_soon_desc": "Bu modülün web arayüzü entegrasyonu devam etmektedir.",
    "no_data_msg": "Veri bulunamadı veya modül henüz aktif değil.",
    "social_title": "Sosyal Performans",
    "social_desc": "Çalışan memnuniyeti, eğitim saatleri ve İSG verilerini takip edin.",
    "social_employee_profile": "Çalışan Profili",
    "social_total_employees": "Toplam Çalışan Sayısı",
    "gov_board_members": "Yönetim Kurulu",
    "gov_ethics_compliance": "Etik ve Uyum",
    "gov_manager_active": "Yönetişim Modülü Aktif",
    "gov_board_members_stat": "Aktif Üye",
    "gov_training_hours": "Eğitim Saati",
    "recent_activities": "Son Aktiviteler",
    "col_type": "Tür",
    "col_detail": "Detay",
    "col_date": "Tarih",
    "gov_board": "Yönetim Kurulu",
    "gov_committee": "Komite",
    "gov_ethics": "Etik",
    "no_data_yet": "Henüz veri yok."
}

def update_json(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        added_count = 0
        for key, value in KEYS_TO_ADD.items():
            if key not in data:
                data[key] = value
                added_count += 1
                print(f"Added missing key: {key} -> {value}")
        
        if added_count > 0:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Updated {path} with {added_count} new keys.")
        else:
            print(f"No new keys added to {path}.")
            
    except Exception as e:
        print(f"Error updating {path}: {e}")

if __name__ == "__main__":
    update_json(TR_JSON_PATH)
    update_json(BACKEND_TR_JSON_PATH)
