import json
import os

file_path = 'c:/SUSTAINAGESERVER/backend/locales/tr.json'

new_keys = {
    "role_name_key": "Rol Anahtarı (Kod)",
    "role_display_name": "Görünen Ad",
    "role_description": "Açıklama",
    "role_info": "Rol Bilgileri",
    "role_permissions": "Yetkiler",
    "role_system": "Sistem",
    "role_custom": "Özel",
    "roles_page_title": "Rol Yönetimi",
    "roles_header": "Rol Yönetimi",
    "roles_new_role": "Yeni Rol Ekle",
    "roles_confirm_delete": "Bu rolü silmek istediğinize emin misiniz?",
    "roles_no_records": "Kayıtlı rol bulunamadı.",
    "role_edit_title": "Rol Düzenle",
    "role_add_title": "Yeni Rol Ekle",
    "role_edit_header": "Rol Düzenle",
    "role_add_header": "Yeni Rol Ekle",
    "role_name_help": "Benzersiz sistem adı (örn: editor, analyst)",
    "select_all": "Tümünü Seç",
    "deselect_all": "Tümünü Kaldır",
    "audit_log_title": "Denetim İzi (Audit Logs)",
    "audit_log_action": "İşlem",
    "audit_log_user": "Kullanıcı",
    "audit_log_date": "Tarih",
    "audit_log_details": "Detaylar",
    "audit_log_ip": "IP Adresi",
    "audit_log_resource": "Kaynak",
    "audit_log_id": "ID"
}

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} keys.")
    
    updated_count = 0
    for k, v in new_keys.items():
        if k not in data:
            data[k] = v
            updated_count += 1
            print(f"Added: {k}")
        else:
            print(f"Skipped (exists): {k}")
            
    if updated_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully updated {updated_count} keys in {file_path}")
    else:
        print("No new keys to add.")

except Exception as e:
    print(f"Error: {e}")
