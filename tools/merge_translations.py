import json
import os

CONFIG_TR = r'c:\SUSTAINAGESERVER\backend\config\translations_tr.json'
BACKEND_TR = r'c:\SUSTAINAGESERVER\backend\locales\tr.json'
ROOT_TR = r'c:\SUSTAINAGESERVER\locales\tr.json'

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved {path}")

def merge_dicts(target, source):
    for key, value in source.items():
        if isinstance(value, dict) and key in target and isinstance(target[key], dict):
            merge_dicts(target[key], value)
        else:
            # Source overwrites target if it exists, or adds if missing
            # But wait, we want to keep existing keys in target if they are valid
            # Actually, config/translations_tr.json seems to have the missing keys
            if key not in target:
                target[key] = value
            # If both have it, which one to trust? 
            # User said "login ekranından itibaren bütün sayfaların butonları bu şekilde" implies the current ones are BROKEN (showing keys).
            # So we should prioritize the one that has VALUES.
            # If target has "dashboard_welcome", keep it. If not, take from source.
            pass
    return target

def main():
    print("Loading translations...")
    config_data = load_json(CONFIG_TR)
    backend_data = load_json(BACKEND_TR)
    root_data = load_json(ROOT_TR)

    print(f"Config keys: {len(config_data)}")
    print(f"Backend keys: {len(backend_data)}")
    print(f"Root keys: {len(root_data)}")

    # Merge config into backend
    # We want to ensure all keys in config_data are present in backend_data
    # Use a recursive update that prioritizes existing values if they are not keys?
    # Actually, simpler: just update backend with config, but be careful not to overwrite valid stuff with less valid stuff.
    # But since backend is MISSING keys, adding config is safe.
    
    # Let's do a deep merge
    def deep_update(d, u):
        if not isinstance(d, dict):
            return u
        for k, v in u.items():
            if isinstance(v, dict):
                current_val = d.get(k, {})
                if not isinstance(current_val, dict):
                    # Conflict: current is str, new is dict. Overwrite with merged dict (if possible) or just v
                    current_val = {}
                d[k] = deep_update(current_val, v)
            else:
                if k not in d:
                    d[k] = v
        return d

    print("Merging config into backend...")
    backend_data = deep_update(backend_data, config_data)
    
    print("Merging config into root...")
    root_data = deep_update(root_data, config_data)
    
    # Also ensure backend and root are consistent
    print("Syncing backend and root...")
    backend_data = deep_update(backend_data, root_data)
    root_data = deep_update(root_data, backend_data)

    save_json(BACKEND_TR, backend_data)
    save_json(ROOT_TR, root_data)

if __name__ == "__main__":
    main()
