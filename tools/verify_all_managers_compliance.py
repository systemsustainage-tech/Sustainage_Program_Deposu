import os
import sys
import importlib.util
import inspect
import glob

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Also add backend to path for legacy imports (if needed, but usually project root is enough if using backend.core)
backend_path = os.path.join(project_root, 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

try:
    from backend.core.base_manager import BaseTenantManager
    # print(f"DEBUG: Loaded BaseTenantManager from backend.core.base_manager")
except ImportError:
    try:
        from core.base_manager import BaseTenantManager
        # print(f"DEBUG: Loaded BaseTenantManager from core.base_manager")
    except ImportError:
        print("❌ CRITICAL: Could not import BaseTenantManager. Check python path.")
        sys.exit(1)

def check_manager_compliance(file_path: str, class_name: str = None) -> bool:
    """
    Checks if a manager class in the file is compliant.
    If class_name is None, tries to find a class ending with 'Manager'.
    """
    try:
        # Load module
        module_name = os.path.basename(file_path).replace('.py', '')
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"⚠️ Could not load module {file_path}: {e}")
            return False
        
        # Find class
        if class_name:
            if not hasattr(module, class_name):
                print(f"❌ Class {class_name} not found in {file_path}")
                return False
            cls = getattr(module, class_name)
        else:
            # Auto-detect class
            classes = [obj for name, obj in inspect.getmembers(module, inspect.isclass) 
                      if name.endswith('Manager') and obj.__module__ == module_name]
            if not classes:
                # print(f"ℹ️ No *Manager class found in {file_path}")
                return True # Skip non-manager files
            cls = classes[0] # Take the first one
            class_name = cls.__name__

        # Check inheritance
        is_compliant = False
        
        # 1. Check strict subclass (identity)
        if issubclass(cls, BaseTenantManager):
            is_compliant = True
        else:
            # 2. Check by name (fallback for import mismatches)
            for base in cls.__bases__:
                if base.__name__ == 'BaseTenantManager':
                    # print(f"⚠️ {class_name} passes by name check (module: {base.__module__})")
                    is_compliant = True
                    break
        
        if not is_compliant:
            print(f"❌ {class_name} does NOT inherit from BaseTenantManager")
            print(f"   Expected: {BaseTenantManager}")
            print(f"   Actual bases: {cls.__bases__}")
            return False
        
        # Check __init__ signature
        sig = inspect.signature(cls.__init__)
        params = sig.parameters
        
        if 'company_id' not in params:
            print(f"❌ {class_name}.__init__ missing 'company_id' parameter")
            return False
        
        # print(f"✅ {class_name} is compliant")
        return True
        
    except Exception as e:
        print(f"⚠️ Error checking {file_path}: {e}")
        return False

def scan_directory(start_dir: str):
    print(f"🔍 Scanning {start_dir} for Managers...")
    failed_count = 0
    passed_count = 0
    
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith('_manager.py'):
                full_path = os.path.join(root, file)
                # Skip legacy
                if 'legacy' in full_path or 'yonetim' in full_path:
                    continue
                    
                if check_manager_compliance(full_path):
                    passed_count += 1
                else:
                    failed_count += 1
                    
    print(f"\n📊 Scan Complete: {passed_count} Passed, {failed_count} Failed")

if __name__ == "__main__":
    scan_directory(os.path.join(project_root, 'backend', 'modules'))
