import sys
import os
import logging

# Setup paths
sys.path.append("/var/www/sustainage")
sys.path.append("/var/www/sustainage/backend")

# Setup logging
logging.basicConfig(level=logging.INFO)

try:
    from modules.water_management.water_manager import WaterManager
    from modules.water_management.water_reporting import WaterReporting
except ImportError as e:
    print(f"Import Error: {e}")
    print("PYTHONPATH:", sys.path)
    sys.exit(1)

def test_reporting():
    print("--- Testing Report Generation (Water Management) ---")
    
    # 1. Setup Data
    try:
        wm = WaterManager()
        # Insert test data
        cid = wm.add_water_consumption(
            company_id=1,
            period="2024",
            consumption_type="industrial",
            water_source="municipal",
            blue_water=100.0,
            green_water=0.0,
            grey_water=20.0,
            total_water=120.0,
            notes="TEST_ENTRY_AUTOMATED"
        )
        if cid:
            print(f"Inserted test data ID: {cid}")
        else:
            print("Failed to insert test data (might be database error)")
            return
            
    except Exception as e:
        print(f"Data insertion failed: {e}")
        return

    # 2. Generate Report
    try:
        wr = WaterReporting()
        report_path = wr.generate_water_footprint_report(
            company_id=1,
            period="2024"
        )
        
        print(f"Report function returned: {report_path}")
        
        if os.path.exists(report_path):
            print(f"SUCCESS: Report file exists at {report_path}")
            # Check file size
            size = os.path.getsize(report_path)
            print(f"File size: {size} bytes")
        else:
            print(f"FAILURE: Report file not found at {report_path}")
            
    except Exception as e:
        print(f"Report generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reporting()
