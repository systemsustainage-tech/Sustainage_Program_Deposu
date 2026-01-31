import requests
import sys
import os

# Configuration
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/login"
UNGC_URL = f"{BASE_URL}/ungc"
EVIDENCE_URL = f"{BASE_URL}/ungc/upload_evidence"
THRESHOLDS_URL = f"{BASE_URL}/ungc/update_thresholds"

USERNAME = "admin"
PASSWORD = "password123"  # Replace with valid credentials if different

def verify_ungc():
    session = requests.Session()
    
    # 1. Login (Simulated or bypassed if we can use a direct manager check)
    # Ideally, we should check the backend logic directly to avoid auth issues in script
    # but let's try to use the backend manager directly like verify_sasb_update.py
    
    print("Verifying UNGC Evidence and Thresholds Logic directly via Manager...")
    
    try:
        sys.path.append(os.path.join(os.getcwd()))
        from backend.modules.ungc.ungc_manager import UNGCManager
        from config.database import DB_PATH
        
        manager = UNGCManager(DB_PATH)
        manager.create_ungc_tables()
        
        # Test Company ID
        company_id = 1
        
        # 1. Test Add Evidence
        print("\n[1] Testing Add Evidence...")
        success = manager.add_evidence(
            company_id=company_id,
            principle_id='P1',
            evidence_type='file',
            description='Test Evidence',
            file_path='ungc/test_evidence.pdf'
        )
        
        if success:
            print("✓ Evidence added successfully")
        else:
            print("✗ Failed to add evidence")
            return False
            
        # Verify it exists
        evidence_list = manager.get_evidence(company_id)
        found = False
        for e in evidence_list:
            if e['evidence_description'] == 'Test Evidence' and e['file_path'] == 'ungc/test_evidence.pdf':
                found = True
                break
        
        if found:
            print("✓ Evidence retrieval verified")
        else:
            print("✗ Evidence not found in retrieval list")
            return False
            
        # 2. Test Update Thresholds
        print("\n[2] Testing Update Thresholds...")
        success = manager.update_thresholds(0.75, 0.35)
        
        if success:
            print("✓ Thresholds updated successfully")
        else:
            print("✗ Failed to update thresholds")
            return False
            
        # Verify
        thresholds = manager.get_thresholds()
        if thresholds['full'] == 0.75 and thresholds['partial'] == 0.35:
            print("✓ Thresholds values verified")
        else:
            print(f"✗ Thresholds mismatch: {thresholds}")
            return False
            
        print("\nUNGC Verification Complete: SUCCESS")
        return True
        
    except Exception as e:
        print(f"\nUNGC Verification Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_ungc()
    sys.exit(0 if success else 1)
