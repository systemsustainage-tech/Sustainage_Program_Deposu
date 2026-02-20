print("Start")
import sys, os
sys.path.append(os.getcwd())
try:
    from backend.modules.notification.notification_manager import NotificationManager
    print("Imported")
    mgr = NotificationManager()
    print("Initialized")
except Exception as e:
    print(f"Error: {e}")
