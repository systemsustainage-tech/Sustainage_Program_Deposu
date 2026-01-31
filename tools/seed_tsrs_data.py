import sqlite3
import os

def seed_data():
    # Database paths to check
    db_paths = [
        'c:\\SUSTAINAGESERVER\\backend\\sustainage.db',
        'c:\\SUSTAINAGESERVER\\sustainage.db',
        '/var/www/sustainage/backend/sustainage.db',
        'backend/sustainage.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
            
    if not db_path:
        print("Database not found!")
        return
        
    print(f"Seeding database at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Seed TSRS Standards
        standards = [
            ('TSRS 1', 'Genel Hükümler', 'Sürdürülebilirlik raporlaması için genel gereklilikler', 'Genel', 'Genel', 'Zorunlu', 'Yıllık', '2024-01-01'),
            ('TSRS 2', 'İklimle İlgili Açıklamalar', 'İklim değişikliği ile ilgili riskler ve fırsatlar', 'Çevresel', 'İklim', 'Zorunlu', 'Yıllık', '2024-01-01')
        ]
        
        print("Seeding TSRS Standards...")
        for std in standards:
            cursor.execute("""
                INSERT OR IGNORE INTO tsrs_standards (code, title, description, category, subcategory, requirement_level, reporting_frequency, effective_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, std)
        
        # Get Standard IDs
        cursor.execute("SELECT id, code FROM tsrs_standards")
        std_map = {row[1]: row[0] for row in cursor.fetchall()}

        # 2. Seed TSRS Indicators
        indicators = [
            # TSRS 1 Indicators
            (std_map.get('TSRS 1'), 'TSRS-1-1', 'Yönetim Kurulu Gözetimi', 'Sürdürülebilirlik risklerinin ve fırsatlarının gözetimi', 'Metin', 'Açıklama', 'Metin', 1, 0),
            (std_map.get('TSRS 1'), 'TSRS-1-2', 'Yönetim Rolü', 'Yönetimin riskleri ve fırsatları değerlendirmedeki rolü', 'Metin', 'Açıklama', 'Metin', 1, 0),
            
            # TSRS 2 Indicators
            (std_map.get('TSRS 2'), 'TSRS-2-1', 'Sera Gazı Emisyonları (Kapsam 1)', 'Doğrudan sera gazı emisyonları', 'ton CO2e', 'GHG Protokolü', 'Sayısal', 1, 1),
            (std_map.get('TSRS 2'), 'TSRS-2-2', 'Sera Gazı Emisyonları (Kapsam 2)', 'Dolaylı enerji kaynaklı sera gazı emisyonları', 'ton CO2e', 'GHG Protokolü', 'Sayısal', 1, 1),
            (std_map.get('TSRS 2'), 'TSRS-2-3', 'Sera Gazı Emisyonları (Kapsam 3)', 'Diğer dolaylı sera gazı emisyonları', 'ton CO2e', 'GHG Protokolü', 'Sayısal', 0, 1),
            (std_map.get('TSRS 2'), 'TSRS-2-4', 'Fiziksel İklim Riskleri', 'Şirketin maruz kaldığı fiziksel iklim riskleri', 'Metin', 'Risk Analizi', 'Metin', 1, 0),
            (std_map.get('TSRS 2'), 'TSRS-2-5', 'İklimle İlgili Fırsatlar', 'İklim değişikliğinin yarattığı fırsatlar', 'Metin', 'Fırsat Analizi', 'Metin', 1, 0)
        ]

        print("Seeding TSRS Indicators...")
        for ind in indicators:
            if ind[0]: # Check if standard_id exists
                cursor.execute("""
                    INSERT OR IGNORE INTO tsrs_indicators (standard_id, code, title, description, unit, methodology, data_type, is_mandatory, is_quantitative)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, ind)

        # Get Indicator IDs
        cursor.execute("SELECT id, code FROM tsrs_indicators")
        ind_map = {row[1]: row[0] for row in cursor.fetchall()}

        # 3. Seed TSRS-ESRS Mappings
        mappings = [
            (ind_map.get('TSRS-1-1'), 'ESRS 2 GOV-1', 'Direct', 'Yönetim kurulu rolü ile tam uyumlu'),
            (ind_map.get('TSRS-1-2'), 'ESRS 2 GOV-2', 'Direct', 'Yönetim rolü ile tam uyumlu'),
            (ind_map.get('TSRS-2-1'), 'ESRS E1-6', 'Direct', 'Kapsam 1 emisyonları'),
            (ind_map.get('TSRS-2-2'), 'ESRS E1-6', 'Direct', 'Kapsam 2 emisyonları'),
            (ind_map.get('TSRS-2-3'), 'ESRS E1-6', 'Direct', 'Kapsam 3 emisyonları'),
            (ind_map.get('TSRS-2-4'), 'ESRS E1-9', 'Related', 'Fiziksel risklerin finansal etkileri'),
            (ind_map.get('TSRS-2-5'), 'ESRS E1-9', 'Related', 'İklim fırsatlarının finansal etkileri')
        ]

        print("Seeding TSRS-ESRS Mappings...")
        # Clear existing mappings to avoid duplication if running multiple times
        cursor.execute("DELETE FROM map_tsrs_esrs")
        
        for mapping in mappings:
            if mapping[0]: # Check if indicator_id exists
                cursor.execute("""
                    INSERT INTO map_tsrs_esrs (tsrs_indicator_id, esrs_code, relationship_type, description)
                    VALUES (?, ?, ?, ?)
                """, mapping)

        conn.commit()
        print("Seeding completed successfully.")

    except Exception as e:
        print(f"Error during seeding: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    seed_data()
