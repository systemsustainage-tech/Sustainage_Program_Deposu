import sys
import os
import logging
import sqlite3
from datetime import datetime, timedelta

# Add project root to path
# c:\SUSTAINAGESERVER\backend\modules\regulation\weekly_update.py -> c:\SUSTAINAGESERVER
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from config.database import DB_PATH
except ImportError:
    # Fallback if config import fails (e.g. strict path issues)
    # Try to find config/database.py relative to here
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    sys.path.insert(0, base_dir)
    try:
        from config.database import DB_PATH
    except ImportError:
        logging.error("Could not import DB_PATH from config.database")
        # Hard fallback based on what we found
        DB_PATH = r'c:\SUSTAINAGESERVER\backend\data\sdg_desktop.sqlite'

# Import Managers
try:
    from backend.modules.regulation.regulation_manager import RegulationManager
    from backend.modules.notification.notification_manager import NotificationManager
except ImportError:
    from modules.regulation.regulation_manager import RegulationManager
    from modules.notification.notification_manager import NotificationManager

def get_admin_users():
    """Get list of admin user IDs to notify"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Get users with role_id that corresponds to admin/super_admin
        # Assuming roles table: 1=super_admin, 2=admin etc. 
        # Or just get all users for now if roles are complex
        # Let's try to find users with role 'admin' or 'super_admin' via user_roles if exists
        
        # First check if user_roles exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_roles'")
        if cursor.fetchone():
            cursor.execute("""
                SELECT ur.user_id 
                FROM user_roles ur
                JOIN roles r ON ur.role_id = r.id
                WHERE r.name IN ('admin', 'super_admin')
            """)
            users = [row[0] for row in cursor.fetchall()]
            if users:
                conn.close()
                return users
        
        # Fallback: Just get ID 1 (usually super admin)
        cursor.execute("SELECT id FROM users WHERE id = 1") 
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users if users else [1]
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        return [1]

def run_weekly_update():
    logging.info(f"Starting weekly regulation update check using DB: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        logging.error(f"Database not found at {DB_PATH}")
        return

    rm = RegulationManager(DB_PATH)
    nm = NotificationManager(DB_PATH)
    
    # 1. Simulate Fetching Updates (Mock)
    logging.info("Checking for new regulations (Simulated)...")
    
    # 2. Check Deadlines
    logging.info("Checking compliance deadlines...")
    regulations = rm.get_regulations(status='active')
    
    today = datetime.now().date()
    warning_threshold = today + timedelta(days=90) # Notify for deadlines within 90 days
    
    target_users = get_admin_users()
    logging.info(f"Target users for notifications: {target_users}")
    
    notification_count = 0
    
    for reg in regulations:
        deadline_str = reg.get('compliance_deadline')
        if not deadline_str:
            continue
            
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        except ValueError:
            logging.warning(f"Invalid date format for {reg['code']}: {deadline_str}")
            continue
            
        # Check if deadline is approaching (future but within threshold)
        if today <= deadline <= warning_threshold:
            days_left = (deadline - today).days
            
            title = f"Mevzuat Uyarısı: {reg['code']}"
            message = f"{reg['title']} için uyum tarihi yaklaşıyor ({days_left} gün kaldı: {deadline_str})."
            link = "/regulation"
            
            for user_id in target_users:
                # Create notification
                nm.create_notification(user_id, title, message, type='warning', link=link)
                notification_count += 1
                
            logging.info(f"Queued notification for {reg['code']} ({days_left} days left)")

    logging.info(f"Weekly update completed. {notification_count} notifications created.")

if __name__ == "__main__":
    run_weekly_update()
