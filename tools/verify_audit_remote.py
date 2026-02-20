import sys
import os
sys.path.append('/var/www/sustainage')
from backend.core.audit_manager import AuditManager

def verify():
    print("Verifying AuditManager on remote...")
    try:
        manager = AuditManager()
        
        # 1. Log action
        print("Logging test action...")
        test_company_id = 1
        manager.log_action(
            user_id=1,
            action="TEST_AUDIT_VERIFY",
            resource="system",
            resource_id=999,
            details="Remote verification test",
            ip_address="127.0.0.1",
            company_id=test_company_id
        )
        
        # 2. Retrieve logs
        print("Retrieving logs...")
        logs = manager.get_logs(limit=10, company_id=test_company_id)
        
        found = False
        for log in logs:
            # log is sqlite3.Row
            if log['action'] == "TEST_AUDIT_VERIFY" and log['company_id'] == test_company_id:
                print(f"Found log: {log['id']} - {log['action']} - {log['details']}")
                found = True
                break
        
        if found:
            print("SUCCESS: Audit log created and retrieved with company_id.")
        else:
            print("FAILURE: Could not find the test log.")
            sys.exit(1)
            
        # 3. Verify count
        print("Verifying count...")
        count = manager.get_logs_count(company_id=test_company_id)
        print(f"Total logs for company {test_company_id}: {count}")
        if count > 0:
            print("SUCCESS: Count retrieved.")
        else:
            print("WARNING: Count is 0 (should be at least 1)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    verify()
