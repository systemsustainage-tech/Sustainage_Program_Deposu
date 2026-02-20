
import sys
import os
import inspect

# Add project root
sys.path.append(os.getcwd())
# Add backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.core.base_manager import BaseTenantManager as BTM_backend
    print(f"BTM_backend loaded from: {sys.modules['backend.core.base_manager'].__file__}")
except ImportError as e:
    print(f"Failed to load BTM_backend: {e}")

try:
    from core.base_manager import BaseTenantManager as BTM_core
    print(f"BTM_core loaded from: {sys.modules['core.base_manager'].__file__}")
except ImportError as e:
    print(f"Failed to load BTM_core: {e}")

try:
    import backend.modules.water_management.water_manager as wm
    print(f"WaterManager loaded from: {wm.__file__}")
    print(f"WaterManager bases: {wm.WaterManager.__bases__}")
    
    if 'BTM_backend' in locals():
        print(f"Is subclass of BTM_backend? {issubclass(wm.WaterManager, BTM_backend)}")
    if 'BTM_core' in locals():
        print(f"Is subclass of BTM_core? {issubclass(wm.WaterManager, BTM_core)}")
        
except ImportError as e:
    print(f"Failed to load WaterManager: {e}")
except Exception as e:
    print(f"Error checking WaterManager: {e}")
