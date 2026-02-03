import json
import os
from collections import OrderedDict

def remove_duplicates(file_path):
    print(f"Processing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # Read lines to preserve order and manually find duplicates
        lines = f.readlines()
        
    new_lines = []
    seen_keys = set()
    
    # We will reconstruct the file line by line, skipping duplicates
    # But we need to be smart: keep the one that is NOT English if possible
    # Actually, simpler approach: Load full JSON, fix values, dump back.
    # But dumping back ruins formatting.
    # Let's try to edit in place or use the 'add_missing_keys.py' logic but for removal.
    
    # Better approach: Read full content, find duplicate occurrences using regex, remove the unwanted ones.
    # The duplicate keys found were: active, completed, roadmap, targets, in_progress, pending
    
    # Strategy: 
    # 1. Read all lines.
    # 2. Identify line numbers for each key.
    # 3. For the problematic keys, keep the line with Turkish content, remove the one with English content.
    
    import re
    key_pattern = re.compile(r'"([^"]+)"\s*:\s*"([^"]+)"')
    
    keys_to_fix = ['roadmap', 'targets', 'active', 'completed', 'in_progress', 'pending']
    
    # Store (line_index, value) for each key
    key_occurrences = {k: [] for k in keys_to_fix}
    
    for i, line in enumerate(lines):
        match = key_pattern.search(line)
        if match:
            k, v = match.groups()
            if k in keys_to_fix:
                key_occurrences[k].append((i, v))
                
    lines_to_remove = set()
    
    for k in keys_to_fix:
        occs = key_occurrences[k]
        if len(occs) > 1:
            print(f"Fixing duplicate '{k}': {occs}")
            # Determine which to keep. 
            # If one is English (same as key or Capitalized key) and other is Turkish, keep Turkish.
            
            # Simple heuristic:
            # roadmap: "Roadmap" vs "Yol Haritası" -> Keep "Yol Haritası"
            # targets: "Targets" vs "Hedefler" -> Keep "Hedefler"
            # active: "Active" vs "Aktif" -> Keep "Aktif"
            
            # Find the best candidate
            best_idx = -1
            best_val = ""
            
            # Prefer value that is NOT equal to title case of key
            for idx, val in occs:
                if val.lower() != k.lower():
                    best_idx = idx
                    best_val = val
                    break
            
            if best_idx == -1:
                # All look like English or same? Keep the first one.
                best_idx = occs[0][0]
                
            # Mark others for removal
            for idx, val in occs:
                if idx != best_idx:
                    lines_to_remove.add(idx)
                    print(f"  - Removing line {idx+1}: {val}")
                else:
                    print(f"  - Keeping line {idx+1}: {val}")
                    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        for i, line in enumerate(lines):
            if i not in lines_to_remove:
                f.write(line)
                
    print("Done removing duplicates.")

if __name__ == "__main__":
    remove_duplicates("locales/tr.json")
