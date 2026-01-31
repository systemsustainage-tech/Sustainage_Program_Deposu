
import sys
import os
import sqlite3
import logging

# Configure logging to stdout to avoid stderr noise
logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)

# Set up paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

print(f"Current Working Directory: {os.getcwd()}")
print(f"Script Path: {os.path.abspath(__file__)}")

print("-" * 50)
print("Attempting to import web_app...")
try:
    from web_app import app, DB_PATH, surveys_module
    print("SUCCESS: web_app imported.")
except Exception as e:
    print(f"FAIL: Could not import web_app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("-" * 50)
print("Attempting to test surveys_module route logic...")
try:
    with app.test_request_context('/surveys'):
        # Mock session
        from flask import session
        session['user'] = {'id': 1, 'name': 'Test User', 'role': 'admin'}
        session['company_id'] = 1
        
        # Call the view function
        print("Calling surveys_module()...")
        response = surveys_module()
        
        # Check if response is a string (rendered html)
        if isinstance(response, str):
            print(f"SUCCESS: surveys_module returned rendered HTML (length: {len(response)})")
        else:
            print(f"SUCCESS: surveys_module returned response type: {type(response)}")

    # Test survey_detail (Manage)
    print("\nTesting survey_detail(1)...")
    with app.test_request_context('/surveys/1'):
        session['user'] = {'id': 1, 'name': 'Test User', 'role': 'admin'}
        session['company_id'] = 1
        
        # Ensure a survey exists for testing
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Create dummy survey if not exists
        cursor.execute("INSERT OR IGNORE INTO online_surveys (id, company_id, survey_title, survey_link, is_active) VALUES (1, 1, 'Test Survey', '/survey/test-token', 1)")
        conn.commit()
        conn.close()
        
        from web_app import survey_detail
        response = survey_detail(1)
        if isinstance(response, str):
            print(f"SUCCESS: survey_detail(1) returned rendered HTML (length: {len(response)})")
        else:
            print(f"SUCCESS: survey_detail(1) returned response type: {type(response)}")

    # Test public_survey (View)
    print("\nTesting public_survey('test-token')...")
    with app.test_request_context('/survey/test-token'):
        from web_app import public_survey
        response = public_survey('test-token')
        if isinstance(response, str):
            print(f"SUCCESS: public_survey('test-token') returned rendered HTML (length: {len(response)})")
        else:
            print(f"SUCCESS: public_survey('test-token') returned response type: {type(response)}")
            
except Exception as e:
    print(f"FAIL: Route execution error: {e}")
    import traceback
    traceback.print_exc()

print("-" * 50)
print("DIAGNOSTICS COMPLETE.")
