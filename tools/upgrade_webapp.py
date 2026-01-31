import os
import sys

WEB_APP_PATH = r'c:\SUSTAINAGESERVER\web_app.py'

APPEND_CODE = """
# ==========================================
# DYNAMIC MODULE INTEGRATION (AUTO-GENERATED)
# ==========================================
try:
    from backend.core.universal_manager import UniversalManagerWrapper
except ImportError:
    try:
        from core.universal_manager import UniversalManagerWrapper
    except ImportError:
        logging.error("Could not import UniversalManagerWrapper")
        UniversalManagerWrapper = None

import importlib.util
import inspect

def _auto_load_managers():
    \"\"\"
    Dynamically finds and loads Manager classes from backend/modules
    and adds them to the global MANAGERS dictionary.
    \"\"\"
    global MANAGERS
    modules_dir = os.path.join(BACKEND_DIR, 'modules')
    
    # Map of specific module names to Manager classes (overrides)
    # or heuristics
    
    for root, dirs, files in os.walk(modules_dir):
        for file in files:
            if file.endswith('_manager.py') or file.endswith('Manager.py') or 'manager' in file.lower():
                if file.startswith('__'): continue
                
                full_path = os.path.join(root, file)
                module_name_guess = os.path.splitext(file)[0]
                
                # Try to import
                try:
                    spec = importlib.util.spec_from_file_location(module_name_guess, full_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    
                    # Find Manager class
                    for name, obj in inspect.getmembers(mod):
                        if inspect.isclass(obj) and 'Manager' in name and name != 'Manager':
                            # Found a manager class
                            # Determine key for MANAGERS dict
                            # e.g. WasteManager -> waste
                            key = name.lower().replace('manager', '').replace('enhanced', '')
                            if key not in MANAGERS or MANAGERS[key] is None:
                                try:
                                    instance = obj(DB_PATH)
                                    MANAGERS[key] = instance
                                    logging.info(f"Auto-loaded {name} as {key}")
                                except Exception as e:
                                    # Maybe it doesn't take DB_PATH or other init args
                                    try:
                                        instance = obj()
                                        MANAGERS[key] = instance
                                        logging.info(f"Auto-loaded {name} as {key} (no args)")
                                    except Exception as e2:
                                        pass
                except Exception as e:
                    logging.warning(f"Failed to auto-load {file}: {e}")

# Run auto-loader
_auto_load_managers()

# List of templates that were "under construction" and now need routes
UNDER_CONSTRUCTION_MODULES = [
    'advanced_calculation', 'advanced_inventory', 'advanced_reporting', 'ai', 'ai_reports', 
    'analysis', 'analytics', 'auditor', 'automated_reporting', 'automation', 'auto_tasks', 
    'company', 'company_info', 'database', 'data_collection', 'data_import', 'data_inventory', 
    'data_provenance', 'digital_security', 'document_processing', 'emergency', 'emission_reduction', 
    'environmental', 'erp_integration', 'eu_taxonomy', 'file_manager', 'forms', 'framework_mapping', 
    'ifrs', 'innovation', 'integration', 'mapping', 'policy_library', 'prioritization', 
    'product_technology', 'quality', 'reporting', 'scenario_analysis', 'scope3', 'security', 
    'skdm', 'stakeholder', 'standards', 'strategic', 'surveys', 'tracking', 'tsrs', 'ungc', 
    'user_experience', 'validation', 'visualization', 'waste_management', 'water_management', 'workflow'
]

def register_dynamic_routes():
    \"\"\"
    Registers routes for the modules that were previously under construction.
    Uses UniversalManagerWrapper to provide data.
    \"\"\"
    
    def create_view_func(template_name, route_key):
        def view_func():
            if 'user' not in session:
                return redirect(url_for('login'))
            
            # Try to find a manager
            # 1. Exact match
            manager = MANAGERS.get(route_key)
            
            # 2. Fuzzy match
            if not manager:
                for k, v in MANAGERS.items():
                    if k in route_key or route_key in k:
                        manager = v
                        break
            
            data = {}
            if manager and UniversalManagerWrapper:
                wrapper = UniversalManagerWrapper(manager)
                data = wrapper.get_dashboard_data()
            
            # Add some context even if no manager found
            if not data:
                data = {'stats': {}, 'records': []}
                
            return render_template(f'{template_name}.html', **data)
        return view_func

    for mod in UNDER_CONSTRUCTION_MODULES:
        route_path = f'/{mod}'
        endpoint = mod
        
        # Check if route already exists
        exists = False
        for rule in app.url_map.iter_rules():
            if rule.rule == route_path:
                exists = True
                break
        
        if not exists:
            # Map module name to manager key
            # e.g. waste_management -> waste
            manager_key = mod.replace('_management', '').replace('_manager', '')
            
            app.add_url_rule(
                route_path, 
                endpoint=endpoint, 
                view_func=create_view_func(mod, manager_key)
            )
            logging.info(f"Registered dynamic route: {route_path}")

register_dynamic_routes()
# ==========================================
"""

def upgrade_webapp():
    with open(WEB_APP_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "DYNAMIC MODULE INTEGRATION" in content:
        print("Web app already upgraded.")
        return

    with open(WEB_APP_PATH, 'a', encoding='utf-8') as f:
        f.write("\n" + APPEND_CODE)
    
    print("Web app upgraded successfully.")

if __name__ == '__main__':
    upgrade_webapp()
