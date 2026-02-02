import json
import os

TR_JSON_PATH = r"c:\SUSTAINAGESERVER\locales\tr.json"

NEW_KEYS = {
    "dashboard_welcome": "Hoş Geldiniz",
    "dashboard_role": "Rol",
    "system_online": "Sistem Çevrimiçi",
    "users_title": "Kullanıcılar",
    "companies_title": "Firmalar",
    "reports_title": "Raporlar",
    "active_surveys": "Aktif Anketler",
    "total_responses": "Toplam Cevap",
    "recent_activities": "Son Aktiviteler",
    "filter": "Filtrele",
    "start_date": "Başlangıç",
    "end_date": "Bitiş",
    "module_action": "Modül / İşlem",
    "search_placeholder": "Ara...",
    "user": "Kullanıcı",
    "action": "İşlem",
    "date": "Tarih",
    "no_recent_activity": "Henüz aktivite yok.",
    "pending_actions": "Bekleyen İşler",
    "all_caught_up": "Harika! Bekleyen işiniz yok.",
    "sustainability_modules": "Sürdürülebilirlik Modülleri",
    "module_environmental": "Çevresel",
    "module_carbon": "Karbon Ayak İzi",
    "module_energy": "Enerji Yönetimi",
    "module_waste": "Atık Yönetimi",
    "module_water": "Su Yönetimi",
    "module_biodiversity": "Biyoçeşitlilik",
    "module_social_governance": "Sosyal & Yönetişim",
    "module_social_impact": "Sosyal Etki",
    "module_corporate_governance": "Kurumsal Yönetişim",
    
    # Labor Module Keys
    "labor_practices_title": "Çalışma Uygulamaları",
    "labor_practices_desc": "Çalışan hakları, iş sağlığı ve güvenliği, eğitim ve gelişim.",
    "module_active_badge": "Aktif",
    "module_passive_badge": "Pasif",
    "statistics": "İstatistikler",
    "records": "Kayıtlar",
    "details": "Detaylar",
    "no_records": "Henüz kayıt bulunmuyor.",
    "add_new_record": "Yeni Kayıt Ekle",
    "site_name": "Tesis/Lokasyon Adı",
    "audit_date": "Denetim Tarihi",
    "forced_labor_risk": "Zorla Çalıştırma Riski",
    "child_labor_risk": "Çocuk İşçiliği Riski",
    "risk_low": "Düşük",
    "risk_medium": "Orta",
    "risk_high": "Yüksek",
    "wage_compliance": "Ücret Uyumluluğu",
    "compliant": "Uyumlu",
    "non_compliant": "Uyumsuz",
    "union_rights": "Sendikal Haklar",
    "respected": "Saygı Gösteriliyor",
    "restricted": "Kısıtlı",
    "audit_score": "Denetim Puanı (0-100)",
    "cancel": "İptal",
    "save": "Kaydet"
}

def update_json():
    if not os.path.exists(TR_JSON_PATH):
        print(f"Error: {TR_JSON_PATH} not found.")
        return

    try:
        with open(TR_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        added_count = 0
        for key, value in NEW_KEYS.items():
            if key not in data:
                data[key] = value
                added_count += 1
                print(f"Added: {key}")
            else:
                # Optional: Update existing if needed, but for now we skip
                pass

        if added_count > 0:
            with open(TR_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Successfully added {added_count} keys to tr.json")
        else:
            print("No new keys to add.")

    except Exception as e:
        print(f"Error updating JSON: {e}")

if __name__ == "__main__":
    update_json()
