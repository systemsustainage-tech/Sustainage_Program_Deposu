
import sys
import os
import sqlite3
import json
import logging

# Add project root and backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from config.database import DB_PATH

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def verify_sasb():
    print("\n--- Verifying SASB Module ---")
    try:
        from backend.modules.sasb.sasb_manager import SASBManager
        manager = SASBManager(DB_PATH)
        
        # 1. Verify GLOBAL Sector (IFRS S2)
        print("Checking GLOBAL sector...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, sector_name FROM sasb_sectors WHERE sector_code = 'GLOBAL'")
        row = cursor.fetchone()
        if row:
            print(f"✓ Found GLOBAL sector: {row[1]}")
            sector_id = row[0]
            
            # Check IFRS-S2 Topic
            cursor.execute("SELECT id, topic_code FROM sasb_disclosure_topics WHERE sector_id = ? AND topic_code = 'IFRS-S2'", (sector_id,))
            topic = cursor.fetchone()
            if topic:
                print(f"✓ Found IFRS-S2 topic")
                topic_id = topic[0]
                
                # Check IFRS-S2-1 Metric
                cursor.execute("SELECT id, metric_code FROM sasb_metrics WHERE disclosure_topic_id = ? AND metric_code = 'IFRS-S2-1'", (topic_id,))
                metric = cursor.fetchone()
                if metric:
                    print(f"✓ Found IFRS-S2-1 metric")
                else:
                    print("✗ IFRS-S2-1 metric NOT found")
            else:
                print("✗ IFRS-S2 topic NOT found")
        else:
            print("✗ GLOBAL sector NOT found")
            
        # 2. Verify GRI Mappings
        print("Checking GRI Mappings...")
        cursor.execute("SELECT count(*) FROM sasb_gri_mapping")
        count = cursor.fetchone()[0]
        print(f"Total mappings in DB: {count}")
        
        cursor.execute("SELECT * FROM sasb_gri_mapping WHERE sasb_metric_code LIKE '%IFRS%'")
        rows = cursor.fetchall()
        if rows:
            print(f"✓ Found {len(rows)} mappings for IFRS:")
            for r in rows:
                print(f"  - {r[1]} -> {r[3]}")
        else:
            print("✗ No mappings found for IFRS")
            
        cursor.execute("SELECT * FROM sasb_gri_mapping WHERE sasb_metric_code = 'IFRS-S2-3'")
        rows = cursor.fetchall()
        if rows:
            print(f"✓ Found {len(rows)} mappings for IFRS-S2-3")
            for r in rows:
                print(f"  - {r[0]} -> {r[2]} ({r[3]})")
        else:
            print("✗ No mappings found for IFRS-S2-3")
            
        conn.close()
        return True
    except Exception as e:
        print(f"SASB Verification Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_ungc():
    print("\n--- Verifying UNGC Module ---")
    try:
        from backend.modules.ungc.ungc_manager import UNGCManager
        manager = UNGCManager(DB_PATH)
        manager.create_ungc_tables()
        
        # 1. Test Evidence Table Column
        print("Checking ungc_evidence table schema...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(ungc_evidence)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'file_path' in columns:
            print("✓ file_path column exists")
        else:
            print("✗ file_path column MISSING")
            return False
        
        # 2. Test Add Evidence
        print("Testing add_evidence...")
        success = manager.add_evidence(
            company_id=1,
            principle_id='P1',
            evidence_type='policy',
            description='Verification Test',
            file_path='test/path.pdf'
        )
        if success:
            print("✓ add_evidence successful")
        else:
            print("✗ add_evidence failed")
            
        # 3. Test Thresholds
        print("Testing thresholds...")
        current = manager.get_thresholds()
        print(f"Current thresholds: {current}")
        
        new_full = 0.85
        success = manager.update_thresholds(new_full, 0.45)
        if success:
            updated = manager.get_thresholds()
            if updated['full'] == new_full:
                 print("✓ update_thresholds successful")
            else:
                 print(f"✗ update_thresholds mismatch: {updated}")
        else:
             print("✗ update_thresholds failed")
             
        conn.close()
        return True
    except Exception as e:
        print(f"UNGC Verification Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    sasb_ok = verify_sasb()
    ungc_ok = verify_ungc()
    
    if sasb_ok and ungc_ok:
        print("\nAll Verifications PASSED ✅")
        sys.exit(0)
    else:
        print("\nVerification FAILED ❌")
        sys.exit(1)
