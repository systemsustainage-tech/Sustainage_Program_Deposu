import os
import sys
import inspect
import importlib.util
import glob

BASE_DIR = r'c:\SUSTAINAGESERVER'
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, BACKEND_DIR)

def list_managers():
    modules_dir = os.path.join(BACKEND_DIR, 'modules')
    managers = []
    
    for root, dirs, files in os.walk(modules_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]
                
                # Try to import
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = mod
                    spec.loader.exec_module(mod)
                    
                    for name, obj in inspect.getmembers(mod):
                        if inspect.isclass(obj) and 'Manager' in name:
                            methods = [m[0] for m in inspect.getmembers(obj, predicate=inspect.isfunction) if not m[0].startswith('_')]
                            managers.append({
                                'file': file,
                                'class': name,
                                'methods': methods,
                                'path': file_path
                            })
                except Exception as e:
                    print(f"Could not inspect {file}: {e}")

    return managers

if __name__ == "__main__":
    results = list_managers()
    print(f"Found {len(results)} managers.")
    for m in results:
        print(f"File: {m['file']} | Class: {m['class']}")
        print(f"  Methods: {m['methods']}")
        print("-" * 40)
