
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.modules.gri.gri_manager import GRIManager

def verify_gri():
    print("Initializing GRIManager...")
    # Initialize without company_id to avoid context issues during init
    manager = GRIManager()
    
    print("Checking gri_standards count...")
    standards = manager.execute_query("SELECT COUNT(*) as count FROM gri_standards")
    print(f"Standards count: {standards[0]['count']}")
    
    print("Checking gri_indicators count...")
    indicators = manager.execute_query("SELECT COUNT(*) as count FROM gri_indicators")
    print(f"Indicators count: {indicators[0]['count']}")
    
    if standards[0]['count'] == 0:
        print("Attempting to populate standards manually...")
        manager.populate_gri_standards()
        
        standards_after = manager.execute_query("SELECT COUNT(*) as count FROM gri_standards")
        print(f"Standards count after population: {standards_after[0]['count']}")
        
        indicators_after = manager.execute_query("SELECT COUNT(*) as count FROM gri_indicators")
        print(f"Indicators count after population: {indicators_after[0]['count']}")

if __name__ == "__main__":
    verify_gri()
