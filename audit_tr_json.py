
import json
import re

def is_english(text):
    # Simple heuristic: check for common English words
    common_english = {'the', 'is', 'are', 'for', 'to', 'of', 'in', 'on', 'with', 'and', 'or', 'not', 'be', 'this', 'that'}
    words = set(re.findall(r'\b\w+\b', text.lower()))
    if len(words.intersection(common_english)) > 0:
        return True
    return False

def audit():
    with open('locales/tr.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    untranslated = []
    for key, value in data.items():
        if isinstance(value, str):
            if is_english(value):
                untranslated.append((key, value))
    
    print(f"Found {len(untranslated)} potentially untranslated items:")
    for k, v in untranslated:
        print(f"{k}: {v}")

if __name__ == "__main__":
    audit()
