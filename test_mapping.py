
import sys
import os
sys.path.insert(0, os.getcwd())
from mapping.sdg_gri_mapping import SDGGRIMapping
try:
    mapper = SDGGRIMapping()
    data = mapper.get_questions_for_goals([1, 2, 13])
    print(f"Found {len(data)} items")
    if data:
        print(f"First item: {data[0]}")
except Exception as e:
    print(f"Error: {e}")
