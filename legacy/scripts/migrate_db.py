import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DB = os.path.join(BASE_DIR, 'backend', 'data', 'sdg_desktop.sqlite')
SOURCE_SCHEMA_FILE = os.path.join(BASE_DIR, 'source_schema.sql')

def migrate_database():
    if not os.path.exists(TARGET_DB):
        logging.error(f"Target database not found: {TARGET_DB}")
        return

    if not os.path.exists(SOURCE_SCHEMA_FILE):
        logging.error(f"Source schema file not found: {SOURCE_SCHEMA_FILE}")
        return

    logging.info(f"Connecting to database: {TARGET_DB}")
    conn = sqlite3.connect(TARGET_DB)
    cursor = conn.cursor()

    # Get existing tables in target DB
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = {row[0] for row in cursor.fetchall()}
    logging.info(f"Found {len(existing_tables)} existing tables.")

    # Read source schema
    with open(SOURCE_SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_content = f.read()

    # Split schema into table creations
    # This is a simple parser assuming standard SQL dump format "CREATE TABLE table_name ..."
    # We will split by "CREATE TABLE" and try to identify table names
    
    statements = schema_content.split(';')
    
    tables_created = 0
    
    for statement in statements:
        statement = statement.strip()
        if not statement or not statement.upper().startswith("CREATE TABLE"):
            continue
            
        # Extract table name
        try:
            # Assuming format: CREATE TABLE table_name ... or CREATE TABLE "table_name" ...
            parts = statement.split()
            table_name_part = parts[2]
            table_name = table_name_part.replace('"', '').replace('(', '').strip()
            
            if table_name not in existing_tables:
                logging.info(f"Creating missing table: {table_name}")
                try:
                    cursor.execute(statement)
                    tables_created += 1
                except sqlite3.Error as e:
                    logging.error(f"Error creating table {table_name}: {e}")
            else:
                # logging.info(f"Table already exists, skipping: {table_name}")
                pass
                
        except Exception as e:
            logging.error(f"Error parsing statement: {e}")

    conn.commit()
    conn.close()
    logging.info(f"Migration completed. {tables_created} new tables created.")

if __name__ == "__main__":
    migrate_database()
