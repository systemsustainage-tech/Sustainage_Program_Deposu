import json
import os

def update_translations():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tr_path = os.path.join(base_dir, 'locales', 'tr.json')
    
    new_keys = {
        "sdg_goal_selection": "Hedef Seçimi",
        "sdg_save_selections": "Seçimleri Kaydet",
        "sdg_selected_details": "Seçilen Hedef Detayları ve Modül Bağlantıları",
        "sdg_link_available": "Bağlantısı Var",
        "sdg_go_to_module": "Modülüne Git",
        "sdg_data_questions": "Veri Giriş Soruları ve GRI Bağlantıları",
        "sdg_col_question": "Soru",
        "sdg_col_gri": "GRI Göstergesi",
        "sdg_col_responsible": "Sorumlu",
        # Add titles for missing modules just in case
        "cbam_title": "CBAM Raporlama",
        "csrd_title": "CSRD Uyumluluk",
        "taxonomy_title": "AB Taksonomisi",
        "esg_title": "ESG Skoru",
        "issb_title": "ISSB Standartları",
        "iirc_title": "Entegre Raporlama (IIRC)",
        "esrs_title": "ESRS Standartları",
        "tcfd_title": "TCFD İklim Riskleri",
        "tnfd_title": "TNFD Doğa İlişkili Beyanlar",
        "biodiversity_title": "Biyoçeşitlilik Yönetimi",
        "waste_title": "Atık Yönetimi",
        "water_title": "Su Yönetimi",
        "energy_title": "Enerji Yönetimi",
        "carbon_title": "Karbon Ayak İzi",
        "social_title": "Sosyal Etki",
        "governance_title": "Kurumsal Yönetişim",
        "economic_title": "Ekonomik Performans",
        "supply_chain_title": "Tedarik Zinciri",
        "gri_title": "GRI Raporlama"
    }
    
    try:
        with open(tr_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        updated = False
        for k, v in new_keys.items():
            if k not in data:
                data[k] = v
                updated = True
                print(f"Added key: {k}")
            # Optional: Update existing if needed (commented out to be safe)
            # else:
            #     if data[k] != v:
            #         data[k] = v
            #         updated = True
            #         print(f"Updated key: {k}")
                    
        if updated:
            with open(tr_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("Translations updated successfully.")
        else:
            print("No changes needed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_translations()
