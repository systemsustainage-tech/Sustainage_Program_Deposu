
import sys
import os

# Add root to path
sys.path.append(os.getcwd())

print("Verifying imports...")

try:
    from backend.modules.supply_chain.supply_chain_manager import SupplyChainManager
    print("✅ SupplyChainManager imported successfully")
except Exception as e:
    print(f"❌ SupplyChainManager import failed: {e}")

try:
    from backend.modules.governance.corporate_governance import CorporateGovernanceManager
    print("✅ CorporateGovernanceManager imported successfully")
except Exception as e:
    print(f"❌ CorporateGovernanceManager import failed: {e}")

try:
    from backend.modules.economic.economic_manager import EconomicManager
    print("✅ EconomicManager imported successfully")
except Exception as e:
    print(f"❌ EconomicManager import failed: {e}")
