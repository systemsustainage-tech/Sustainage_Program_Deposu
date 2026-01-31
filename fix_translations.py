
import json
import os

translations = {
    "and": "ve",
    "are_pending_reporting": "raporlama bekliyor.",
    "cdp_c1_1": "Kuruluşunuzun iklimle ilgili konularda yönetim kurulu düzeyinde gözetimi var mı?",
    "cdp_c1_2": "Lütfen kuruluşunuzun iklim değişikliği yönetişim yapısının ayrıntılarını verin.",
    "cdp_c1_3": "İklimle ilgili konuların yönetimi için teşvik sağlıyor musunuz?",
    "cdp_c2_1": "İşiniz üzerinde önemli finansal veya stratejik etki yaratma potansiyeline sahip iklimle ilgili riskler belirlediniz mi?",
    "cdp_c2_2": "Kısa, orta ve uzun vadeli zaman dilimlerini nasıl tanımlıyorsunuz?",
    "cdp_c2_3": "İklimle ilgili risklerin ve fırsatların işiniz üzerindeki potansiyel etkisini nasıl değerlendiriyorsunuz?",
    "cdp_c3_1": "İklimle ilgili riskleri belirleme, değerlendirme ve yönetme süreciniz var mı?",
    "cdp_c4_1": "İklimle ilgili fırsatları belirleme, değerlendirme ve yönetme süreciniz var mı?",
    "cdp_c4_2": "Kuruluşunuzun toplam brüt küresel Kapsam 1 ve Kapsam 2 sera gazı emisyonları nedir?",
    "cdp_c4_3": "Kuruluşunuzun toplam brüt küresel Kapsam 3 sera gazı emisyonları nedir?",
    "cdp_cat_gov_cc": "Yönetim kurulu gözetimi ve iklim konularının yönetimi",
    "cdp_cat_gov_f": "Yönetim kurulu gözetimi ve orman konularının yönetimi",
    "cdp_cat_gov_ws": "Yönetim kurulu gözetimi ve su konularının yönetimi",
    "cdp_cat_met_cc": "İklim metrikleri, hedefler ve performans",
    "cdp_cat_met_f": "Orman metrikleri, hedefler ve performans",
    "cdp_cat_met_ws": "Su metrikleri, hedefler ve performans",
    "cdp_cat_str_cc": "İklim stratejisi ve risk değerlendirmesi",
    "cdp_cat_str_f": "Orman stratejisi ve risk değerlendirmesi",
    "cdp_cat_str_ws": "Su stratejisi ve risk değerlendirmesi",
    "cdp_w1_1": "Kuruluşunuzun su ile ilgili konularda yönetim kurulu düzeyinde gözetimi var mı?",
    "cdp_w1_2": "Lütfen kuruluşunuzun su yönetişim yapısının ayrıntılarını verin.",
    "cdp_w1_3": "Su ile ilgili konuların yönetimi için teşvik sağlıyor musunuz?",
    "cdp_w2_1": "İşiniz üzerinde önemli finansal veya stratejik etki yaratma potansiyeline sahip su ile ilgili riskler belirlediniz mi?",
    "cdp_w2_2": "Su ile ilgili risklerin ve fırsatların işiniz üzerindeki potansiyel etkisini nasıl değerlendiriyorsunuz?",
    "cdp_w3_1": "Su ile ilgili riskleri belirleme, değerlendirme ve yönetme süreciniz var mı?",
    "cdp_w4_1": "Kuruluşunuzun toplam su çekimi nedir?",
    "cdp_w4_2": "Kuruluşunuzun toplam su tüketimi nedir?",
    "gri_11_name": "Petrol ve Gaz Sektörü",
    "gri_13_name": "Tarım, Su Ürünleri ve Balıkçılık Sektörleri",
    "gri_commitment_text": "Bu rapor, GRI standartlarına uygun olarak şeffaflık ve sürdürülebilirlik raporlamasına olan taahhüdümüzü göstermektedir.",
    "gri_report_intro": "Bu GRI sürdürülebilirlik raporu şunları kapsar",
    "of_the": "tarihli",
    "statement_of_use": "Kullanım Beyanı",
    "table_of_contents": "İçindekiler",
    "topic_artisanal_mining": "Zanaatkar ve Küçük Ölçekli Madencilik",
    "topic_health_safety": "İş Sağlığı ve Güvenliği",
    "topic_health_safety_mining": "İş Sağlığı ve Güvenliği (Madencilik)",
    "topic_labor_rights_agri": "Tarımda İşçi Hakları",
    "topic_spill": "Döküntü Önleme ve Müdahale",
    "topic_water_tailings": "Su ve Atık Yönetimi",
    "topic_water_usage": "Su Kullanımı ve Kalitesi"
}

def fix():
    file_path = 'locales/tr.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = 0
    for k, v in translations.items():
        if k in data:
            data[k] = v
            count += 1
        else:
            print(f"Key not found: {k}")
            
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    print(f"Updated {count} translations in {file_path}")

if __name__ == "__main__":
    fix()
