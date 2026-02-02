import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'sustainage.db')

def check_indexes():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Checking database indexes...")
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    missing_indexes = []

    for table in tables:
        table_name = table[0]
        if table_name.startswith('sqlite_'):
            continue
            
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = cursor.fetchall()
        
        # Get existing indexes
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        
        existing_index_columns = set()
        for idx in indexes:
            idx_name = idx[1]
            cursor.execute(f"PRAGMA index_info({idx_name})")
            cols = cursor.fetchall()
            # We only care about the first column for simple FK lookup optimization
            if cols:
                existing_index_columns.add(cols[0][2]) # column name

        for fk in fks:
            from_col = fk[3]
            # to_table = fk[2]
            
            if from_col not in existing_index_columns:
                # Check if it's a primary key (implicitly indexed)
                cursor.execute(f"PRAGMA table_info({table_name})")
                cols_info = cursor.fetchall()
                is_pk = False
                for col in cols_info:
                    if col[1] == from_col and col[5] == 1: # pk flag
                        is_pk = True
                        break
                
                if not is_pk:
                    missing_indexes.append((table_name, from_col))

    conn.close()

    if missing_indexes:
        print(f"\nFound {len(missing_indexes)} potential missing indexes on Foreign Keys:")
        for table, col in missing_indexes:
            print(f"  - Table: {table}, Column: {col}")
            # Generate CREATE INDEX statement suggestion
            print(f"    Suggest: CREATE INDEX idx_{table}_{col} ON {table}({col});")
    else:
        print("\n✅ All Foreign Keys appear to be indexed.")

if __name__ == "__main__":
    check_indexes()
