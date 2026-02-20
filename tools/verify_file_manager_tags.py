
import sys
import os

# Add project root to path
sys.path.append('/var/www/sustainage')

from backend.modules.file_manager.advanced_file_manager import AdvancedFileManager
# from backend.data.database import Database # Not needed if we use manager.db

def test_tag_isolation():
    db_path = '/var/www/sustainage/backend/data/sdg_desktop.sqlite'
    
    # Initialize manager
    manager = AdvancedFileManager(db_path)
    
    tag_name = "IsolationTestTag"
    
    print(f"Testing tag isolation for '{tag_name}'...")
    
    # Clean up previous tests
    manager.db.execute_update("DELETE FROM file_tags WHERE tag_name = ?", (tag_name,))
    
    # Create for Company 1
    id1 = manager._ensure_tag(tag_name, 1)
    print(f"Created tag for Company 1: ID {id1}")
    
    # Create for Company 2
    id2 = manager._ensure_tag(tag_name, 2)
    print(f"Created tag for Company 2: ID {id2}")
    
    if id1 == id2:
        print("FAIL: IDs are identical! Isolation failed.")
        sys.exit(1)
        
    # Verify retrieval
    tags1 = manager.get_all_tags(1)
    ids1 = [t['id'] for t in tags1 if t['name'] == tag_name]
    
    tags2 = manager.get_all_tags(2)
    ids2 = [t['id'] for t in tags2 if t['name'] == tag_name]
    
    print(f"Company 1 tags: {ids1}")
    print(f"Company 2 tags: {ids2}")
    
    if id1 in ids1 and id2 not in ids1 and id2 in ids2 and id1 not in ids2:
        print("SUCCESS: Tags are isolated correctly.")
    else:
        print("FAIL: Retrieval isolation failed.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        test_tag_isolation()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
