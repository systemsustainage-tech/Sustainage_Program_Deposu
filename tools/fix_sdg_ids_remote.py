import sqlite3
import datetime

DB_PATH = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'

GOALS = [
    (1, "Yoksulluğa Son"),
    (2, "Açlığa Son"),
    (3, "Sağlık ve Kaliteli Yaşam"),
    (4, "Nitelikli Eğitim"),
    (5, "Toplumsal Cinsiyet Eşitliği"),
    (6, "Temiz Su ve Sanitasyon"),
    (7, "Erişilebilir ve Temiz Enerji"),
    (8, "İnsana Yakışır İş ve Ekonomik Büyüme"),
    (9, "Sanayi, Yenilikçilik ve Altyapı"),
    (10, "Eşitsizliklerin Azaltılması"),
    (11, "Sürdürülebilir Şehirler ve Topluluklar"),
    (12, "Sorumlu Üretim ve Tüketim"),
    (13, "İklim Eylemi"),
    (14, "Sudaki Yaşam"),
    (15, "Karasal Yaşam"),
    (16, "Barış, Adalet ve Güçlü Kurumlar"),
    (17, "Amaçlar İçin Ortaklıklar")
]

def fix_ids():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("Cleaning sdg_goals table...")
        cursor.execute("DELETE FROM sdg_goals")
        
        print("Resetting auto-increment...")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='sdg_goals'")
        
        print("Inserting goals with correct IDs...")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for code, title in GOALS:
            # We explicitly set ID to ensure it matches the image filename
            cursor.execute(
                "INSERT INTO sdg_goals (id, code, title_tr, created_at) VALUES (?, ?, ?, ?)",
                (code, code, title, now)
            )
            
        conn.commit()
        print("Done. All 17 goals inserted with correct IDs.")
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_ids()
