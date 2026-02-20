import json
import sys
from collections import Counter

def check_duplicates(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Load as string first to find duplicates, but JSON standard doesn't allow duplicate keys.
            # Python's json.load will take the last one.
            # To find duplicates, we need to parse manually or use object_pairs_hook.
            
            def find_dupes(ordered_pairs):
                keys = [k for k, v in ordered_pairs]
                counts = Counter(keys)
                dupes = [k for k, c in counts.items() if c > 1]
                if dupes:
                    print(f"❌ Duplicate keys found in {file_path}: {dupes}")
                    return dict(ordered_pairs)
                else:
                    print(f"✅ No duplicate keys found in {file_path}")
                    return dict(ordered_pairs)

            json.load(f, object_pairs_hook=find_dupes)
            
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    check_duplicates("c:/SUSTAINAGESERVER/locales/tr.json")
