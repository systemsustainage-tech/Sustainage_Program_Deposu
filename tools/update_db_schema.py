import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.getcwd(), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)
    
sys.path.append(os.getcwd())

from backend.modules.supply_chain.supply_chain_manager import SupplyChainManager

print("Initializing Supply Chain Manager to create new tables...")
manager = SupplyChainManager()
print("Tables updated.")
