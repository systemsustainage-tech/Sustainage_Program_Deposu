
import json
import os

file_path = 'c:/SUSTAINAGESERVER/locales/tr.json'

new_keys = {
    "roles_page_title": "Rol Yönetimi",
    "roles_header": "Rol Yönetimi",
    "roles_new_role": "Yeni Rol Ekle",
    "role_name": "Rol Adı",
    "role_description": "Açıklama",
    "role_is_system": "Sistem Rolü",
    "role_is_active": "Aktif",
    "confirm_delete_role": "Bu rolü silmek istediğinizden emin misiniz?",
    "role_edit_title": "Rol Düzenle",
    "role_add_title": "Yeni Rol Ekle",
    "role_edit_header": "Rol Düzenle",
    "role_add_header": "Yeni Rol Ekle",
    "role_display_name": "Görünen Ad",
    "role_is_system_label": "Sistem Rolü (Silinemez)",
    "role_is_active_label": "Aktif Rol",
    "permissions_header": "Yetkiler",
    "module_permissions": "Modül Yetkileri",
    "select_all": "Tümünü Seç",
    "deselect_all": "Seçimi Kaldır",
    "btn_edit": "Düzenle",
    "btn_delete": "Sil",
    "btn_save": "Kaydet",
    "btn_cancel": "İptal"
}

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated = False
    for k, v in new_keys.items():
        if k not in data:
            data[k] = v
            updated = True
            print(f"Added: {k}")
        else:
            print(f"Exists: {k}")
            
    if updated:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Successfully updated tr.json")
    else:
        print("No updates needed.")

except Exception as e:
    print(f"Error: {e}")
