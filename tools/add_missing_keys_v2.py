import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT_PATH = os.path.join(BASE_DIR, 'tools', 'translation_dictionary.json')

NEW_KEYS = {
    "biodiversity": {"en": "Biodiversity", "tr": "Biyoçeşitlilik"},
    "supply_chain": {"en": "Supply Chain", "tr": "Tedarik Zinciri"},
    "economic": {"en": "Economic", "tr": "Ekonomik"},
    "esg": {"en": "ESG", "tr": "ESG"},
    "cbam": {"en": "CBAM", "tr": "SKDM (CBAM)"},
    "csrd": {"en": "CSRD", "tr": "KSRD (CSRD)"},
    "taxonomy": {"en": "EU Taxonomy", "tr": "AB Taksonomisi"},
    "gri": {"en": "GRI", "tr": "GRI"},
    "sdg": {"en": "SDG", "tr": "SKA (SDG)"},
    "esrs": {"en": "ESRS", "tr": "ESRS"},
    "prioritization": {"en": "Prioritization", "tr": "Önceliklendirme"},
    "ifrs": {"en": "IFRS", "tr": "UFRS (IFRS)"},
    "tcfd": {"en": "TCFD", "tr": "TCFD"},
    "tnfd": {"en": "TNFD", "tr": "TNFD"},
    "cdp": {"en": "CDP", "tr": "CDP"},
    "product_technology": {"en": "Product & Technology", "tr": "Ürün ve Teknoloji"},
    "regulation": {"en": "Regulation", "tr": "Regülasyon"},
    "unified_report": {"en": "Unified Report", "tr": "Birleşik Rapor"},
    "benchmark": {"en": "Benchmark", "tr": "Kıyaslama"},
    "issb": {"en": "ISSB", "tr": "ISSB"},
    "risk": {"en": "Risk", "tr": "Risk"},
    "compliance": {"en": "Compliance", "tr": "Uyumluluk"},
    "ethics": {"en": "Ethics", "tr": "Etik"},
    "human_rights": {"en": "Human Rights", "tr": "İnsan Hakları"},
    "stakeholders": {"en": "Stakeholders", "tr": "Paydaşlar"},
    "carbon": {"en": "Carbon", "tr": "Karbon"},
    "energy": {"en": "Energy", "tr": "Enerji"},
    "water": {"en": "Water", "tr": "Su"},
    "waste": {"en": "Waste", "tr": "Atık"},
    "social": {"en": "Social", "tr": "Sosyal"},
    "governance": {"en": "Governance", "tr": "Yönetişim"}
}

def update_dictionary():
    with open(DICT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Ensure structure is data['en'][key] and data['tr'][key]
    if 'en' not in data: data['en'] = {}
    if 'tr' not in data: data['tr'] = {}
    
    added_count = 0
    for key, translations in NEW_KEYS.items():
        # Update logic: If key exists, only update if empty or explicitly forcing (here we update if missing)
        # But for modules, I want to ensure they are present.
        if key not in data['en']:
            data['en'][key] = translations['en']
            data['tr'][key] = translations['tr']
            added_count += 1
            print(f"Added key: {key}")
        else:
            # Check if tr is missing
            if key not in data['tr']:
                data['tr'][key] = translations['tr']
                print(f"Added TR for existing key: {key}")
                added_count += 1

    if added_count > 0:
        with open(DICT_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully added {added_count} keys to translation dictionary.")
    else:
        print("No new keys added.")

if __name__ == "__main__":
    update_dictionary()
