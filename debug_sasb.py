
import sys
import os
import inspect

# Add project root
sys.path.append(os.getcwd())
# Add backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("Importing SASBManager...")
try:
    import backend.modules.sasb.sasb_manager as sm
    print(f"SASBManager loaded from: {sm.__file__}")
    
    from backend.core.base_manager import BaseTenantManager as BTM_backend
    
    print(f"BTM_backend: {BTM_backend}")
    print(f"SASBManager base: {sm.SASBManager.__bases__[0]}")
    
    print(f"Is subclass? {issubclass(sm.SASBManager, BTM_backend)}")
    
except ImportError as e:
    print(f"Failed to load SASBManager: {e}")
except Exception as e:
    print(f"Error checking SASBManager: {e}")
