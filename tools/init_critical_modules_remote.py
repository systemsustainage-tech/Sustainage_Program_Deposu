import sys
import os
import sqlite3

# Proje ana dizinini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.modules.tnfd.tnfd_manager import TNFDManager
    from backend.modules.advanced_calculation.emission_calculator import EmissionCalculator
    # Import other critical managers here if needed
except ImportError as e:
    print(f"Import Error: {e}")
    # Localde çalışırken backend modülü bulunamayabilir, sunucuda çalışması önemli.
    sys.exit(1)

DB_PATH = '/var/www/sustainage/database/sustainage.db'

def init_modules():
    print(f"Initializing modules with DB: {DB_PATH}")
    
    # DB dizini yoksa oluştur
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        print(f"Creating DB directory: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)
        
    try:
        # TNFD
        print("Initializing TNFD Manager...")
        tnfd = TNFDManager(DB_PATH)
        print("TNFD tables initialized.")
        
        # Emission Calculator (DB kullanmıyor ama test edelim)
        print("Testing Emission Calculator...")
        calc = EmissionCalculator()
        res = calc.calculate_scope1([{'type': 'diesel', 'amount': 100}])
        print(f"Emission test result: {res}")
        
        print("All critical modules initialized successfully.")
        
    except Exception as e:
        print(f"Error initializing modules: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_modules()
