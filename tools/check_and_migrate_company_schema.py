import sqlite3
import os

# Doğru DB yolu
DB_PATH = os.path.join("c:\\SUSTAINAGESERVER", "backend", "data", "sdg_desktop.sqlite")

def migrate_company_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get existing columns
    try:
        cursor.execute("PRAGMA table_info(company_info)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"Existing columns: {columns}")
    except Exception as e:
        print(f"Error reading table info: {e}")
        conn.close()
        return

    new_columns = [
        ("vizyon", "TEXT"),
        ("misyon", "TEXT"),
        ("degerler", "TEXT"),
        ("tesisler_ozet", "TEXT"),
        ("kilometre_taslari_ozet", "TEXT"),
        ("urun_hizmet_ozet", "TEXT"),
        ("karbon_profili_ozet", "TEXT"),
        ("uyelikler_ozet", "TEXT"),
        ("oduller_ozet", "TEXT")
    ]

    for col_name, col_type in new_columns:
        if col_name not in columns:
            print(f"Adding missing column: {col_name}")
            try:
                cursor.execute(f"ALTER TABLE company_info ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")
        else:
            print(f"Column {col_name} already exists.")

    conn.commit()
    conn.close()
    print("Migration check completed.")

if __name__ == "__main__":
    migrate_company_schema()
