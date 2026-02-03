import json
import sys
from collections import Counter

def check_json(file_path):
    print(f"Checking {file_path}...")
    
    # 1. Check for duplicates using raw parsing
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple duplicate finder via key counting
    keys = []
    import re
    # Match "key": pattern
    matches = re.findall(r'"([^"]+)"\s*:', content)
    key_counts = Counter(matches)
    duplicates = [k for k, v in key_counts.items() if v > 1]
    
    if duplicates:
        print(f"FAILED: Found {len(duplicates)} duplicate keys!")
        for k in duplicates:
            print(f"  - {k} (count: {key_counts[k]})")
    else:
        print("PASS: No duplicate keys found.")

    # 2. Check strict JSON syntax
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("PASS: JSON syntax is valid.")
        
        # 3. Check specific keys
        check_keys = ['dashboard', 'roadmap', 'targets', 'help', 'management', 'reports']
        print("\nKey Check:")
        for k in check_keys:
            if k in data:
                print(f"  - '{k}': '{data[k]}'")
            else:
                print(f"  - '{k}': MISSING")
                
    except json.JSONDecodeError as e:
        print(f"FAILED: JSON syntax error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAILED: Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_json("locales/tr.json")
