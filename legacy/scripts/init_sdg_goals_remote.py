import sqlite3
import os
import datetime

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

goals_data = [
    (1, "1", "Yoksulluğa Son", "Her biçimiyle yoksulluğu her yerde sona erdirmek"),
    (2, "2", "Açlığa Son", "Açlığı bitirmek, gıda güvenliğini sağlamak ve sürdürülebilir tarımı desteklemek"),
    (3, "3", "Sağlık ve Kaliteli Yaşam", "Sağlıklı ve kaliteli yaşamı her yaşta güvence altına almak"),
    (4, "4", "Nitelikli Eğitim", "Kapsayıcı ve hakkaniyetli nitelikli eğitimi sağlamak ve herkes için yaşam boyu öğrenim fırsatlarını teşvik etmek"),
    (5, "5", "Toplumsal Cinsiyet Eşitliği", "Toplumsal cinsiyet eşitliğini sağlamak ve tüm kadınlar ile kız çocuklarını güçlendirmek"),
    (6, "6", "Temiz Su ve Sanitasyon", "Herkes için erişilebilir su ve atık su hizmetlerini ve sürdürülebilir su yönetimini güvence altına almak"),
    (7, "7", "Erişilebilir ve Temiz Enerji", "Herkes için uygun maliyetli, güvenilir, sürdürülebilir ve modern enerjiye erişimi sağlamak"),
    (8, "8", "İnsana Yakışır İş ve Ekonomik Büyüme", "İstikrarlı, kapsayıcı ve sürdürülebilir ekonomik büyümeyi, tam ve üretken istihdamı ve herkes için insana yakışır işleri desteklemek"),
    (9, "9", "Sanayi, Yenilikçilik ve Altyapı", "Dayanıklı altyapılar tesis etmek, kapsayıcı ve sürdürülebilir sanayileşmeyi desteklemek ve yenilikçiliği güçlendirmek"),
    (10, "10", "Eşitsizliklerin Azaltılması", "Ülkeler içinde ve arasında eşitsizlikleri azaltmak"),
    (11, "11", "Sürdürülebilir Şehirler ve Topluluklar", "Şehirleri ve insan yerleşimlerini kapsayıcı, güvenli, dayanıklı ve sürdürülebilir kılmak"),
    (12, "12", "Sorumlu Üretim ve Tüketim", "Sürdürülebilir üretim ve tüketim kalıplarını sağlamak"),
    (13, "13", "İklim Eylemi", "İklim değişikliği ve etkileri ile mücadele için acilen eyleme geçmek"),
    (14, "14", "Sudaki Yaşam", "Sürdürülebilir kalkınma için okyanusları, denizleri ve deniz kaynaklarını korumak ve sürdürülebilir kullanmak"),
    (15, "15", "Karasal Yaşam", "Karasal ekosistemleri korumak, iyileştirmek ve sürdürülebilir kullanımını desteklemek; sürdürülebilir orman yönetimini sağlamak; çölleşme ile mücadele etmek; arazi bozunumunu durdurmak ve tersine çevirmek; biyoçeşitlilik kaybını engellemek"),
    (16, "16", "Barış, Adalet ve Güçlü Kurumlar", "Sürdürülebilir kalkınma için barışçıl ve kapsayıcı toplumlar tesis etmek, herkes için adalete erişimi sağlamak ve her düzeyde etkili, hesap verebilir ve kapsayıcı kurumlar oluşturmak"),
    (17, "17", "Amaçlar için Ortaklıklar", "Uygulama araçlarını güçlendirmek ve sürdürülebilir kalkınma için küresel ortaklığı canlandırmak")
]

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop table to ensure clean state if schema is wrong (optional but safer given history)
    # Check if we should drop - let's try update/insert first to be safe
    
    # Ensure table exists with correct schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sdg_goals (
            id INTEGER PRIMARY KEY,
            code TEXT NOT NULL,
            title_tr TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check current count
    cursor.execute("SELECT COUNT(*) FROM sdg_goals")
    count = cursor.fetchone()[0]
    print(f"Current goal count: {count}")
    
    if count < 17:
        print("Populating goals...")
        cursor.execute("DELETE FROM sdg_goals") # Clear partial data
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for g in goals_data:
            cursor.execute(
                "INSERT INTO sdg_goals (id, code, title_tr, description, created_at) VALUES (?, ?, ?, ?, ?)",
                (g[0], g[1], g[2], g[3], current_time)
            )
        
        conn.commit()
        print("Goals populated successfully.")
    else:
        print("Goals already exist. Checking integrity...")
        # Optional: Update titles if they are empty/wrong
        for g in goals_data:
             cursor.execute("UPDATE sdg_goals SET title_tr = ?, description = ? WHERE id = ?", (g[2], g[3], g[0]))
        conn.commit()
        print("Goals updated.")

    conn.close()
    print("Done.")

except Exception as e:
    print(f"Error: {e}")
