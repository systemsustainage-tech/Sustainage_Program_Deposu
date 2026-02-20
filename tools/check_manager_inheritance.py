import os
import sys
import inspect
import importlib.util
from pathlib import Path
import logging

# Add project root to sys.path
sys.path.insert(0, r"C:\SUSTAINAGESERVER")

# Silence logs from imported modules
logging.basicConfig(level=logging.CRITICAL)

try:
    from backend.core.base_manager import BaseTenantManager
except ImportError as e:
    print(f"CRITICAL: Could not import BaseTenantManager: {e}")
    sys.exit(1)

def get_manager_classes(directory):
    managers = []
    print(f"Scanning directory: {directory}")
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                file_path = os.path.join(root, file)
                module_name = os.path.relpath(file_path, r"C:\SUSTAINAGESERVER").replace(os.sep, ".").replace(".py", "")
                
                # Skip legacy
                if "legacy" in module_name:
                    continue

                # print(f"Checking {module_name}...")
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if name.endswith("Manager") and obj.__module__ == module.__name__:
                                managers.append(obj)
                except Exception as e:
                    # print(f"Skipping {module_name} due to error: {e}")
                    pass
    return managers

def check_inheritance():
    print("Starting inheritance check...")
    backend_dir = r"C:\SUSTAINAGESERVER\backend"
    managers = get_manager_classes(backend_dir)
    
    print(f"Found {len(managers)} manager classes.")
    
    passing = []
    failing = []
    
    exceptions = [
        "LanguageManager", "DatabaseManager", "BaseTenantManager", "DBManager",
        "LicenseManager", "ThemeManager", "IconManager", "CacheManager",
        "LogManager", "ConfigManager", "PromptManager", "SystemMonitor",
        "ProcessManager", "MaintenanceManager", "AdvancedFileManager",
        "NotificationManager", "BackupRecoveryManager", "CloudStorageManager",
        "APIManager", "CaptchaManager", "AuditManager", "RoleManager",
        "GenericDataManager"
    ]

    for mgr in managers:
        if mgr.__name__ in exceptions:
            # print(f"[SKIP] {mgr.__name__}")
            continue
            
        if issubclass(mgr, BaseTenantManager):
            passing.append(mgr.__name__)
        else:
            failing.append(f"{mgr.__name__} (in {mgr.__module__}) - MRO: {[c.__name__ for c in mgr.__mro__]}")

    print("\n--- PASSING (Inherits BaseTenantManager) ---")
    for m in passing:
        print(f"[OK] {m}")

    print("\n--- FAILING (Does NOT Inherit BaseTenantManager) ---")
    for m in failing:
        print(f"[FAIL] {m}")

if __name__ == "__main__":
    check_inheritance()
