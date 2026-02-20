import os
import sys
import inspect
import importlib.util

sys.path.insert(0, r"C:\SUSTAINAGESERVER")

try:
    from backend.core.base_manager import BaseTenantManager
except ImportError:
    print("Could not import BaseTenantManager")
    sys.exit(1)

def check_init_compliance():
    backend_dir = r"C:\SUSTAINAGESERVER\backend"
    print(f"Scanning {backend_dir}...")
    
    issues = []
    
    for root, _, files in os.walk(backend_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                file_path = os.path.join(root, file)
                module_name = os.path.relpath(file_path, r"C:\SUSTAINAGESERVER").replace(os.sep, ".").replace(".py", "")
                
                if "legacy" in module_name:
                    continue

                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if issubclass(obj, BaseTenantManager) and obj is not BaseTenantManager:
                                init_spec = inspect.getfullargspec(obj.__init__)
                                if 'company_id' not in init_spec.args:
                                    issues.append(f"{obj.__name__} in {file_path}")
                                    
                except Exception:
                    pass

    print("\n--- Managers missing company_id in __init__ ---")
    for issue in issues:
        print(issue)

if __name__ == "__main__":
    check_init_compliance()
