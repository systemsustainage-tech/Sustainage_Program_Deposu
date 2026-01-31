import sys
import os
import json
import sqlite3

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

print(f"Backend path added to HEAD: {backend_path}")
print(f"Sys path: {sys.path}")

try:
    import modules
    print(f"Modules package found: {modules.__file__}")
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

try:
    from modules.esg.esg_manager import ESGManager
    print("ESGManager imported successfully.")
except ImportError as e:
    print(f"Error importing ESGManager: {e}")
    # Fallback to direct file loading? No, let's fix the path.
    sys.exit(1)

try:
    from config.database import DB_PATH
    print("DB_PATH imported successfully.")
except ImportError as e:
    print(f"Error importing DB_PATH: {e}")
    # Fallback DB path
    DB_PATH = os.path.join(backend_path, 'data', 'sdg_desktop.sqlite')

def test_esg_scoring():
    print("Testing ESG Score Manager...")
    
    # 1. Initialize
    print("\n[1] Initializing ESGManager...")
    manager = ESGManager(backend_path)
    print("ESGManager initialized.")

    # 2. Test Weight Update
    print("\n[2] Testing Weight Update...")
    new_weights = {'E': 0.5, 'S': 0.3, 'G': 0.2}
    success = manager.update_weights(new_weights)
    if success:
        print(f"PASS: Weights updated to {new_weights}")
        # Verify persistence
        config_path = os.path.join(backend_path, 'config', 'esg_config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                saved_config = json.load(f)
                if saved_config['weights'] == new_weights:
                    print("PASS: Config file verified.")
                else:
                    print(f"FAIL: Config file content mismatch: {saved_config['weights']}")
        else:
            print("FAIL: Config file not created.")
    else:
        print("FAIL: Weight update returned False.")

    # 3. Test Score Calculation and Persistence
    print("\n[3] Testing Score Calculation and Persistence...")
    company_id = 1
    scores = manager.calculate_and_save_score(company_id)
    print(f"Calculated Scores: E={scores['E']}, S={scores['S']}, G={scores['G']}, Overall={scores['overall']}")
    
    # Verify DB insertion
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, overall_score FROM esg_scores WHERE company_id = ? ORDER BY id DESC LIMIT 1", (company_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        print(f"PASS: Score saved to DB. ID: {row[0]}, Overall: {row[1]}")
    else:
        print("FAIL: No score found in DB.")

    # 4. Test History Retrieval
    print("\n[4] Testing History Retrieval...")
    history = manager.get_history(company_id)
    if history:
        print(f"PASS: History retrieved. Count: {len(history)}")
        print(f"Latest entry date: {history[0]['date']}")
    else:
        print("FAIL: History is empty.")

if __name__ == "__main__":
    try:
        test_esg_scoring()
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
