
import sqlite3
import os

def dump_schema(db_path, output_path):
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            f.write(f"--- Table: {table_name} ---\n")
            
            # Get schema
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            schema = cursor.fetchone()
            if schema and schema[0]:
                f.write(schema[0] + ";\n\n")
            
            # Get columns info for more detail if needed (pragma)
            # cursor.execute(f"PRAGMA table_info({table_name})")
            # columns = cursor.fetchall()
            # for col in columns:
            #     f.write(f"  {col}\n")
            # f.write("\n")

    conn.close()
    print(f"Schema dumped to {output_path}")

if __name__ == "__main__":
    source_db = r"c:\sdg\data\sdg_desktop.sqlite"
    target_db = r"c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite"
    
    dump_schema(source_db, "source_schema.sql")
    dump_schema(target_db, "target_schema.sql")
