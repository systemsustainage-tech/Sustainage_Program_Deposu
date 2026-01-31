import sqlite3
import sys
import os

# Add backend to path
sys.path.insert(0, r"c:\SUSTAINAGESERVER\backend")

from modules.sdg.sdg_manager import SDGManager

db_path = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sdg_targets LIMIT 1")
    target_id = cursor.fetchone()[0]
    conn.close()
    print(f"Testing with target_id: {target_id}")

    manager = SDGManager(db_path)
    indicators = manager.get_target_indicators(target_id)
    print(f"Successfully retrieved {len(indicators)} indicators.")
    for ind in indicators:
        print(f" - {ind['code']}: {ind['frequency']} (Unit: {ind['unit']})")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
