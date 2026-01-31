import sys
import os

# Add backend to path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend'))
sys.path.insert(0, backend_path)

print(f"Added to path: {backend_path}")

try:
    from modules.gri.gri_schema_upgrade import GRISchemaUpgrade

    if __name__ == "__main__":
        print("Running GRI Schema Upgrade...")
        upgrader = GRISchemaUpgrade()
        try:
            upgrader.create_extension_tables()
            print("GRI Schema Upgrade completed successfully.")
        except Exception as e:
            print(f"Error running GRI Schema Upgrade: {e}")
except ImportError as e:
    print(f"Import Error: {e}")
    # Fallback: try direct file execution approach if modules package is messy
    import sqlite3
    # ... logic to run it manually if needed, but let's hope the path fix works
