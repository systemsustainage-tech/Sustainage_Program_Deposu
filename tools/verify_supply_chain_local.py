
import sys
import os
import json
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.modules.supply_chain.supply_chain_manager import SupplyChainManager
from config.database import DB_PATH

def test_supply_chain_recommendations():
    print("Testing Supply Chain Manager Recommendations...")
    
    manager = SupplyChainManager(DB_PATH)
    company_id = 999  # Test Company
    
    # 1. Add Supplier
    try:
        supplier_id = manager.add_supplier(company_id, "Test Supplier A", "Manufacturing", "Turkey", "test@supplier.com")
        print(f"Added Supplier ID: {supplier_id}")
    except Exception as e:
        print(f"Error adding supplier: {e}")
        return

    # 2. Add Assessment (Low Score)
    details = {'env_score': 30, 'social_score': 30, 'gov_score': 30, 'notes': 'Test Note'}
    try:
        manager.add_assessment(
            supplier_id, 
            company_id, 
            "2023-10-27", 
            30.0, 
            "High", 
            details,
            30, 30, 30
        )
        print("Added Low Score Assessment")
    except Exception as e:
        print(f"Error adding assessment: {e}")
        return

    # 3. Add High Score Assessment (New Supplier to avoid average dragging down)
    try:
        supplier_id_high = manager.add_supplier(company_id, "Test Supplier B", "Tech", "USA", "tech@supplier.com")
        manager.add_assessment(
            supplier_id_high, 
            company_id, 
            "2023-10-28", 
            95.0, 
            "Low", 
            details,
            95, 95, 95
        )
        print("Added High Score Assessment to new supplier")
        
        # DEBUG: Check risk score
        s = manager.get_supplier(supplier_id_high, company_id)
        print(f"DEBUG: Supplier Risk Score: {s.get('risk_score')}")
        
    except Exception as e:
        print(f"Error adding high score assessment: {e}")
        return

    # 4. Check Recommendations
    recs_low = manager.get_recommendations(supplier_id, company_id)
    print("\nRecommendations for Low Score (30):")
    for r in recs_low:
        print(f"- {r}")
    
    if any("kritik seviyenin altında" in r for r in recs_low):
        print("SUCCESS: Found expected recommendation for low score.")
    else:
        print("FAILURE: Did not find expected recommendation for low score.")

    recs_high = manager.get_recommendations(supplier_id_high, company_id)
    print("\nRecommendations for High Score (95):")
    for r in recs_high:
        print(f"- {r}")
        
    if any("Stratejik tedarikçi" in r for r in recs_high):
        print("SUCCESS: Found expected recommendation for high score.")
    else:
        print("FAILURE: Did not find expected recommendation for high score.")

    # Clean up (Optional, but good practice for test scripts)
    # conn = manager.get_connection()
    # conn.execute("DELETE FROM supplier_profiles WHERE id = ?", (supplier_id,))
    # conn.execute("DELETE FROM supplier_assessments WHERE supplier_id = ?", (supplier_id,))
    # conn.commit()
    # conn.close()
    # print("\nCleaned up test data.")

if __name__ == "__main__":
    test_supply_chain_recommendations()
