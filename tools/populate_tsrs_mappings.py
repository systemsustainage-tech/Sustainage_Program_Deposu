import sqlite3
import os
import datetime

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "backend", "data", "sdg_desktop.sqlite")

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def populate_mappings():
    print(f"Connecting to database at {DB_PATH}...")
    conn = get_db_connection()
    cur = conn.cursor()

    # --- 1. Populate map_sdg_tsrs ---
    print("Populating map_sdg_tsrs...")
    cur.execute("DELETE FROM map_sdg_tsrs") # Clear existing to avoid duplicates/conflicts
    
    # Format: (sdg_indicator_code, tsrs_section, tsrs_metric)
    sdg_tsrs_data = [
        # SDG 1: No Poverty
        ('1.1.1', 'TSRS S1: Sosyal - Çalışanlar', 'S1-10: Yeterli Ücret'),
        ('1.2.1', 'TSRS S1: Sosyal - Çalışanlar', 'S1-11: Sosyal Güvence'),
        
        # SDG 3: Good Health
        ('3.8.1', 'TSRS S1: Sosyal - Çalışanlar', 'S1-12: Sağlık ve Güvenlik'),
        ('3.9.1', 'TSRS E2: Kirlilik', 'E2-4: Hava Kirliliği'),

        # SDG 4: Quality Education
        ('4.3.1', 'TSRS S1: Sosyal - Çalışanlar', 'S1-13: Eğitim ve Gelişim'),
        ('4.4.1', 'TSRS S1: Sosyal - Çalışanlar', 'S1-13: Yetenek Yönetimi'),

        # SDG 5: Gender Equality
        ('5.1.1', 'TSRS S1: Sosyal - Çalışanlar', 'S1-9: Çeşitlilik ve Kapsayıcılık'),
        ('5.5.1', 'TSRS G1: Yönetişim', 'G1-1: Yönetim Kurulu Yapısı'),
        ('5.5.2', 'TSRS S1: Sosyal - Çalışanlar', 'S1-16: Kadın Yönetici Oranı'),

        # SDG 6: Clean Water
        ('6.3.1', 'TSRS E3: Su ve Deniz Kaynakları', 'E3-1: Su Tüketimi'),
        ('6.4.1', 'TSRS E3: Su ve Deniz Kaynakları', 'E3-2: Su Verimliliği'),

        # SDG 7: Affordable Energy
        ('7.2.1', 'TSRS E1: İklim Değişikliği', 'E1-5: Yenilenebilir Enerji'),
        ('7.3.1', 'TSRS E1: İklim Değişikliği', 'E1-6: Enerji Yoğunluğu'),

        # SDG 8: Decent Work
        ('8.5.1', 'TSRS S1: Sosyal - Çalışanlar', 'S1-1: İstihdam Politikaları'),
        ('8.8.1', 'TSRS S1: Sosyal - Çalışanlar', 'S1-14: İş Sağlığı ve Güvenliği'),
        ('8.7.1', 'TSRS S2: Değer Zincirindeki Çalışanlar', 'S2-1: Çocuk İşçiliği'),

        # SDG 9: Industry & Innovation
        ('9.4.1', 'TSRS E1: İklim Değişikliği', 'E1-9: CO2 Emisyonları'),
        
        # SDG 10: Reduced Inequalities
        ('10.2.1', 'TSRS S1: Sosyal - Çalışanlar', 'S1-17: Ayrımcılık Karşıtlığı'),
        ('10.4.1', 'TSRS S1: Sosyal - Çalışanlar', 'S1-10: Ücret Eşitliği'),

        # SDG 11: Sustainable Cities
        ('11.6.1', 'TSRS E5: Kaynak Kullanımı', 'E5-5: Atık Yönetimi'),
        ('11.6.2', 'TSRS E2: Kirlilik', 'E2-2: Partikül Madde'),

        # SDG 12: Responsible Consumption
        ('12.2.1', 'TSRS E5: Kaynak Kullanımı', 'E5-4: Hammadde Kullanımı'),
        ('12.5.1', 'TSRS E5: Kaynak Kullanımı', 'E5-6: Geri Dönüşüm Oranı'),
        ('12.6.1', 'TSRS G1: Yönetişim', 'G1-3: Sürdürülebilirlik Raporlaması'),

        # SDG 13: Climate Action
        ('13.1.1', 'TSRS E1: İklim Değişikliği', 'E1-1: İklim Riskleri'),
        ('13.2.1', 'TSRS E1: İklim Değişikliği', 'E1-3: Azaltım Hedefleri'),

        # SDG 16: Peace & Justice
        ('16.5.1', 'TSRS G1: Yönetişim', 'G1-4: Yolsuzlukla Mücadele'),
        ('16.6.2', 'TSRS G1: Yönetişim', 'G1-5: Şeffaflık'),
    ]

    for row in sdg_tsrs_data:
        cur.execute(
            "INSERT INTO map_sdg_tsrs (sdg_indicator_code, tsrs_section, tsrs_metric, created_at) VALUES (?, ?, ?, ?)",
            (row[0], row[1], row[2], datetime.datetime.now())
        )
    print(f"Inserted {len(sdg_tsrs_data)} rows into map_sdg_tsrs.")


    # --- 2. Populate map_gri_tsrs ---
    print("Populating map_gri_tsrs...")
    cur.execute("DELETE FROM map_gri_tsrs")
    
    # Format: (gri_standard, gri_disclosure, tsrs_section, tsrs_metric)
    gri_tsrs_data = [
        # GRI 200: Economic
        ('GRI 201', '201-1', 'TSRS E1: İklim Değişikliği', 'E1-9: Finansal Etkiler'),
        ('GRI 201', '201-2', 'TSRS E1: İklim Değişikliği', 'E1-1: İklim Riskleri'),
        ('GRI 205', '205-1', 'TSRS G1: Yönetişim', 'G1-4: Yolsuzluk Riskleri'),
        ('GRI 205', '205-2', 'TSRS G1: Yönetişim', 'G1-4: Yolsuzluk Eğitimi'),
        ('GRI 205', '205-3', 'TSRS G1: Yönetişim', 'G1-4: Yolsuzluk Vakaları'),

        # GRI 300: Environmental
        ('GRI 302', '302-1', 'TSRS E1: İklim Değişikliği', 'E1-5: Enerji Tüketimi'),
        ('GRI 302', '302-3', 'TSRS E1: İklim Değişikliği', 'E1-6: Enerji Yoğunluğu'),
        ('GRI 303', '303-3', 'TSRS E3: Su', 'E3-1: Su Çekimi'),
        ('GRI 303', '303-5', 'TSRS E3: Su', 'E3-2: Su Tüketimi'),
        ('GRI 305', '305-1', 'TSRS E1: İklim Değişikliği', 'E1-6: Kapsam 1 Emisyonları'),
        ('GRI 305', '305-2', 'TSRS E1: İklim Değişikliği', 'E1-6: Kapsam 2 Emisyonları'),
        ('GRI 305', '305-3', 'TSRS E1: İklim Değişikliği', 'E1-6: Kapsam 3 Emisyonları'),
        ('GRI 306', '306-3', 'TSRS E5: Kaynaklar', 'E5-5: Atık Oluşumu'),

        # GRI 400: Social
        ('GRI 401', '401-1', 'TSRS S1: Sosyal', 'S1-6: İşe Alım ve Ayrılma'),
        ('GRI 403', '403-9', 'TSRS S1: Sosyal', 'S1-14: İş Kazaları'),
        ('GRI 404', '404-1', 'TSRS S1: Sosyal', 'S1-13: Eğitim Saatleri'),
        ('GRI 405', '405-1', 'TSRS S1: Sosyal', 'S1-9: Çeşitlilik Göstergeleri'),
        ('GRI 406', '406-1', 'TSRS S1: Sosyal', 'S1-17: Ayrımcılık Vakaları'),
        ('GRI 413', '413-1', 'TSRS S3: Toplum', 'S3-1: Yerel Topluluk Katılımı'),
    ]

    for row in gri_tsrs_data:
        cur.execute(
            "INSERT INTO map_gri_tsrs (gri_standard, gri_disclosure, tsrs_section, tsrs_metric, created_at) VALUES (?, ?, ?, ?, ?)",
            (row[0], row[1], row[2], row[3], datetime.datetime.now())
        )
    print(f"Inserted {len(gri_tsrs_data)} rows into map_gri_tsrs.")

    conn.commit()
    conn.close()
    print("Mapping population completed successfully.")

if __name__ == "__main__":
    populate_mappings()
